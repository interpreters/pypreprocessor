import sys
a = 150
from pypreprocessor import pypreprocessor
#[pypreprocessor]#exclude
#exclude
sys.exit(1)
#endexclude

#ifdef printTest
a+=50
#else
a-=50
#endif

#ifdef printTest
import os
print('Hello, world!')
print('가즈아ㅏㅏ')
print(a)
#endif
#[pypreprocessor]#endexclude