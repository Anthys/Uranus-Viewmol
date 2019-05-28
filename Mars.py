"""

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
"""
subprocess.run(["ls"])
print(subprocess.check_output(['ls']))
"""
"""
import sys, time

for i in range(100):
    time.sleep(0.1)
    print(" "*10, end='\r')
    print("."*(i%5), end="\r")
"""

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

from time import sleep

# A List of Items
items = list(range(0, 57))
l = len(items)

# Initial call to print 0% progress
printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
for i, item in enumerate(items):
    # Do stuff...
    sleep(0.1)
    # Update Progress Bar
    printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)