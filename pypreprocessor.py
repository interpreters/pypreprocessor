#!/usr/bin/env python
# pypreprocessor.py

from subprocess import call
import traceback, sys, os

class preprocessor:
    def __init__(self):
        self.defines = []
        self.input = os.path.join(sys.path[0],sys.argv[0])
        self.output = ''

    # the #define directive
    def define(self, define):
        self.defines.append(define)

    def searchDefines(self, define):
        if define in self.defines:
            return True
        else:
            return False
            
    # the #ifdef directive
    def compareDefinesAndConditions(self, defines, conditions):
        # if both lists are empty (else = true)
        if not [val for val in defines if val in conditions]:
            return True
        else:
            return False
            
    # the #undef directive
    def undefine(self, define):
        self.defines[:] = [x for x in self.defines if x != define]

    # evaluate
    def evalDef(self, line): 
        # squelch preprocessor specific code on the first
        # pass to prevent preprocessor infinite loop
        if 'pypreprocessor' in line:
            return True
        # handle #define directives
        if line[:7] == '#define':
            self.define(line.split()[1])
            return False
        # handle #undef directives                
        if line[:6] == '#undef':
            self.undefine(line.split()[1])
            return False
        # handle #endif directives 
        if line[:6] == '#endif':
            self.ifblock = False
            self.ifcondition = ''
            self.ifconditions = []
            self.evalsquelch = True
            return False
        # handle #ifdef directives
        if line[:6] == '#ifdef':
            self.ifblock = True
            self.ifcondition = line.split()[1]
            self.ifconditions.append(line.split()[1])
        
        # process the ifblock
        if self.ifblock == True:
            # evaluate and process an #ifdef
            if line[:6] == '#ifdef':
                if self.searchDefines(self.ifcondition):
                    self.evalsquelch = False
                else:
                    self.evalsquelch = True
                return False
            # evaluate and process the #else
            elif line[:5] == '#else':
                if self.compareDefinesAndConditions(self.defines, self.ifconditions):
                    self.evalsquelch = False
                else:
                    self.evalsquelch = True
                return False
            else:
                return self.evalsquelch
        else:
            return False
          
    # parse
    def parse(self):
        outputBuffer = ''
        # open the input file
        input_file = open(self.input,'r')
        try:
            self.ifblock = False
            self.ifcondition = ''
            self.ifconditions = []
            self.evalsquelch = True
        
            # process the input file
            for line in input_file:
                
                squelch = self.evalDef(line)

                if squelch == True:
                    outputBuffer += '#' + line
                    continue
                if squelch == False:
                    outputBuffer += line
                    continue
        finally:
            input_file.close()
        
        # open file for output
        if self.output != '':
            self.run = False
            output_file = open(self.output, 'w')            
        # open tmp file for output
        else:
            self.run = True
            self.output = self.input + '.tmp'
            output_file = open(self.output, 'w')
            
        # write post-processed code to file 
        try:
            output_file.write(outputBuffer)
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
