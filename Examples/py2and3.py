#!/usr/bin/env python
# py2and3.py

from pypreprocessor import pypreprocessor
import sys

if sys.version[:3].split('.')[0] == '2':
    pypreprocessor.defines.append('python2')
    pass
elif sys.version[:3].split('.')[0] == '3':
    pypreprocessor.defines.append('python3')
    pass
else:
    print('python' + version.split('.')[0] + ' not supported') 
    sys.exit(1)
    
pypreprocessor.parse()

#ifdef python2
print('You are using Python 2x')
#ifdef python3
print('You are using python 3x')
#else
print('Python version not supported')
#endif
