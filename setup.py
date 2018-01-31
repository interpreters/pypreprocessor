#!/usr/bin/env python
# pypreprocessor's setup.py

# dependencies
# - pandoc - `sudo apt install pandoc`
# - pypandoc - `sudo pip install pypandoc`

# To update:
# - python setup.py sdist upload

#from distutils.core import setup
from setuptools import setup
from pypreprocessor import __version__, __author__
try:
    import pypandoc
    print('Creating README.rst')
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    print('Pypandoc not installed, skipping README.rxt creation')
    long_description = open('README.md').read();
setup(
    name = "pypreprocessor",
    py_modules = ['pypreprocessor'],
    version = __version__,
    description = "Run c-style preprocessor directives in python modules",
    author = __author__,
    author_email = "evanplaice@gmail.com",
    url = "https://github.com/interpreters/pypreprocessor",
    packages=['pypreprocessor'],
    long_description = long_description,
    license = open('LICENSE').read(),
    keywords = ["python", "preprocessor", "meta"],
    platforms = "all",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
    ]
)
