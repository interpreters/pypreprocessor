#!/usr/bin/env python
# debug2production.py

'''
debug2production.py - For schitzophrenic source files.

This source file has multiple modes of operation all of which can be
 controlled by passing an argument on the command line.

This file has 3 different modes:
    1. debug
        Run all of the code contained in the #define debug blocks
         and execute it on the fly.
        Just run 'python debug2production.py debug'.

    2. production
        Output the source to output.py with all of the meta-tags
         stripped.
        Just run it type 'python debug2production.py production'

    3. postprocessed
        Output the source to output.py but perserve all the
         metadata.
        Just run 'python debug2production.py postprocessed'
'''

import sys
from pypreprocessor import pypreprocessor

outputFile = 'output_file.py'

#exclude
# run the script in 'debug' mode
if 'debug' in sys.argv:
    pypreprocessor.defines.append('debug')

# run the script in 'production' mode
if 'production' in sys.argv:
    pypreprocessor.defines.append('production')
    pypreprocessor.output = outputFile
    pypreprocessor.removeMeta = True

# run the script in 'postprocessed' mode
if 'postprocessed' in sys.argv:
    pypreprocessor.defines.append('postprocessed')
    pypreprocessor.output = outputFile

pypreprocessor.parse()
#endexclude
#ifdef debug
print('This script is running in \'debug\' mode')
#else
#ifdef production
print('This script is running in \'production\' mode')
print('To see the output open ' + outputFile)
#else
#ifdef postprocessed
print('This script is running in \'postprocessed\' mode')
print('To see the output open ' + outputFile)
#endifall
