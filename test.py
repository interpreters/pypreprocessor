#!/usr/bin/env python
# test.py

from pypreprocessor import pypreprocessor
import sys
    
pypreprocessor.parse()

print('#define test:')
#define testdefine
#ifdef testdefine
print('this should print')
#else
print('this shouldn\'t print')
#endif
print('')
print('#undef test:')
#undef testdefine
#ifdef testdefine
print('this shouldn\'t print')
#else
print('this should print')
#endif
print('')
print('#ifdef test:')
#define testif
#define testif2
#ifdef testif
print('this should print')
#ifdef testnotif
print('this shouldn\'t print')
#ifdef testif2
print('this should print')
#else
print('this shouldn\'t print')
#endif
print('')
print('#else test:')
#ifdef foo
print('this shouldn\'t print')
#ifdef bar
print('this shouldn\'t print')
#ifdef baz
print('this shouldn\'t print')
#else
print('this should print')
#endif
