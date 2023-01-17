#!/usr/bin/python3
"""
setup file for pyporter
"""
#******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Author: Zhipeng Xie
# Create: 2020-05-15
# Description: provide setup file for pyporter
# ******************************************************************************/

import setuptools

setuptools.setup(
    name='pyporter',
    version='0.1',
    url='https://gitee.com/openeuler/pyporter',
    author='Zhipeng Xie',
    author_email='xiezhipeng1@huawei.com',
    description="A rpm packager bot for python modules from pypi.org",
    license="Mulan PSL v2",
    classifiers=[
        'Environment :: Console',
        'License :: Mulan PSL v2',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    long_description=open('README.md').read(),
#    scripts=['pyporter'],
    entry_points={
        'console_scripts': [
            'pyporter = pyporter.pyporter:main',
        ]
    }
)
