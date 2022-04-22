# pypreprocessor

## Features

**support c-style directives in python**

* using an intentionally limited subset of the c directives, and then some...

**can run post-processed code on-the-fly**

* pre-process and run code all in one shot
* accurately preserves error tracebacks for the source file

**can output to a file**

* as easily as setting a flag
* with a user specified filename if defined

**can strip all pre-processor data from the output**

* as easily as setting a flag
* removes all preprocessor directives
* removes all preprocessor specific code

**#defines can be set in code prior to processing**

* useful if you need to run a file in different modes
* eliminates the need for decision logic in the preprocessor itself

**nested #ifdef directives are supported**

* helpfull for more complicated code
* #endifall gives the opportunity to end all open blocks


## Benefits

**Ease of Use**

* all of the functionality required to run the pypreprocessor is contained in a single module
* adding preprocessor support is as simple as importing pypreprocessor to a file containing preprocessor directives and telling it to run
* the preprocessor preserves errors in the pre and post processed code as much as possible
* the preprocessor will break execution and output traceback errors if it sees invalid preprocessor directives

**Dynamic**

* pypreprocessor has multiple option of operation
* it can generate a new post-processed version of a source file absent all of the preprocessor information
* or it can pre-process and run code transparently the same way as c-style languages do

**Simple**

* the source footprint for the pypreprocessor code is very small
* the preprocessor is designed to be as simple and lightweight as possible

## Syntax

The syntax for pypreprocessor uses a select subset of the standard c-style preprocessor directives, and then some...

**Supported directives**

* defines constants (valued or not) used by the preprocessor
```python
#define constant [value]
```

* removes a constant from the list of defined constants
```python
#undef constant
```

* makes the subsequent block of code available if the specified constant is set
```python
#ifdef constant
```

* makes the subsequent block of code available if the specified constant is not set
```python
#ifndef constant
```

* makes the subsequent block of code available if the specified condition returns true
```python
#if boolean_condition
```

* makes the subsequent block of code available if all of the preceding #ifdef, #elif, #if statements returns false
```python
#else
```

* makes the subsequent block of code available if all of the preceding #ifdef, #elif, #if statements return false and the specifified condition returns true
```python
#elif boolean_condition
```

* required to close out an #ifdef/#else block
```python
#endif
```

* Interrupts execution and returns error when reached
```python
#error
```

**Unofficial supported directives**

Unofficial directives exist to ease writing long files but should not be used in file that could be preprocessed without pypreprocessor 

* possibility to close all open blocks
```python
#endifall
```

* excludes the subsequent block of code (conditionals not included). I know it doesn't fit into the standard set of c-style directives but it's too handy to exclude (no pun).
```python
#exclude
```

* required to close out an #exclude block
```python
#endexclude
```

* Attempts closing <num> #ifdef/#else blocks
```python
#endif<num>
```

* Similar to #ifndef
```python
#ifnotdef constant
```

* Similar to #ifndef
```python
#ifdefnot constant
```

* Similar to #elif boolean_condition
```python
#elseif boolean_condition
```

* Similar to #elif constant
```python
#elseifdef constant
```

* Similar to #endif followed by #ifdef constant
```python
#endififdef constant
```

**Unsupported directives**

Unsupported directives are not handled by pypreprocessor and concidered as comment

* Inserts a particuliar header from another file. This has no use in Python
```python
#include
```

* Issues special commands to the compiler, using a standardized method. This has no use in Python
```python
#pragma
```

**Options**

The following options need to be set prior to pypreprocessor.parse()


```python
pypreprocessor.defines.append('define')
```
add defines to the preprocessor programmatically, this allows the source file to have some decision logic to decide which 'defines' need to be set

```python
pypreprocessor.run = True / False
pypreprocessor.resume = True / False
pypreprocessor.save = True / False
pypreprocessor.overload = True / False
pypreprocessor.quiet = True / False
```
set the options of the preprocessor:

* run: Run the preprocessed code if true. Default is true
* resume: Return after a file is preprocessed and can preprocess a next file if true. Default is false
* save: Save preprocessed code if true. Default is true
* overload: Any defines added to the preprocessor will overload existing defines. Default is false
* quiet: no warning about not understood directives or missing #indef

```python
pypreprocessor.input = 'inputFile.py'
```
required if you are preprocessing a module that is going to be imported. you can also use it to process external files.

```python
pypreprocessor.output = 'outputFile.py'
```
set this to get a user defined name for the output file, otherwise the default is used: ``` 'inputFile_out.py' ```

```python
pypreprocessor.removeMeta = True
```
set this to remove the metadata from the output, useful if you're generating a 'clean' version of the source

```python
pypreprocessor.readEncoding = sys.stdin.encoding
pypreprocessor.writeEncoding = sys.stdout.encoding
```
set this to make preprocessor use encoding

## Applications

**Include support for debug-specific information**

It is often useful to provide statements within code specific to debugging, such as, print statements used to verify correct outputs. But, removing those debug statements can be painful and introduce new bugs while migrating to the production version.

Why not leave them...

By setting a "#define debug" at the top of the module and wrapping all of the debug statements in "#ifdef debug" blocks; disabling that code during production is as easy as adding another hash mark before the "#define debug" statement.

For a working example see:

* [/examples/debug.py](https://github.com/evanplaice/pypreprocessor/blob/master/Examples/debug.py)

**Python2 -> Python3 code conversion**

Producing code that can be run in both Python 2 and Python 3 is as easy as...

1. check the version of the python interpreter in use
2. set a #define in the preprocessor indicating the version
3. add #ifdef directives on the code that is version specific

For a working example see:

* [/examples/py2and3.py](https://github.com/evanplaice/pypreprocessor/blob/master/Examples/py2and3.py)

**Writing code from Debug -> Production in the same file**

Ever wanted to run a file with debug-specific code during development but output a clean version specific source file for release? Here's how...

1. make a source file that takes the arguments 'debug' and 'production'
2. put the debug code in "#ifdef debug" blocks
3. then run 'filename.py debug' during development
4. or 'filename.py production' to output a version without any of the pypreprocessor metadata

For a working example see:

* [/examples/debug2production.py](https://github.com/evanplaice/pypreprocessor/blob/master/Examples/debug2production.py)

Note: This file also contains a 'postprocessed' mode that shows what pypreprocessor actually outputs. It's so simple it'll probably make you ::facepalm:: ;)
