import argparse
import logging
import subprocess
import os.path
import os
from shutil import copyfile

parser = argparse.ArgumentParser(description='CommandTest')
parser.add_argument("-f", dest="file", required=True, help="file name", type=str)
parser.add_argument('-d', "--debug", action="store_true")

binput= True

def is_valid_file(arg):
    if args.debug:
        return arg
    if not os.path.exists(arg):
        parser.error("File %s doesn't exist" % arg)
    elif not arg[-3:] == "xyz":
        parser.error('Format not .xyz')
    else:
        return arg


args = parser.parse_args()

if not is_valid_file(args.file):
    quit()


rroot = os.getcwd()
rwork = rroot + "/temp"
file = args.file
print(args.file)
subprocess.run(["mkdir", "temp"])
os.chdir(rwork)
copyfile(rroot + "/" + file, rwork + "/" + file)
subprocess.run(["tp", "-g", args.file])

if binput:
    arg1 = ""
    arg2 = ""
    print("--\n"*5)
    print("r ridft")
    print("d dscf")
    while arg1 not in ["r", "d"]:
        arg1 = input("Enter first parameter: ").lower()
    print("--\n"*5)
    print("o optimisation minimum")
    print("t transition state")
    print("O optimisation minimum + force")
    print("T transition state + force")
    print("f force")
    print("F energy + force")
    print("p pathway")
    print("x tddft")
    print("X opt + tddft")
    while arg2 not in ["o", "t", "O", "T", "f", "F", "p", "x", "X"]:
        arg2 = input("Enter second parameter: ")
    arg1 = "-" + arg1
    arg2 = "-" + arg2

subprocess.run(["which", "gtm"])
os.system("gtm " + arg1 + " " + arg2)
#subprocess.run(["gtm", arg1, arg2])