#! /usr/bin/env python3
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

package = 'scopsowl'
version = '0.2017.12.20'


def readme():
    with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'README.md'
            )
    ) as f:
        return f.read()


setup(
    name=package,
    version=version,
    description='Fetch SCOPUS database information',
    long_description=readme(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
    ],
    license='GPL',
    author='Wolfson Liu',
    author_email='wolfsonliu@gmail.com',
    url='',
    packages=['scopsowl'],
    install_requires=[
        'numpy', 'pandas', 'time', 'logging', 'requests', 'urllib3'
    ],
    package_dir={'scopsowl': 'scopsowl'},
    data_files=[('api', ['data/scopus_api_keys']), ('logconf', 'data/logging.conf')],
    include_package_data=True,
    zip_safe=False
)
