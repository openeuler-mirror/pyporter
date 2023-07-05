# pyporter

#### Description
A rpm packager bot for python modules from pypi.org

#### Preparation
Install below software before using this tool
1. gcc
2. gdb
3. libstdc++-devel
4. python3-cffi
5. rpmbuild


#### Installation

Install from source
```
pip install .
```

Install with develop mode
```
pip install -e .
```

#### Instructions

pyporter is a tool to create spec file and create rpm for python modules
For more details, please use `pyporter -h`

Create spec file, and output spec file named `python-<package>.spec`
```
pyporter <package> -s -o python-<package>.spec
```

#### Contribution

You could install pre commit hook before commit your code, it will check your code format and style.

```python
pip install pre-commit
```
Refer https://pre-commit.com/

1.  Fork the repository
2.  Create Feat_xxx branch
3.  Commit your code
4.  Create Pull Request

#### How to create a rpm file

1.  Create spec file, `pyporter -s  filename`
2.  Get required python modules, `pyporter -R filename`
3.  Build and Install rpm package, `pyporter -B filename`
4.  For more detail, `pyporter -h`
