from setuptools import setup, find_packages, Extension
from codecs import open
import os
import os.path
import os
import sys
import sysconfig

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
PREFIX = sysconfig.get_config_vars()["prefix"]
name = "aat"

CPU_COUNT = os.cpu_count()
# *************************************** #
# Numpy build path and compiler toolchain #
# *************************************** #
try:
    # enable numpy faster compiler
    from numpy.distutils.ccompiler import CCompiler_compile
    import distutils.ccompiler

    distutils.ccompiler.CCompiler.compile = CCompiler_compile
    os.environ["NPY_NUM_BUILD_JOBS"] = str(CPU_COUNT)
except ImportError:
    pass  # no numpy


with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read().replace("\r\n", "\n")

if sys.version_info.major < 3 or sys.version_info.minor < 7:
    raise Exception("Must be python3.7 or above")

requires = [
    "aiostream>=0.3.1",
    "matplotlib>2.2",
    "numpy>=1.11.0",
    "pandas>=0.24.1",
    "perspective-python>=0.4.8",
    "pybind11>=2",
    "temporal-cache>=0.1.2",
    "tornado>=6.0",
    "traitlets>=4.3.3",
]

requires_dev = [
    "black>=23",
    "flake8>=3.7.9",
    "flake8-black>=0.2.1",
    "mock>=3.0.5",
    "mypy>=0.782",
    "pybind11>=2.4.3",
    "pytest>=6.0.1",
    "pytest-cov>=2.8.1",
    "pytest-faulthandler>=2.0.1",
    "Sphinx>=1.8.4",
    "sphinx-markdown-builder>=0.5.2",
    "types-pytz>=2021.1.2",
    "types-requests>=2.25.6",
] + requires


sources = [
    "aat/cpp/src/config/enums.cpp",
    "aat/cpp/src/config/parser.cpp",
    "aat/cpp/src/core/instrument/instrument.cpp",
    "aat/cpp/src/core/exchange/exchange.cpp",
    "aat/cpp/src/core/data/data.cpp",
    "aat/cpp/src/core/data/event.cpp",
    "aat/cpp/src/core/data/order.cpp",
    "aat/cpp/src/core/data/trade.cpp",
    "aat/cpp/src/core/position/account.cpp",
    "aat/cpp/src/core/position/cash.cpp",
    "aat/cpp/src/core/position/position.cpp",
    "aat/cpp/src/core/order_book/price_level.cpp",
    "aat/cpp/src/core/order_book/collector.cpp",
    "aat/cpp/src/core/order_book/order_book.cpp",
    "aat/cpp/src/python/binding.cpp",
]

extension = Extension(
    "aat.binding",
    define_macros=[("HAVE_SNPRINTF", "1")],
    include_dirs=[
        "aat/cpp/include",
        "aat/cpp/third/date/",
        "aat/cpp/third/pybind11/",
        "aat/cpp/third/pybind11_json/",
        "aat/cpp/third/nlohmann_json/",
    ],
    libraries=[],
    library_dirs=[],
    extra_compile_args=["-Wall"]
    + (["-std=c++1y"] if os.name != "nt" else ["/std:c++14"]),
    sources=sources,
)

setup(
    name=name,
    version="0.1.0",
    description="Algorithmic trading library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timkpaine/{}".format(name),
    author="Tim Paine",
    author_email="t.paine154@gmail.com",
    license="Apache 2.0",
    install_requires=requires,
    extras_require={"dev": requires_dev},
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="algorithmic trading cryptocurrencies",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "aat=aat:main",
            "aat-synthetic-server=aat.exchange.synthetic.server:main",
            "aat-view-strategy-results=aat.strategy.calculations:main",
        ]
    },
    ext_modules=[extension],
)
