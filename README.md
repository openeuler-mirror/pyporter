# pyporter

#### Description
A rpm packager bot for python modules from pypi.org

#### Installation

1.  python3 setup.py install

#### Preparation
Install below software before using this tool
1.  gcc
2.  gdb
3.  libstdc++-devel
4.  python3-cffi

#### Instructions

pyporter is a tool to create spec file and create rpm for python modules
For more details, please use pyporter -h

pyporter &lt;package&gt; -s -b -d -o python-&lt;package&gt;.spec

#### Contribution

1.  Fork the repository
2.  Create Feat_xxx branch
3.  Commit your code
4.  Create Pull Request

#### How to create a rpm file

1.  Create spec file, pyporter -s XXX
2.  Get required python modules, pyporter -R XXX
3.  Build and Install rpm package, pyporter -B XXX
4.  For more detail, pyporter -h
