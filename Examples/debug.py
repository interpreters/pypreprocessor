#!/usr/bin/env python
# debug.py

'''
debug.py - Flip debug-specific statements on/off like a switch.

Just add/remove the '#define debug' statement to turn debug
statements on/off
'''

from pypreprocessor import pypreprocessor

pypreprocessor.parse()

#define debug

#ifdef debug
print('The source is in debug mode')
#else
print('The source is not in debug mode')
#endif
