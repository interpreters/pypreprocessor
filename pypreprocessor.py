#!/usr/bin/env python
# pypreprocessor.py

import traceback, os

class preprocessor:
    def __init__(self):
        self.defines = []
        self.output = "output.py"

    # the #define directive
    def define(self, define):
        self.defines.append(define)

    def searchDefines(self, define):
        if define in self.defines:
            return True
        else:
            return False

    def printDefines(self):
        for define in self.defines:
            print(define)
            
    # the #undef directive
    def undefine(self, define):
        self.defines[:] = [x for x in self.defines if x != define]

    def parse(self):
        outputBuffer = ''
        ifblock = False
        ifdef = False
        ifcondition = ''
        squelch = True

        input_file = open('example.py','r')
        try:
            for line in input_file:
                # remove #define directives
                if line[:7] == '#define':
                    self.define(line.split()[1])

                if line[:6] == '#undef':
                    self.undefine(line.split()[1])

                # handle #ifdef directives
                if ifblock == False:
                    if line[:6] == '#ifdef':
                        ifblock = True
                else:
                    if line[:6] == '#endif':
                        ifblock = False
                        ifcondition = ''
                        squelch = True

                if ifblock == True:
                    if line[:6] == '#ifdef':
                        ifcondition = line.split()[1]
                        if self.searchDefines(ifcondition):
                            squelch = False
                        else:
                            squelch = True
                        outputBuffer += line
                        continue
                    
                    if line[:5] == '#else':
                        if not self.searchDefines(ifcondition):
                            squelch = False
                        else:
                            squelch = True
                        outputBuffer += line
                        continue
                    
                if ifblock == True and squelch == True:
                    outputBuffer += '#'
                    outputBuffer += line
                else:
                    outputBuffer += line


            
        finally:
            input_file.close()
        
        output_file = open(self.output, 'w')
        try:
            output_file.write(outputBuffer)
        finally:
            output_file.close()

#        try:
#            exec outputBuffer
#        except Exception:
#            traceback.print_exc()
#            return 1

        print(outputBuffer)
        self.printDefines()

pypreprocessor = preprocessor()
