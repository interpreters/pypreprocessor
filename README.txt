===========
Python Preprocessor
===========

Features
=========
 - support c-style directives in python
 - can run post-processed code on-the-fly
 - can output to a file
 - can strip all pre-processor data from the output
 - #defines can be set in code prior to processing

Supported Directives
-------------
 - #define
 - #undef
 - #ifdef
 - #else
 - #endif
 - #exclude
 - #endexclude

Python Interpreter Compatibility
-------------
pypreprocessor itself was originally designed to provide developers
 with a simple solution to write python 2x and python 3x code in the
 same source file so compatibility is a must.
 
Currently pypreprocessor has been tested and works in:
 - 2.5
 - 2.6
 - 3.0
 - 3.1

2.4 support has been looked into and can easily be made possible if
 users request it.
 
There are no plans to support earlier versions of python unless
 there is sufficient demand from users.

Install
=========
Simple
-------------
1. download and unpack the contents.
2. copy pypreprocessor.py to the directory where it will be used

*Note: pypreprocessor is intentionally kept small and self-contained
 in a single source file to make it easy to use and/or package with
 other libraries/applications. As long as pypreprocessor exists this
 will remain true.*

Using pip
-------------
1. in a terminal enter:
    sudo pip install pypreprocessor

*Note: sudo is only necessary if the location of the python
 libraries requires root priveledges to access.* 

This is the easiest method to install pypreprocessor for system-wide
 use. The only downside is, pip currently only supports installing
 to python 2x.

Using setup.py
-------------
1. download and unpack the contents
2. open a terminal in the directory containing the contents
3. in the terminal enter:
    sudo python setup.py install
    
*Note: sudo is only necessary if the location of the python
 libraries requires root priveledges to access.*
 
To install for python 3x repeat steps 1 & 2 and for step 3 enter:
    sudo python3 setup.py install
    
Support
=========
For more extensive information on features, access to the source 
 repository, documentation, or examples of use cases involving
 pypreprocessor be sure to visit the project's Home Page.
