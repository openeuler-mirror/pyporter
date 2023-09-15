#!/usr/bin/python3
"""
This is a packager bot for python modules from pypi.org
"""
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Author: Shinwell_Hu Myeuler
# Create: 2020-05-07
# Description: provide a tool to package python module automatically
# ******************************************************************************/

import argparse
import datetime
import hashlib
import json
import logging
import os
import platform
import subprocess
import sys
import urllib
import urllib.request
from os import path
from pathlib import Path

from retry import retry_call

from pyporter.utils import refine_requires, transform_module_name

logger = logging.getLogger()

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

json_file_template = '{pkg_name}.json'
name_tag_template = 'Name:\t\t{pkg_name}'
summary_tag_template = 'Summary:\t{pkg_sum}'
version_tag_template = 'Version:\t{pkg_ver}'
release_tag_template = 'Release:\t1'
license_tag_template = 'License:\t{pkg_lic}'
home_tag_template = 'URL:\t\t{pkg_home}'
source_tag_template = 'Source0:\t{pkg_source}'

buildreq_tag_template = 'BuildRequires:\t{req}'

# TODO List
# 1. Need a reliable way to get description of module .. Partially done
# 2. requires_dist has some dependency restirction, need to present
# 3. dependency outside python (i.e. pycurl depends on libcurl) doesn't exist in pipy


class PyPorter:
    __url_template = 'https://pypi.org/pypi/{pkg_name}/json'
    __url_template_with_ver = 'https://pypi.org/pypi/{pkg_name}/{pkg_ver}/json'
    __build_noarch = True
    __json = None
    __module_name = ""
    __spec_name = ""
    __pkg_name = ""

    def __init__(self, args):
        mirror = args.mirror
        resp = ""
        self.mirror = mirror if mirror == "" or mirror[
            -1] != '/' else mirror[:-1]
        retry_call(self.do_init, [args.arch, args.pkg, args.pkgversion],
                   tries=args.retry,
                   delay=args.delay)

    def do_init(self, arch, pkg, ver=""):
        """
        receive json from pypi.org
        """
        if not ver:
            ver = "latest"
            url = self.__url_template.format(pkg_name=pkg)
        else:
            url = self.__url_template_with_ver\
                .format(pkg_name=pkg, pkg_ver=ver)

        try:
            with urllib.request.urlopen(url, timeout=30) as u:
                self.__json = json.loads(u.read().decode('utf-8'))
        except urllib.error.HTTPError as err:
            if err.code == 404:
                logger.error(
                    f"The package:{pkg} ver:{ver} does not existed on pypi")
                sys.exit(1)
            else:
                raise
        if self.__json is not None:
            self.__module_name = self.__json["info"]["name"]
            self.__spec_name = "python-" + self.__module_name
            self.__pkg_name = "python3-" + self.__module_name
            self.__build_noarch = self.__get_buildarch()

        if arch:
            self.__build_noarch = False

    def get_spec_name(self):
        return self.__spec_name

    def get_module_name(self):
        return self.__module_name

    def get_archive_name(self):
        s_info = self.get_source_info()
        if s_info:
            # filename is {archive_name}-{version}.{suffix}
            filename = s_info.get("filename")
            if not filename:
                return ""
            filename = (filename[:-len(".tar.gz")]
                        if "tar.gz" in filename else filename[:-len(".zip")])
            v = self.get_version()
            return filename.replace("-" + v, "")
        return ""

    def get_pkg_name(self):
        return self.__pkg_name

    def get_version(self):
        return self.__json["info"]["version"]

    def get_summary(self):
        summary = self.__json["info"]["summary"]
        return summary if summary else "please add a summary manually as the author left a blank one"

    def get_home(self):
        # try to get homepage from project_urls
        # or else try with project_url, home_page, package_url
        try:
            home = self.__json["info"]["project_urls"]["Homepage"]
        except:
            home = (self.__json["info"]["project_url"]
                    or self.__json["info"]["home_page"]
                    or self.__json["info"]["package_url"])
        if home is None:
            logger.error("Cant find home page url")
            sys.exit(1)
        return home

    def get_license(self):
        """
        By default, the license info can be achieved from json["info"]["license"]
        in rare cases it doesn't work.
        We fall back to json["info"]["classifiers"], it looks like License :: OSI Approved :: BSD Clause
        or License :: Public Domain, seems like the license is at the end
        """
        if self.__json["info"]["license"] != "":
            return self.__json["info"]["license"]
        for k in self.__json["info"]["classifiers"]:
            if k.startswith("License"):
                ks = k.split("::")
                return ks[-1].strip()
        return ""

    def get_source_info(self):
        """
        return a map of source filename, md5 of source, source url
        return None in errors
        """
        rs = self.get_releases()
        for r in rs:
            if r["packagetype"] == "sdist":
                return {
                    "filename": r["filename"],
                    "md5": r["md5_digest"],
                    "url": r["url"]
                }
        return None

    def get_releases(self):
        """
        The https://pypi.org/pypi/{pkg}/json API contains both "releases" and "urls" keys
        The version specified https://pypi.org/pypi/{pkg}/{ver}/json API contains only "urls"
        If user specified a version, we need grab release info from "urls"
        """
        v = self.get_version()
        if "releases" in self.__json.keys():
            return self.__json["releases"][v]
        elif "urls" in self.__json.keys():
            return self.__json["urls"]
        else:
            return []

    def get_source_url(self):
        """
        return URL for source file for the latest version
        return "" in errors
        """
        s_info = self.get_source_info()
        if s_info:
            surl = s_info.get("url")
            if self.mirror:
                surl = surl.replace("https://files.pythonhosted.org",
                                    self.mirror)
            return surl
        return ""

    def get_requires(self):
        """
        return all requires no matter if extra is required.
        """
        rs = self.__json["info"]["requires_dist"]
        if rs is None:
            return []
        all_requires = []
        for r in rs:
            idx = r.find(";")
            if idx != -1:
                r = r[:idx]
            all_requires.append(transform_module_name(r))
        return all_requires

    def __get_buildarch(self):
        """
        if this module has a prebuild package for amd64, then it is arch dependent.
        print BuildArch tag if needed.
        """
        rs = self.get_releases()
        for r in rs:
            if r["packagetype"] == "bdist_wheel" and "amd64" in r["url"]:
                return False
        return True

    def is_build_noarch(self):
        return self.__build_noarch

    def get_buildarch(self):
        if (self.__build_noarch == True):
            print("BuildArch:\tnoarch")

    def get_description(self):
        """
        return description.
        Usually it's json["info"]["description"]
        If it's rst style, then only use the content for the first paragraph, and remove all tag line.
        For empty description, use summary instead.
        """
        desc = self.__json["info"]["description"].splitlines()
        res = []
        paragraph = 0
        for d in desc:
            if len(d.strip()) == 0:
                continue
            ignore_line = False
            if d.strip().startswith("===") or d.strip().startswith("---"):
                paragraph = paragraph + 1
                ignore_line = True
            elif d.strip().startswith(":") or d.strip().startswith(".."):
                ignore_line = True
            if ignore_line != True and paragraph == 1:
                res.append(d)
            if paragraph >= 2:
                del res[-1]
                return "\n".join(res)
        if res:
            return "\n".join(res)
        elif paragraph == 0:
            return self.__json["info"]["description"]
        else:
            return self.__json["info"]["summary"]

    def get_build_requires(self):
        req_list = []
        rds = self.__json["info"]["requires_dist"]
        if rds is not None:
            for rp in rds:
                br = refine_requires(rp)
                if br == "":
                    continue
                #
                # Do not output BuildRequires:
                # just collect all build requires and using pip to install
                # than can help to build all rpm withoud trap into
                # build dependency nightmare
                #
                name = str.lstrip(br).split(" ")
                req_list.append(name[0])
        return req_list

    def prepare_build_requires(self):
        print(buildreq_tag_template.format(req='python3-devel'))
        print(buildreq_tag_template.format(req='python3-setuptools'))
        print(buildreq_tag_template.format(req='python3-pip'))
        if not self.__build_noarch:
            print(buildreq_tag_template.format(req='python3-cffi'))
            print(buildreq_tag_template.format(req='gcc'))
            print(buildreq_tag_template.format(req='gdb'))

    def prepare_pkg_build(self):
        print("%pyproject_build")

    def prepare_pkg_install(self):
        print("%pyproject_install")

    def prepare_pkg_files(self):
        if self.__build_noarch:
            print("%{python3_sitelib}/*")
        else:
            print("%{python3_sitearch}/*")

    def store_json(self, spath):
        """
        save json file
        """
        fname = json_file_template.format(pkg_name=self.__pkg_name)
        json_file = os.path.join(spath, fname)

        if path.exists(json_file) and path.isfile(json_file):
            with open(json_file, 'r') as f:
                resp = json.load(f)
        else:
            with open(json_file, 'w') as f:
                json.dump(self.__json, f)


def download_source(porter, tgtpath):
    """
    download source file from url, and save it to target path
    """
    if not os.path.exists(tgtpath):
        print("download path %s does not exist\n", tgtpath)
        return False
    s_info = porter.get_source_info()
    if s_info is None:
        print("analyze source info error")
        return False
    s_url = s_info.get("url")
    s_path = os.path.join(tgtpath, s_info.get("filename"))
    if os.path.exists(s_path):
        with open(s_path, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            _hash = str(md5obj.hexdigest()).lower()
            if s_info.get("md5") == _hash:
                print("same source file exists, skip")
                return True
    return subprocess.call(["wget", s_url, "-P", tgtpath])


def prepare_rpm_build_env(root):
    """
    prepare environment for rpmbuild
    """
    if not os.path.exists(root):
        print(f"Root path {root} does not exist\n")
        return ""

    buildroot = os.path.join(root, "rpmbuild")
    if not os.path.exists(buildroot):
        os.mkdir(buildroot)

    for sdir in ['SPECS', 'BUILD', 'SOURCES', 'SRPMS', 'RPMS', 'BUILDROOT']:
        bpath = os.path.join(buildroot, sdir)
        if not os.path.exists(bpath):
            os.mkdir(bpath)

    return buildroot


def try_pip_install_package(pkg):
    """
    install packages listed in build requires
    """
    pip_name = pkg.split("-")
    if len(pip_name) == 2:
        ret = subprocess.call(["pip3", "install", "--user", pip_name[1]])
    else:
        ret = subprocess.call(["pip3", "install", "--user", pip_name[0]])

    if ret != 0:
        logger.error(
            f"{pip_name} can not be installed correctly, Fix it later, go ahead to do building..."
        )

    return True


def package_installed(pkg):
    print(pkg)
    ret = subprocess.call(["rpm", "-qi", pkg])
    if ret == 0:
        return True

    return False


def build_package(specfile):
    """
    build rpm package with rpmbuild
    """
    ret = subprocess.call(["rpmbuild", "-ba", specfile])
    return ret


def build_install_rpm(porter, rootpath):
    ret = build_rpm(porter, rootpath)
    if ret != "":
        return ret

    arch = "noarch"
    if porter.is_build_noarch():
        arch = "noarch"
    else:
        arch = platform.machine()

    pkgname = os.path.join(rootpath, "rpmbuild", "RPMS", arch,
                           porter.get_pkg_name() + "*")
    ret = subprocess.call(["rpm", "-ivh", pkgname])
    if ret != 0:
        return "Install failed\n"

    return ""


def build_rpm(porter, rootpath):
    """
    full process to build rpm
    """
    buildroot = prepare_rpm_build_env(rootpath)
    if buildroot == "":
        return False

    specfile = os.path.join(buildroot, "SPECS",
                            porter.get_spec_name() + ".spec")

    req_list = build_spec(porter, specfile)

    download_source(porter, os.path.join(buildroot, "SOURCES"))

    build_package(specfile)

    return ""


def build_spec(porter, output):
    """
    print out the spec file
    """
    if os.path.isdir(output):
        output = os.path.join(output, porter.get_spec_name() + ".spec")
    tmp = sys.stdout
    if output != "":
        sys.stdout = open(output, 'w+', encoding='utf-8')

    print("%global _empty_manifest_terminate_build 0")
    print(name_tag_template.format(pkg_name=porter.get_spec_name()))
    print(version_tag_template.format(pkg_ver=porter.get_version()))
    print(release_tag_template)
    print(summary_tag_template.format(pkg_sum=porter.get_summary()))
    print(license_tag_template.format(pkg_lic=porter.get_license()))
    print(home_tag_template.format(pkg_home=porter.get_home()))
    print(source_tag_template.format(pkg_source=porter.get_source_url()))
    porter.get_buildarch()
    print("")
    for r in porter.get_requires():
        print("Requires:\t" + r)
    print("")
    print("%description")
    print(porter.get_description())
    print("")

    print(f"%package -n {porter.get_pkg_name()}")
    print(summary_tag_template.format(pkg_sum=porter.get_summary()))
    print(f"Provides:\t{porter.get_spec_name()}")

    porter.prepare_build_requires()

    build_req_list = porter.get_build_requires()

    print(f"%description -n {porter.get_pkg_name()}")
    print(porter.get_description())
    print("")
    print("%package help")
    print(
        f"Summary:\tDevelopment documents and examples for {porter.get_module_name()}"
    )
    print(f"Provides:\t{porter.get_pkg_name()}-doc")
    print("%description help")
    print(porter.get_description())
    print("")
    print("%prep")
    print(f"%autosetup -n {porter.get_archive_name()}-{porter.get_version()}")
    print("")
    print("%build")
    porter.prepare_pkg_build()
    print("")
    print("%install")
    porter.prepare_pkg_install()
    print("install -d -m755 %{buildroot}/%{_pkgdocdir}")
    print("if [ -d doc ]; then cp -arf doc %{buildroot}/%{_pkgdocdir}; fi")
    print("if [ -d docs ]; then cp -arf docs %{buildroot}/%{_pkgdocdir}; fi")
    print(
        "if [ -d example ]; then cp -arf example %{buildroot}/%{_pkgdocdir}; fi"
    )
    print(
        "if [ -d examples ]; then cp -arf examples %{buildroot}/%{_pkgdocdir}; fi"
    )
    print("pushd %{buildroot}")
    print("touch filelist.lst")
    # # we double quota the path for the case:
    # # whitespace in filename or dirname
    # # see: https://rpm-list.redhat.narkive.com/7WUOZXa6/basic-question-space-in-file-name
    print("if [ -d usr/lib64 ]; then")
    print(
        "\tfind usr/lib64 -type f -printf \"\\\"/%h/%f\\\"\\n\" >> filelist.lst"
    )
    print("fi")
    print("if [ -d usr/bin ]; then")
    print(
        "\tfind usr/bin -type f -printf \"\\\"/%h/%f\\\"\\n\" >> filelist.lst")
    print("fi")
    print("if [ -d usr/sbin ]; then")
    print(
        "\tfind usr/sbin -type f -printf \"\\\"/%h/%f\\\"\\n\" >> filelist.lst"
    )
    print("fi")
    print("touch doclist.lst")
    print("if [ -d usr/share/man ]; then")
    print(
        "\tfind usr/share/man -type f -printf \"\\\"/%h/%f.gz\\\"\\n\" >> doclist.lst"
    )
    print("fi")
    print("popd")
    print("mv %{buildroot}/filelist.lst .")
    print("mv %{buildroot}/doclist.lst .")
    print("")
    print(f"%files -n {porter.get_pkg_name()} -f filelist.lst")

    porter.prepare_pkg_files()

    print("")
    print("%files help -f doclist.lst")
    print("%{_docdir}/*")
    print("")
    print("%changelog")
    date_str = datetime.date.today().strftime("%a %b %d %Y")
    print(
        f"* {date_str} Python_Bot <Python_Bot@openeuler.org> - {porter.get_version()}-1"
    )
    print("- Package Spec generated")

    sys.stdout = tmp

    return build_req_list


def do_args(dft_root_path):
    parser = argparse.ArgumentParser()

    parser.add_argument("-v",
                        "--pkgversion",
                        help="Specify the pypi package version",
                        type=str,
                        default="")
    parser.add_argument(
        "--retry",
        help="Specify the retry times when fetching metadata(default=3)",
        type=int,
        default=3)
    parser.add_argument(
        "--delay",
        help="Specify the delay time between two retries(default 2s)",
        type=int,
        default=2)
    parser.add_argument(
        "-m",
        "--mirror",
        help="Specify pypi mirror, should be a url which contain"
        " pypi packages",
        type=str,
        default="")
    parser.add_argument("-s",
                        "--spec",
                        help="Create spec file",
                        action="store_true")
    parser.add_argument("-R",
                        "--requires",
                        help="Get required python modules",
                        action="store_true")
    parser.add_argument("-b",
                        "--build",
                        help="Build rpm package",
                        action="store_true")
    parser.add_argument("-B",
                        "--buildinstall",
                        help="Build&Install rpm package",
                        action="store_true")
    parser.add_argument("-r",
                        "--rootpath",
                        help="Build rpm package in root path",
                        type=str,
                        default=dft_root_path)
    parser.add_argument("-d",
                        "--download",
                        help="Download source file indicated path",
                        action="store_true")
    parser.add_argument("-p",
                        "--path",
                        help="indicated path to store files",
                        type=str,
                        default=os.getcwd())
    parser.add_argument("-j",
                        "--json",
                        help="Get Package JSON info",
                        action="store_true")
    parser.add_argument("-o",
                        "--output",
                        help="Output to file",
                        type=str,
                        default="")
    parser.add_argument("-t",
                        "--type",
                        help="Build module type : python, perl...",
                        type=str,
                        default="python")
    parser.add_argument("-a",
                        "--arch",
                        help="Build module with arch",
                        action="store_true")
    parser.add_argument("pkg", type=str, help="The Python Module Name")

    return parser


def porter_creator(args):
    if args.type == "python":
        return PyPorter(args)

    logger.error(f"Type {args.type} is not supported now")
    sys.exit(1)


def main():
    dft_root_path = os.path.join(str(Path.home()))

    parser = do_args(dft_root_path)
    args = parser.parse_args()
    porter = porter_creator(args)

    if args.requires:
        req_list = porter.get_build_requires()
        if req_list is not None:
            print('\n'.join(req_list))
    elif args.spec:
        build_spec(porter, args.output)
    elif args.build:
        ret = build_rpm(porter, args.rootpath)
        if ret != "":
            logger.error(f"build failed : BuildRequire : {ret}")
            sys.exit(1)
    elif args.buildinstall:
        ret = build_install_rpm(porter, args.rootpath)
        if ret != "":
            logger.error("Build & install failed\n")
            sys.exit(1)
    elif args.download:
        download_source(porter, args.path)
    elif args.json:
        porter.store_json(args.path)


if __name__ == "__main__":
    main()
