import argparse
import logging



import os.path
def is_valid_file(parser, arg):

    if not os.path.exists(arg):
        parser.error("File %s doesn't exist" % arg)
    elif not arg[-3:]== "xyz":
        parser.error('Format not .xyz')
    else:
        return arg

parser = argparse.ArgumentParser(description='test')

parser.add_argument("-test", dest="testfile", required=True,

                help="test", type=lambda f: open(f))


    try:
        args = parser.parse_args()
        args.testfile = args.testfile.read()
    except FileNotFoundError:
        print(3)
        return
    else:
        print(4)
        print(args.testfile)
"""
subprocess.run(["ls"])
print(subprocess.check_output(['ls']))
"""