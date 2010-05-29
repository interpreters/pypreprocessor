#!/usr/bin/env python
# test.py

from pypreprocessor import pypreprocessor
import sys

version = sys.version[:3]
if version.split('.')[0] == '2':
    pypreprocessor.defines.append('python2')
    pass
elif version.split('.')[0] == '3':
    pypreprocessor.defines.append('python3')
    pass
else:
    print('python' + version.split('.')[0] + ' not supported') 
    sys.exit(1)
    
#pypreprocessor.output = "output_file.py"
pypreprocessor.runcmd = "python"
pypreprocessor.parse()

#define def1

#define asda

#define adsafa

#define asda

#undef asda

#define asda

#ifdef def1
print('this is defined')
#ifdef defkjh
print('this is defined')
#ifdef asda
print('some stuff')
#else
print('blah blah')
#endif
