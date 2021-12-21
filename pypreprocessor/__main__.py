import argparse
from . import preprocessor

parser = argparse.ArgumentParser(
    description="Check https://github.com/interpreters/pypreprocessor for documentation",
    epilog="""Examples:
    python -m """+__package__+""" somepython.py post-proc.py -m -d DEBUG FILE:4 EXEC
    python -m """+__package__+""" table.json --escape #@ -d NUM:4 ID:1 
    """,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    usage=' python -m '+__package__+' input [output] [-h] [-r] [-m] [-e ESCAPE] [-d [DEFINE ...]]',
)
parser.add_argument("-r", "--run", help="Run on the fly", 
                    action='store_true', default=False)
parser.add_argument("-m", "--removeMeta", help="remove meta lines from the output", 
                    action='store_true', default=False)
parser.add_argument("-e", "--escape", help="define the escape sequence to use. Default is #")
parser.add_argument("-d", "--define", help="list of variable to define", nargs='*')
parser.add_argument("-o", "--overload", help="overload variable definition in the file by those \
                    provided by --define", action='store_true', default=False)
parser.add_argument("-q", "--quiet", help="No warning on ununderstable directives and missign ending",
                    action='store_true', default=False)
parser.add_argument("input", help="input file.")
parser.add_argument("output", nargs='?', help="output file. Default is <input_basename>_out.<input_extension>")
args = parser.parse_args()

p=preprocessor(inFile=args.input, mode=None, removeMeta=args.removeMeta, escapeChar=None, 
               run=args.run, resume=False, save=True, overload=args.overload, quiet=args.quiet)
if args.output:
    p.define = args.output
if args.define:
    for elem in args.define:
        p.define(*elem.split(':'))
    self.__reset_internal() # not very pythonic
if args.escape:
    p.escape = args.escape

p.parse()