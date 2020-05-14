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
    
    scripts=['pyporter'],
)
