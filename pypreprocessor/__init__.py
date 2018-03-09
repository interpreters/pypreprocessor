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
class preprocessor:
    def __init__(self, inFile=sys.argv[0], outFile='', defines=[], \
            removeMeta=False, escapeChar=None, mode=None, escape='#', \
            run=True, resume=False, save=True):
        # public variables
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
        self.__linenum = 0
        self.__excludeblock = False
        self.__ifblocks = []
        self.__ifconditions = []
        self.__evalsquelch = True
        self.__outputBuffer = ''

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
        self.__ifblocks = []
        self.__ifconditions = []
        self.__evalsquelch = True
        self.__outputBuffer = ''

    # the #define directive
    def define(self, define):
        self.defines.append(define)

    # the #undef directive
    def undefine(self, define):
        # re-map the defines list excluding the define specified in the args
        self.defines[:] = [x for x in self.defines if x != define]

    # search: if define is defined
    def search_defines(self, define):
        if define in self.defines:
            return True
        else:
            return False

    #returning: validness of #ifdef #else block
    def __if(self):
        value = bool(self.__ifblocks)
        for ib in self.__ifblocks:
            value *= ib   #* represents and: value = value and ib
        return not value    #not: because True means removing

    # evaluate
    def lexer(self, line):
        # strip any and all leading whitespace characters
        line = line.lstrip()
        # return values are (squelch, metadata)
        if not (self.__ifblocks or self.__excludeblock):
            if 'pypreprocessor.parse()' in line:
                return True, True
            #this block only for faster processing (not necessary)
            elif line[:len(self.escape)] != self.escape:
                return False, False
        # handle #define directives
        if line[:len(self.escape) + 6] == self.escape + 'define':
            if len(line.split()) != 2:
                self.exit_error(self.escape + 'define')
            else:
                self.define(line.split()[1])
                return False, True
        # handle #undef directives
        elif line[:len(self.escape) + 5] == self.escape + 'undef':
            if len(line.split()) != 2:
                self.exit_error(self.escape + 'undef')
            else:
                self.undefine(line.split()[1])
                return False, True
        # handle #exclude directives
        elif line[:len(self.escape) + 7] == self.escape + 'exclude':
            if len(line.split()) != 1:
                self.exit_error(self.escape + 'exclude')
            else:
                self.__excludeblock = True
                return False, True
        # handle #endexclude directives
        elif line[:len(self.escape) + 10] == self.escape + 'endexclude':
            if len(line.split()) != 1:
                self.exit_error(self.escape + 'endexclude')
            else:
                self.__excludeblock = False
                return False, True
        # handle #ifnotdef directives (is the same as: #ifdef X #else)
        elif line[:len(self.escape) + 8] == self.escape + 'ifdefnot':
            if len(line.split()) != 2:
                self.exit_error(self.escape + 'ifdefnot')
            else:
                self.__ifblocks.append(not self.search_defines(line.split()[1]))
                self.__ifconditions.append(line.split()[1])
                return False, True
        # handle #ifdef directives
        elif line[:len(self.escape) + 5] == self.escape + 'ifdef':
            if len(line.split()) != 2:
                self.exit_error(self.escape + 'ifdef')
            else:
                self.__ifblocks.append(self.search_defines(line.split()[1]))
                self.__ifconditions.append(line.split()[1])
                return False, True
        # handle #else...
        # handle #elseif directives
        elif line[:len(self.escape) + 6] == self.escape + 'elseif':
            if len(line.split()) != 2:
                self.exit_error(self.escape + 'elseif')
            else:
                self.__ifblocks[-1] = not self.__ifblocks[-1]
                  #self.search_defines(self.__ifconditions[-1]))
                self.__ifblocks.append(self.search_defines(line.split()[1]))
                self.__ifconditions.append(line.split()[1])
            return False, True
        # handle #else directives
        elif line[:len(self.escape) + 4] == self.escape + 'else':
            if len(line.split()) != 1:
                self.exit_error(self.escape + 'else')
            else:
                self.__ifblocks[-1] = not self.__ifblocks[-1]
                  #self.search_defines(self.__ifconditions[-1]))
            return False, True
        # handle #endif..
        # handle #endififdef
        elif line[:len(self.escape) + 10] == self.escape + 'endififdef':
            if len(line.split()) != 2:
                self.exit_error(self.escape + 'endififdef')
            else:
                if len(self.__ifconditions) >= 1:
                    self.__ifblocks.pop(-1)
                    self.__ifcondition = self.__ifconditions.pop(-1)
                else:
                    self.__ifblocks = []
                    self.__ifconditions = []
                self.__ifblocks.append(self.search_defines(line.split()[1]))
                self.__ifconditions.append(line.split()[1])
                return False, True
        # handle #endifall directives
        elif line[:len(self.escape) + 8] == self.escape + 'endifall':
            if len(line.split()) != 1:
                self.exit_error(self.escape + 'endifall')
            else:
                self.__ifblocks = []
                self.__ifconditions = []
                return False, True
        # handle #endif and #endif numb directives
        elif line[:len(self.escape) + 5] == self.escape + 'endif':
            if len(line.split()) != 1:
                self.exit_error(self.escape + 'endif number')
            else:
                try:
                    number = int(line[6:])
                except ValueError as VE:
                    #print('ValueError',VE)
                    #self.exit_error(self.escape + 'endif number')
                    number = 1
                if len(self.__ifconditions) > number:
                    for i in range(0, number):
                        self.__ifblocks.pop(-1)
                        self.__ifcondition = self.__ifconditions.pop(-1)
                elif len(self.__ifconditions) == number:
                    self.__ifblocks = []
                    self.__ifconditions = []
                else:
                    print('Warning try to remove more blocks than present', \
                      self.input, self.__linenum)
                    self.__ifblocks = []
                    self.__ifconditions = []
                return False, True
        else: #No directive --> execute
            # process the excludeblock
            if self.__excludeblock is True:
                return True, False
            # process the ifblock
            elif self.__ifblocks: # is True:
                return self.__if(), False
            #here can add other stuff for deleting comnments eg
            else:
                return False, False

    # error handling
    def exit_error(self, directive):
        print('File: "' + self.input + '", line ' + str(self.__linenum))
        print('SyntaxError: Invalid ' + directive + ' directive')
        sys.exit(1)
    def rewrite_traceback(self):
        trace = traceback.format_exc().splitlines()
        index = 0
        for line in trace:
            if index == (len(trace) - 2):
                print(line.replace("<string>", self.input))
            else:
                print(line)
            index += 1

    # parsing/processing
    def parse(self):
        self.__reset_internal()
        self.check_deprecation()
        # open the input file
        input_file = io.open(os.path.join(self.input), 'r', encoding=self.readEncoding)
        try:
            # process the input file
            for line in input_file:
                self.__linenum += 1
                # to squelch or not to squelch
                squelch, metaData = self.lexer(line)
                # process and output
                if self.removeMeta is True:
                    if metaData is True or squelch is True:
                        continue
                if squelch is True:
                    if metaData:
                        self.__outputBuffer += self.escape + line
                    else:
                        self.__outputBuffer += self.escape[0] + line
                    continue
                if squelch is False:
                    self.__outputBuffer += line
                    continue
        finally:
            input_file.close()
            #Warnings for unclosed #ifdef blocks
            if self.__ifblocks:
                print('Warning: Number of unclosed Ifdefblocks: ', len(self.__ifblocks))
                print('Can cause unwished behaviour in the preprocessed code, preprocessor is safe')
                try:
                    select = input('Do you want more Information? ')
                except SyntaxError:
                    select = 'no'
                select = select.lower()
                if select in ('yes', 'true', 'y', '1'):
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
            # open file for output
            output_file = io.open(self.output, 'w', encoding=self.writeEncoding)
            # write post-processed code to file
            output_file.write(self.__outputBuffer)
        finally:
            output_file.close()

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
            f = io.open(self.output, "r", encoding=self.readEncoding)
            exec(f.read())
            f.close()
        except:
            self.rewrite_traceback()

pypreprocessor = preprocessor()
