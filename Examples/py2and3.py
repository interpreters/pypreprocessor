#!/usr/bin/env python
# py2and3.py

'''
py2and3.py - Python2x and Python3x playing nicely together.

This source file can run different code for different python
 interpreters.

This file has 3 different modes:
    1. If run as 'python py2and3.py'
        It will output 'You are using Python 2x'
    2. If run as 'python3 py2and3.py'
        It will output 'You are using python 3x'
    3. If run with any version that doesn't fall under 2x or 3x
        It will output 'Python version not supported'
'''

import sys
from pypreprocessor import pypreprocessor

#exclude
if sys.version[:3].split('.')[0] == '2':
    pypreprocessor.defines.append('python2')
if sys.version[:3].split('.')[0] == '3':
    pypreprocessor.defines.append('python3')

pypreprocessor.parse()
#endexclude
#ifdef python2
print('You are using Python 2x')
#else
#ifdef python3
print('You are using python 3x')
#else
print('Python version not supported')
#endifall
