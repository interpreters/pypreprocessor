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

#ifdefnot testdefine
tests += ['#definenot: failed']
#else
tests += ['#definenot: passed']
#endif


# #not define test
#ifdef testdefine2
tests += ['#not define: failed']
#else
tests += ['#not define: passed']
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
#endif
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
#endif
#ifdef bar
elsetest += [1]
#endif
#ifdef baz
elsetest += [1]
#else
elsetest += [0]
#endif
if 1 in elsetest or len(elsetest) != 1:
    tests += ['#else: failed']
else:
    tests += ['#else: passed']
    
# #nested ifdef test
#define nested1
#define nested2
nesttest = []
#ifdef nested1
nesttest += [0]
#ifdef nested2
nesttest += [0]
#else
nesttest += [3]
#endif
nesttest += [0]
#else
nesttest += [4]
#ifdef nested2
nesttest += [5]
#else
nesttest += [6]
#endifall
#ifdef nested3
nesttest += [7]
#elseif nested2
nesttest += [0]
#else
nesttest += [9]
#endif
nesttest += [0]
#endif
if 1 in nesttest or len(nesttest)!=5:
    print(nesttest)
    tests += ['#nested: failed']
else:
    tests += ['#nested: passed']

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
    
# #still open #ifdefs test
print('If there was no warning with else,else,if: Warning Test Failed')
#ifdef car
#else
#ifdef bus
#else
#ifdef truck