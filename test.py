#!/usr/bin/env python
# test.py

import sys
from pypreprocessor import pypreprocessor

pypreprocessor.parse()

print('Testing Python ' + sys.version[:3] + ':')

tests = []

# #define test
#define testdefine
#ifdef testdefine
tests += ['#define: passed']
#else
tests += ['#define: failed']
#endif

# #undef test
#define testundef
#undef testundef
#ifdef testundef
tests += ['#undef: failed']
#else
tests += ['#undef: passed']
#endif

# #ifdef test
iftest = []
#define testif1
#define testif2
#ifdef testif1
iftest += [0]
#ifdef testnotif
iftest += [1]
#ifdef testif2
iftest += [0]
#else
iftest += [1]
#endif
if iftest == [0, 0]:
    tests += ['#ifdef: passed']
else:
    tests += ['#ifdef: failed']

# #else test
elsetest = []
#ifdef foo
elsetest += [1]
#ifdef bar
elsetest += [1]
#ifdef baz
elsetest += [1]
#else
elsetest += [0]
#endif
if 1 in elsetest:
    tests += ['#else: failed']
else:
    tests += ['#else: passed']

# #exclude test
excludetest = []
#exclude
excludetest += [1]
#endexclude
if 1 in excludetest:
    tests += ['#exclude: failed']
else:
    tests += ['#exclude: passed']

# print the results
for test in tests:
    print(test)
