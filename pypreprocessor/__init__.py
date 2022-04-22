#!/usr/bin/env python
# pypreprocessor.py

__author__ = 'Evan Plaice'
__coauthor__ = 'Hendi O L, Epikem, Laurent Pinson'
__version__ = '1.0'

import sys
import os
import traceback
import imp
import io
import collections
import re

#support for <=0.7.7
class customDict(dict):
    def append(self, var):
        self[var]=True


class preprocessor:
    __overloaded = []
    defines = customDict()

    def __init__(self, inFile=sys.argv[0], outFile='', defines={}, removeMeta=False, 
                 escapeChar=None, mode=None, escape='#', run=True, resume=False, 
                 save=True, overload=True, quiet=False):
        # public variables
        # support for <=0.7.7
        if isinstance(defines, collections.Sequence):
            for x in defines:
                self.define(*x.split(':'))
        else:
            for x,y in defines.items():
                self.define(x,y)
        self.input = inFile
        self.output = outFile
        self.removeMeta = removeMeta
        self.escapeChar = escapeChar
        self.mode = mode
        self.escape = escape
        self.run = run
        self.resume = resume
        self.save = save
        self.overload = overload
        self.quiet = quiet
        self.readEncoding = sys.stdin.encoding 
        self.writeEncoding = sys.stdout.encoding

        # private variables
        self.__reset_internal()

    def check_deprecation(self):
        """
            Deprecation checks for older implementation of this library
        
        """
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

    def __reset_internal(self):
        self.__linenum = 0
        self.__excludeblock = False
        # contains the evaluated if conditions
        # due to the introduction of #elif, elements of __ifblocks are duos of boolean
        # the 1st is the evaluation of the current #if or #elif or #else
        # the 2nd indicates if at least one #if or #elif was True in the whole #if/#endif block
        self.__ifblocks = []  
        # contains the if conditions
        self.__ifconditions = [] 
        self.__outputBuffer = ''
        self.__overloaded = list(self.defines.keys()) if self.overload else []

    def define(self, name, val=True):
        """
            Adds variable definition to the store as expected from a #define directive.
            The directive can contains no value as it would be tested with a #ifdef directive or 
            with a value for an evaluation as in an #if directive.

            Note: if the `name` was part of the initial definition and `overload` was set to 
            True, this new definition will be skipped
        
        :params
            name (str): definition name
            
            val (str): definition value when it exists. Default is None
        """
        # try conversion for number else evaluate() might fail
        try:
            val = int(val)
        except:
            # assume val is string 
            pass    
        if name not in self.__overloaded:
            self.defines[name]=val

    def undefine(self, define):
        """
            Removes variable definition from store as expected from an #undef directive

        :params
            define (str): definition name
            
        """
        if define in self.defines:
            self.defines.pop(define)

    def __is_defined(self, define):
        """
            Checks variable is defined as used in #ifdef, #ifnotdef & #elseif directives

        :params
            define (str): definition name
            
        """
        return define in self.defines

    def __evaluate_if(self, line):
        """
            Evaluate the content of a #if, #elseif, #elif directive

        :params
            line (str): definition name
            
        """
        try:
            # replace C-style bool format by Python's
            line = line.replace('&&', 'and').replace('||', 'or').replace('!','not ')
            return eval(line, self.defines) or False
        except BaseException as e:
            print(str(e))
            self.exit_error(self.escape + 'if')

    def __validate_ifs(self):
        """
            Evaluate if the successive #ifs block are validated for the current position

        :return
            ifs (bool): True if all ifs condition are validated

        """
        # no ifs mean we pass else check all ifs are True
        return not self.__ifblocks or all(x[0] for x in self.__ifblocks)

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

    def __cleanup_line(self, line):
        """
            Clean a line of anything that should not impact parsing such as C-style comment

        :params:
            line (str): line to check

        :return
            line (str): cleaned line
        
        """
        line= re.sub('\s*/\*.*\*/\s+', '', line) #remove /* */ C-style comment
        line= re.sub('\s*//.*', '', line) #remove // C-style comment
        return line

    def lexer(self, line):
        """
            Analyse the `line`. This method attempts to find a known directive and, when found, to 
            understand it and to perform appropriate action.

        :params
            line (str): line of code to analyse

        :return
            exclude (bool): should the line be excluded in the final output?

            metadata (bool): is this line a directive?

        """
        line = line.strip()
        if not (self.__ifblocks or self.__excludeblock):
            if 'pypreprocessor.parse()' in line:
                return True, True

        # put that block here for faster processing
        if not line.startswith(self.escape): #No directive --> execute
            # exclude=True if we are in an exclude block or the ifs are not validated
            return self.__excludeblock or not self.__validate_ifs(), False

        # strip line of any C-style comment
        line = self.__cleanup_line(line)

        if self.__is_directive(line, 'define', 2,3):
            self.define(*line.split()[1:])

        elif self.__is_directive(line, 'undef', 2):
            self.undefine(line.split()[1])

        elif self.__is_directive(line, 'exclude', 1):
            self.__excludeblock = True

        elif self.__is_directive(line, 'endexclude', 1):
            self.__excludeblock = False

        # #ifnotdef sounds better than #ifdefnot..
        elif self.__is_directive(line, 'ifdefnot', 2) or \
        self.__is_directive(line, 'ifnotdef', 2) or \
        self.__is_directive(line, 'ifndef', 2):
            _check = not self.__is_defined(line.split()[1])
            self.__ifblocks.append([ _check, _check])
            self.__ifconditions.append(line.split()[1])

        elif self.__is_directive(line, 'ifdef', 2):
            _check = self.__is_defined(line.split()[1])
            self.__ifblocks.append([ _check, _check])
            self.__ifconditions.append(line.split()[1])

        elif self.__is_directive(line, 'if'):
            _check = self.__evaluate_if(' '.join(line.split()[1:]))
            self.__ifblocks.append([ _check, _check])
            self.__ifconditions.append(' '.join(line.split()[1:]))

        # since in version <=0.7.7, it didn't handle #if it should be #elseifdef instead.
        # kept elseif with 2 elements for retro-compatibility (equivalent to #elseifdef).
        elif self.__is_directive(line, 'elseif') or \
        self.__is_directive(line, 'elif'):
            _cur, _whole = self.__ifblocks[-1]
            if len(line.split()) == 2:
                #old behaviour
                _check = self.__is_defined(line.split()[1])
            else:
                #new behaviour
                _check = self.__evaluate_if(' '.join(line.split()[1:]))
            self.__ifblocks[-1]=[ not _whole and _check, _whole or _check ]
            self.__ifconditions[-1]=' '.join(line.split()[1:])

        elif self.__is_directive(line, 'elseifdef', 2):
            _cur, _whole = self.__ifblocks[-1]
            _check = self.__is_defined(line.split()[1])
            self.__ifblocks[-1]=[ not _whole and _check, _whole or _check ]
            self.__ifconditions[-1]=' '.join(line.split()[1:])

        elif self.__is_directive(line, 'else', 1):
            _cur, _whole = self.__ifblocks[-1]
            self.__ifblocks[-1] = [not _whole, not _whole] #opposite of the whole if/elif block

        elif self.__is_directive(line, 'endififdef', 2):
            # do endif
            if len(self.__ifconditions) >= 1:
                self.__ifblocks.pop(-1)
                self.__ifconditions.pop(-1)
            # do ifdef
            self.__ifblocks.append(self.__is_defined(line.split()[1]))
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

            try:
                while number:
                    self.__ifblocks.pop(-1)
                    self.__ifconditions.pop(-1)
                    number-=1
            except:
                if not self.quiet:
                    print('Warning trying to remove more blocks than present', 
                          self.input, self.__linenum)

        elif self.__is_directive(line, 'error'):
            if self.__validate_ifs():
                print('File: "' + self.input + '", line ' + str(self.__linenum + 1))
                print('Error directive reached')
                sys.exit(1)

        else: 
            # escapechar + space ==> comment
            # starts with #!/ ==> shebang
            # else print warning
            if len(line.split()[0]) > 1 and not line.startswith('#!/') and not self.quiet:
                print('Warning unknown directive or comment starting with ', 
                        line.split()[0], self.input, self.__linenum + 1)

        return False, True

    # error handling
    def exit_error(self, directive):
        """
            Prints error and interrupts execution

        :params
            directive (str): faulty directive
            
        """
        print('File: "' + self.input + '", line ' + str(self.__linenum + 1))
        print('SyntaxError: Invalid ' + directive + ' directive')
        sys.exit(1)

    def rewrite_traceback(self):
        """
            Dumps traceback but with the input file name included

        """
        trace = traceback.format_exc().splitlines()
        trace[-2]=trace[-2].replace("<string>", self.input)
        for line in trace:
            print(line)

    def parse(self):
        """
            Main method:
            - reset internal counters/values
            - check & warn about deprecation
            - starts the parsing of the input file
            - warn of unclosed #ifdef blocks if any
            - trigger post-process activities

        """
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
            if self.__ifblocks and not self.quiet:
                print('Warning: Number of unclosed Ifdefblocks: ', len(self.__ifblocks))
                print('Can cause unwished behaviour in the preprocessed code, preprocessor is safe')
                try:
                    select = input('Do you want more Information? ')
                except SyntaxError:
                    select = 'no'
                if select.lower() in ('yes', 'true', 'y', '1'):
                    print('Name of input and output file: ', self.input, ' ', self.output)
                    for i, item in enumerate(self.__ifconditions):
                        if (item in self.defines) != self.__ifblocks[i]:
                            cond = ' else '
                        else:
                            cond = ' if '
                        print('Block:', item, ' is in condition: ', cond)
        self.post_process()

    def post_process(self):
        """
            Perform post-parsing activities:
            - write output file from parsing.
            - override import if requested or attempt execution with its content
            - remove output file if no save was requested
            - force exit if resume was not requested

        """
        try:
            # set file name
            if not self.output:
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
        """
            Override the import of the output of the processed file

        """
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
        """
            Execute output of the processed file

        """
        try:
            with io.open(self.output, "r", encoding=self.readEncoding) as f:
                exec(f.read())
        except:
            self.rewrite_traceback()

pypreprocessor = preprocessor()
