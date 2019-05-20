from setuptools import setup, find_packages
from distutils.extension import Extension
from codecs import open
import os
import os.path

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

sources = []
outputs = []
for path, subdirs, files in os.walk('algocoin/src'):
    for name in files:
        fp = os.path.join(path, name)
        if fp.endswith('cpp'):
            outputs.append(fp.replace('.cpp', '').replace('/src', ''))
            sources.append(fp)

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().split()

setup(
    name='aat',
    version='0.0.1',
    description='Algorithmic trading library',
    long_description=long_description,
    url='https://github.com/timkpaine/aat',
    download_url='https://github.com/timkpaine/aat/archive/v0.0.3.tar.gz',
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
    extras_require={'dev': requires + ['pytest', 'pytest-cov', 'pylint', 'flake8']},
    entry_points={
        'console_scripts': [
            'algocoin=algocoin:main',
        ],
    },

    ext_modules=[
        # Extension('algocoin/_extension', include_dirs=['algocoin/include'], sources=['algocoin/src/test.cpp'], libraries=['boost_python']),
        Extension(x,
                  include_dirs=["algocoin/include"],
                  sources=[y],
                  libraries=["boost_python"]) for x, y in zip(outputs, sources)
    ]
)
