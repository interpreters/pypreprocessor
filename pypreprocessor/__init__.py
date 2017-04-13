#!/usr/bin/env python
# pypreprocessor.py

__author__ = 'Evan Plaice'
__version__ = '0.6.0'
#modified by hendiol


# changed by hendiol at 18.01.2017: added reset_internal for processing several files after each other
# changed by hendiol at 11.04.2017: trying to get nested #ifdefs handeld

#develop nested further

import sys
import os
import traceback
import imp

class preprocessor:
    def __init__(self, inFile=sys.argv[0], outFile='',
                 defines=[], removeMeta=False, escapeChar = '#'):
        # public variables
        self.defines = defines
        self.input = inFile
        self.output = outFile
        self.removeMeta = removeMeta
        self.escapeChar = escapeChar
        # private variables
        self.__linenum = 0
        self.__excludeblock = False
        self.__ifblocks = []
        self.__ifconditions = []
        self.__evalsquelch = True
        self.__outputBuffer = ''
    
    # reseting internal things to parse a second file
    def reset_internal(self):
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

    def search_defines(self, define):
        if define in self.defines:
            return True
        else:
            return False

    # the #ifdef directive
    def compare_defines_and_conditions(self, defines, conditions):
        # if defines and conditions lists have no intersecting values (ie. else = true)
        if not [val for val in defines if val in conditions]:
            return True
        else:
            return False
            
    def __if(self):
        value = bool(self.__ifblocks)
        for ib in self.__ifblocks: #may better use list comprehension
            value=value and ib
        return not value    #not: because True means removing



 # evaluate
    def lexer(self, line):
    # return values are (squelch, metadata)
        if not self.__ifblocks and self.__excludeblock is False: 
            # squelch the preprocessor parse on the first
            # pass to prevent preprocessor infinite loop
            if 'pypreprocessor.parse()' in line:
                return True, True
            if line[:1] != self.escapeChar:
                return False, False
        # handle #define directives
        if line[:7] == self.escapeChar + 'define':
            if len(line.split()) != 2:
                self.exit_error(self.escapeChar + 'define')
            else:
                self.define(line.split()[1])
                return False, True
        # handle #undef directives
        elif line[:6] == self.escapeChar + 'undef':
            if len(line.split()) != 2:
                self.exit_error(self.escapeChar + 'undef')
            else:
                self.undefine(line.split()[1])
                return False, True
        # handle #exclude directives
        elif line[:8] == self.escapeChar + 'exclude':
            if len(line.split()) != 1:
                self.exit_error(self.escapeChar + 'exclude')
            else:
                self.__excludeblock = True
        # handle #endexclude directives
        elif line[:11] == self.escapeChar + 'endexclude':
            if len(line.split()) != 1:
                self.exit_error(self.escapeChar + 'endexclude')
            else:
                self.__excludeblock = False
                return False, True  
        # handle #ifdef directives
        elif line[:6] == self.escapeChar + 'ifdef':
            if len(line.split()) != 2:
                self.exit_error(self.escapeChar + 'ifdef')
            else:
                self.__ifblocks.append(self.search_defines(line.split()[1]))
                self.__ifconditions.append(line.split()[1])  
                return False, True
        # handle #else directives
        elif line[:5] == self.escapeChar + 'else':
            if len(line.split()) != 1:
                self.exit_error(self.escapeChar + 'else')
            else:
                self.__ifblocks[-1]=not(self.search_defines(self.__ifconditions[-1]))
            return False, True                  
        # handle #endif directives
        elif line[:6] == self.escapeChar + 'endif':
            if len(line.split()) != 1:
                self.exit_error(self.escapeChar + 'endif')
            else:
                if len(self.__ifconditions)>1:
                    self.__ifblocks.pop(-1)
                    self.__ifcondition=self.__ifconditions.pop(-1)
                else:
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
        # open the input file
        input_file = open(os.path.join(self.input),'r')
        try:
            # process the input file
            for line in input_file:
                self.__linenum += 1
                # to squelch or not to squelch
                print('__________________')
                print('lexer',self.__linenum)
                print('Def',self.defines)
                print('Cond',self.__ifconditions)
                print('Ifs',self.__ifblocks)
                print('Eval',self.__evalsquelch)
                print(self.__if())
                #
                squelch, metaData = self.lexer(line)
                # 
                print('----')
                print('Def',self.defines)
                print('Cond',self.__ifconditions)
                print('Ifs',self.__ifblocks)
                print('Eval',self.__evalsquelch)
                print(self.__if())
                print(squelch, metaData)
                print(line)
                #
                # process and output
                if self.removeMeta is True:
                    if metaData is True or squelch is True:
                        continue
                if squelch is True:
                    self.__outputBuffer += self.escapeChar + line
                    continue
                if squelch is False:
                    self.__outputBuffer += line
                    continue
        finally:
            input_file.close()
        self.post_process()

    # post-processor
    def post_process(self):
        try:
            # open file for output (no auto-run)
            if self.output != '':
                self.run = False
                output_file = open(self.output, 'w')
            # open tmp file
            else:
                self.run = True
                self.output = 'tmp_' + os.path.basename(self.input)
                output_file = open(self.output, 'w')
            # write post-processed code to file
            output_file.write(self.__outputBuffer)
        finally:
            output_file.close()
        # resolve postprocess stage depending on the mode
        '''
        if self.run == False:
            sys.exit(0)
        else:
        #'''
        if self.run == True:
            # if this module is loaded as a library override the import
            if imp.lock_held() is True:
                    self.override_import()
            else:
                self.on_the_fly()
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
            exec(open(self.output,"rb").read())
        except:
            self.rewrite_traceback()
        finally:
            # remove tmp file
            os.remove(self.output)    


pypreprocessor = preprocessor()