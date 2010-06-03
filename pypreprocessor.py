#!/usr/bin/env python
# pypreprocessor.py

import sys
import os

class preprocessor:
    def __init__(self):
        self.defines = []
        self.input = os.path.join(sys.path[0],sys.argv[0])
        self.output = ''
        self.outputBuffer = ''
        self.removeMeta = False

    # the #define directive
    def define(self, define):
        self.defines.append(define)

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
            
    # the #undef directive
    def undefine(self, define):
        # re-map the defines list excluding the define specified in the args
        self.defines[:] = [x for x in self.defines if x != define]

    # evaluate
    def eval_pre(self, line): 
        # squelch preprocessor specific code on the first
        # pass to prevent preprocessor infinite loop
        # return values are (squelch, metadata)
        if 'pypreprocessor' in line:
            return True, True
        # handle #define directives
        if line[:7] == '#define':
            self.define(line.split()[1])
            return False, True
        # handle #undef directives                
        if line[:6] == '#undef':
            self.undefine(line.split()[1])
            return False, True
        # handle #endif directives 
        if line[:6] == '#endif':
            self.ifblock = False
            self.ifcondition = ''
            self.ifconditions = []
            self.evalsquelch = True
            return False, True
        # handle #ifdef directives
        if line[:6] == '#ifdef':
            self.ifblock = True
            self.ifcondition = line.split()[1]
            self.ifconditions.append(line.split()[1])
        
        # process the ifblock
        if self.ifblock is True:
            # evaluate and process an #ifdef
            if line[:6] == '#ifdef':
                if self.search_defines(self.ifcondition):
                    self.evalsquelch = False
                else:
                    self.evalsquelch = True
                return False, True
            # evaluate and process the #else
            elif line[:5] == '#else':
                if self.compare_defines_and_conditions(self.defines, self.ifconditions):
                    self.evalsquelch = False
                else:
                    self.evalsquelch = True
                return False, True
            else:
                return self.evalsquelch, True
        else:
            return False, False
          
    # parse
    def parse(self):
        # open the input file
        input_file = open(self.input,'r')
        self.ifblock = False
        self.ifcondition = ''
        self.ifconditions = []
        self.evalsquelch = True
        
        try:
            # process the input file
            for line in input_file:
                # to squelch or not to squelch
                squelch, metaData = self.eval_pre(line)
                # process and output
                if self.removeMeta is True and metaData is True:
                    continue
                if squelch is True:
                    self.outputBuffer += '#' + line
                    continue
                if squelch is False:
                    self.outputBuffer += line
                    continue
        finally:
            input_file.close()
        
        # open file for output (no auto-run)
        if self.output != '':
            self.run = False
            output_file = open(self.output, 'w')            
        # open tmp file for output (auto-run)
        else:
            self.run = True
            self.output = self.input + '.tmp'
            output_file = open(self.output, 'w')
            
        # write post-processed code to file 
        try:
            output_file.write(self.outputBuffer)
        finally:
            output_file.close()

        # run the post-processed code
        if self.run == True:
            try:
                exec(open(self.output,"rb").read())
            finally:
                os.remove(self.output)

        # break execution so python doesn't
        # run the rest of the pre-processed code    
        sys.exit(0)

pypreprocessor = preprocessor()
