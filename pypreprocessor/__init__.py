#!/usr/bin/env python
# pypreprocessor.py

__author__ = 'Evan Plaice'
__coauthor__ = 'Hendi O L, Epikem'
__version__ = '0.7.7'

import sys
import os
import traceback
import imp
import io
import collections


class preprocessor:
    def __init__(self, inFile=sys.argv[0], outFile='', defines={}, removeMeta=False, 
                 escapeChar=None, mode=None, escape='#', run=True, resume=False, save=True):
        # public variables
        #support for <=0.7.7
        if isinstance(defines, collections.Sequence):
            defines = {x:None for x in defines} 
        self.defines = defines
        self.input = inFile
        self.output = outFile
        self.removeMeta = removeMeta
        self.escapeChar = escapeChar
        self.mode = mode
        self.escape = escape
        self.run = run
        self.resume = resume
        self.save = save
        self.readEncoding = sys.stdin.encoding
        self.writeEncoding = sys.stdout.encoding

        # private variables
        self.__reset_internal()

    def check_deprecation(self):
        def deprecation(message):
            import warnings
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(message, DeprecationWarning)
            warnings.simplefilter('default', DeprecationWarning)

        if self.escapeChar != None:
            deprecation("'pypreprocessor.escapeChar' is deprecated. Use 'escape' instead.")
            if self.escape == '#':
                self.escape = self.escapeChar

        if self.mode != None:
            msg = "'pypreprocessor.mode' is deprecated. Use 'run/resume/save' options instead."
            if self.run != True or self.resume != False or self.save != True:
                msg += " Ignoring 'pypreprocessor.mode'."
            else:
                if self.mode.lower() == 'run':
                    self.run = True
                    self.resume = False
                    self.save = False
                elif self.mode.lower() == 'pp':
                    self.run = False
                    self.resume = False
                    self.save = True
                elif self.mode.lower() == 'ppcont':
                    self.run = False
                    self.resume = True
                    self.save = True
                elif self.mode is not None:
                    print('Unknown mode : ' + str(self.mode))
            deprecation(msg)

    # reseting internal things to parse a second file
    def __reset_internal(self):
        self.__linenum = 0
        self.__excludeblock = False
        self.__ifblocks = [] # contains the evaluated if conditions 
        self.__ifconditions = [] # contains the if conditions
        self.__outputBuffer = ''

    # the #define directive
    def define(self, define):
        self.defines[define]=val

    # the #undef directive
    def undefine(self, define):
        if define in self.defines:
            self.defines.pop(define)

    # search: if define is defined
    def search_defines(self, define):
        return define in self.defines

    def evaluate(self, line):
        """
            Evaluate the content of a #if, #elseif, #elif directive

        :params
            line (str): definition name
            
        """
        return eval(line, self.defines)

    #returning: validness of #ifdef #else block
    def __validate_ifs(self):
        # no ifs mean we pass else check all ifs are True
        return not self.__ifblocks and all(self.__ifblocks)

    def __is_directive(self, line, directive, *size):
        """
            Checks the `line` is a `directive` and , if `size` is provided, checks its number of 
            elements is amongst the list of allowed `size` 

        :params:
            line (str): line to check

            directive (str): directive to be found in the `line`

            *size (int): list of allowed number of elements to compose the directive. Can be empty
        
        """
        if line.startswith(self.escape + directive):
            if size and len(line.split()) not in size:
                self.exit_error(self.escape + directive)
            return True
        return False

    # evaluate
    def lexer(self, line):
    # return values are (squelch, metadata)
        if not (self.__ifblocks or self.__excludeblock):
            if 'pypreprocessor.parse()' in line:
                return True, True

        # put that block here for faster processing
        if not line.startswith(self.escape): #No directive --> execute
            # exclude=True if we are in an exclude block or the ifs are not validated
            return self.__excludeblock or not self.__validate_ifs(), False

        elif self.__is_directive(line, 'define', 2,3):
            self.define(*line.split()[1:])

        elif self.__is_directive(line, 'undef', 2):
            self.undefine(line.split()[1])

        elif self.__is_directive(line, 'exclude', 1):
            self.__excludeblock = True

        elif self.__is_directive(line, 'endexclude', 1):
            self.__excludeblock = False

        elif self.__is_directive(line, 'ifdefnot', 2):
            self.__ifblocks.append(not self.search_defines(line.split()[1]))
            self.__ifconditions.append(line.split()[1])

        elif self.__is_directive(line, 'ifdef', 2):
            self.__ifblocks.append(self.search_defines(line.split()[1]))
            self.__ifconditions.append(line.split()[1])

        elif self.__is_directive(line, 'if'):
            self.__ifblocks.append(self.evaluate(' '.join(line.split()[1:])))
            self.__ifconditions.append(' '.join(line.split()[1:]))

        # since in version <=0.7.7, it didn't handle #if it should be #elseifdef instead.
        # kept elseif with 2 elements for retro-compatibility (equivalent to #elseifdef).
        elif self.__is_directive(line, 'elseif'):
            # do else
            self.__ifblocks[-1] = not self.__ifblocks[-1] 
            # do if
            if len(line.split()) == 2:
                #old behaviour
                self.__ifblocks.append(self.search_defines(line.split()[1]))
            else:
                #new behaviour
                self.__ifblocks.append(self.evaluate(' '.join(line.split()[1:])))
            self.__ifconditions.append(' '.join(line.split()[1:]))
 
        elif self.__is_directive(line, 'else', 1):
            self.__ifblocks[-1] = not self.__ifblocks[-1] #opposite of last if

        elif self.__is_directive(line, 'endififdef', 2):
            # do endif
            if len(self.__ifconditions) >= 1:
                self.__ifblocks.pop(-1)
                self.__ifconditions.pop(-1)
            # do ifdef
            self.__ifblocks.append(self.search_defines(line.split()[1]))
            self.__ifconditions.append(line.split()[1])

        elif self.__is_directive(line, 'endifall', 1):
            self.__ifblocks = []
            self.__ifconditions = []

        # handle #endif and #endif<numb> directives
        elif self.__is_directive(line, 'endif', 1):
            try:
                number = int(line[6:])
            except ValueError as VE:
                number = 1

            if len(self.__ifconditions) >= number:
                for i in range(0, number):
                    self.__ifblocks.pop(-1)
                    self.__ifconditions.pop(-1)
            else:
                print('Warning trying to remove more blocks than present', \
                    self.input, self.__linenum)
                self.__ifblocks = []
                self.__ifconditions = []

        else: 
            # unknown directive or comment
            if len(line.split()[0]) > 1:
                print('Warning unknown directive or comment starting with ', \
                        line.split()[0], self.input, self.__linenum)

        return False, True

    # error handling
    def exit_error(self, directive):
        print('File: "' + self.input + '", line ' + str(self.__linenum))
        print('SyntaxError: Invalid ' + directive + ' directive')
        sys.exit(1)

    def rewrite_traceback(self):
        trace = traceback.format_exc().splitlines()
        trace[-2]=trace[-2].replace("<string>", self.input))
        for line in trace:
            print(line)


    # parsing/processing
    def parse(self):
        self.__reset_internal()
        self.check_deprecation()
        # open the input file
        try:
            with io.open(os.path.join(self.input), 'r', encoding=self.readEncoding) as input_file:
                for self.__linenum, line in enumerate(input_file):
                    exclude, metaData = self.lexer(line)
                    # process and output
                    if self.removeMeta:
                        if metaData or exclude:
                            continue
                    if exclude:
                        if metaData:
                            self.__outputBuffer += self.escape + line
                        else:
                            self.__outputBuffer += self.escape[0] + line
                        continue
                    else:
                        self.__outputBuffer += line
                        continue
        finally:
            #Warnings for unclosed #ifdef blocks
            if self.__ifblocks:
                print('Warning: Number of unclosed Ifdefblocks: ', len(self.__ifblocks))
                print('Can cause unwished behaviour in the preprocessed code, preprocessor is safe')
                try:
                    select = input('Do you want more Information? ')
                except SyntaxError:
                    select = 'no'
                select = select.lower()
                if select.lower() in ('yes', 'true', 'y', '1'):
                    print('Name of input and output file: ', self.input, ' ', self.output)
                    for i, item in enumerate(self.__ifconditions):
                        if (item in self.defines) != self.__ifblocks[i]:
                            cond = ' else '
                        else:
                            cond = ' if '
                        print('Block:', item, ' is in condition: ', cond)
        self.post_process()

    # post-processor
    def post_process(self):
        try:
            # set file name
            if self.output == '':
                self.output = self.input[0:-len(self.input.split('.')[-1])-1]+'_out.'+self.input.split('.')[-1]

            # write post-processed code to file
            with io.open(self.output, 'w', encoding=self.writeEncoding) as output_file:
                output_file.write(self.__outputBuffer)
        finally:
            pass

        if self.run:
            # if this module is loaded as a library override the import
            if imp.lock_held() is True:
                self.override_import()
            else:
                self.on_the_fly()

        if not self.save:
            # remove tmp file
            if os.path.exists(self.output):
                os.remove(self.output)

        if not self.resume:
            # break execution so python doesn't
            # run the rest of the pre-processed code
            sys.exit(0)

    # postprocessor - override an import
    def override_import(self):
        try:
            moduleName = self.input.split('.')[0]
            tmpModuleName = self.output.split('.')[0]
            del sys.modules[moduleName]
            sys.modules[tmpModuleName] = __import__(tmpModuleName)
            sys.modules[moduleName] = __import__(tmpModuleName)
        except:
            self.rewrite_traceback()
        finally:
            # remove tmp (.py & .pyc) files
            os.remove(self.output)
            os.remove(self.output + 'c')

    # postprocessor - on-the-fly execution
    def on_the_fly(self):
        try:
            with io.open(self.output, "r", encoding=self.readEncoding) as f:
                exec(f.read())
        except:
            self.rewrite_traceback()

pypreprocessor = preprocessor()
