#!/usr/bin/env python
# pypreprocessor.py

from subprocess import call
import traceback, sys, os

class preprocessor:
    def __init__(self):
        self.defines = []
        self.input = os.path.join(sys.path[0],sys.argv[0])
        self.output = ''
        self.process = True

    # the #define directive
    def define(self, define):
        self.defines.append(define)

    def searchDefines(self, define):
        if define in self.defines:
            return True
        else:
            return False
            
    # the #undef directive
    def undefine(self, define):
        self.defines[:] = [x for x in self.defines if x != define]

    def parse(self):
        outputBuffer = ''
        ifblock = False
        ifdef = False
        ifcondition = ''
        squelch = True

        input_file = open(self.input,'r')
        try:
            for line in input_file:
                # squelch preprocessor specific code on the first
                # pass to prevent preprocessor infinite loop
                if 'pypreprocessor' in line:
                    outputBuffer += '#' + line
                    continue
            
                # handle #define directives
                if line[:7] == '#define':
                    self.define(line.split()[1])
                    outputBuffer += line
                    continue
                
                # handle #undef directives                
                if line[:6] == '#undef':
                    self.undefine(line.split()[1])
                    outputBuffer += line
                    continue
                
                # handle #ifdef directives
                if ifblock == False:
                    # open an ifblock
                    if line[:6] == '#ifdef':
                        ifblock = True
                else:
                    # close an ifblock 
                    if line[:6] == '#endif':
                        ifblock = False
                        ifcondition = ''
                        squelch = True

                if ifblock == True:
                    # evaluate and process an #ifdef
                    if line[:6] == '#ifdef':
                        ifcondition = line.split()[1]
                        if self.searchDefines(ifcondition):
                            squelch = False
                        else:
                            squelch = True
                        outputBuffer += line
                        continue
                    # evaluate and process the #else
                    if line[:5] == '#else':
                        if not self.searchDefines(ifcondition):
                            squelch = False
                        else:
                            squelch = True
                        outputBuffer += line
                        continue
                
                # comment out code that isn't supposed to run 
                if ifblock == True and squelch == True:
                    outputBuffer += '#' + line
                else:
                    outputBuffer += line
        finally:
            input_file.close()
        
        # output to file
        if self.output != '':
            self.process = False
            output_file = open(self.output, 'w')            
        # create temp file to execute
        else:
            self.output = self.input + '.tmp'
            output_file = open(self.output, 'w')
            
        try:
            output_file.write(outputBuffer)
            print(outputBuffer)
            print(self.defines)
        finally:
            output_file.close()

        # run the script
        if self.process == True:
            ret = call(['python', self.output])
            if ret == 0:
                os.remove(self.output)

        # break execution so python doesn't
        # run the rest of the pre-processed code    
        sys.exit(0)

pypreprocessor = preprocessor()
