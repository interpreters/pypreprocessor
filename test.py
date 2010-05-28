#!/usr/bin/env python
# test.py

from pypreprocessor import pypreprocessor
import sys 

pypreprocessor.output = "output_file.py"

version = sys.version[:3]
if version.split('.')[0] == '2':
    pypreprocessor.defines.append('python2')
elif version.split('.')[0] == '3':
    pypreprocessor.defines.append('python3')
    
pypreprocessor.parse()
