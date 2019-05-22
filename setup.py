# # # # GENERATED FILE -- DO NOT MODIFY # # # #
from setuptools import setup, find_packages
from shutil import copy
from distutils.extension import Extension
from codecs import open
import os
import os.path
import fnmatch

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

sources = []
outputs = []
for path, subdirs, files in os.walk('aat/src'):
    for name in files:
        fp = os.path.join(path, name)
        if fp.endswith('cpp'):
            outputs.append(fp.replace('.cpp', '').replace('/src', ''))
            sources.append(fp)

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().split()


def find(pattern, path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)

setup(
    name='aat',
    version='0.0.2',
    description='Analytics library',
    long_description=long_description,
    url='https://github.com/timkpaine/aat',
    download_url='https://github.com/timkpaine/aat/archive/v0.0.2.tar.gz',
    author='Tim Paine',
    author_email='timothy.k.paine@gmail.com',
    license='Apache 2.0',
    install_requires=requires,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='algorithmic trading cryptocurrencies',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={'dev': requires + ['pytest', 'pytest-cov', 'pylint', 'flake8', 'mock']},
    entry_points={
        'console_scripts': [
            'aat=aat:main',
        ],
    },

    ext_modules=[
        Extension(x,
                  include_dirs=["aat/include"],
                  sources=[y],
                  libraries=["boost_python"]) for x, y in zip(outputs, sources)
    ]

)

binding = find('test*.so', 'build')
library = find('_cpp_helpers*.so', 'build')

print("copying test.so")
copy(binding, 'aat')

print("copying _cpp_helpers.so")
copy(library, 'aat/exchanges')
