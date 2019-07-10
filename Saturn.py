import time
import argparse
import logging
import subprocess
import os.path
import os
from shutil import copyfile


def is_valid(arg):
    if args.force:
        return arg
    if not os.path.exists(arg):
        parser.error("File %s doesn't exist" % arg)
    elif not arg[-3:] == "xyz":
        parser.error('Format not .xyz')
    else:
        return arg


parser = argparse.ArgumentParser(description='SaturnCommand')
parser.add_argument("file", help="file name (format xyz)", type=str)
parser.add_argument('-f', "--force", action="store_true", help="force the file to be processed")
parser.add_argument('-s', "--shrink", action="store_true", help="remove input spacing")
args = parser.parse_args()


binput= True
shrink = False
spr = "---\n"*5

if not is_valid(args.file): quit()

if args.shrink: shrink = True

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
    if not shrink: print(spr)
    print("r ridft")
    print("d dscf")
    while arg1 not in ["r", "d"]:
        arg1 = input("Enter first parameter: ").lower()
    if not shrink: print(spr)
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

if not shrink: print(spr)

prejobfile= open("submit.job")
jobfile = prejobfile.read()
prejobfile.close()

time1 = ""
time2 = ""
unit1 = " "
unit2 = " "

units = {"s":1, "min":60, "h":60*60, "":None}

while not unit1 in units.keys():
    unit1 = input("Enter maximum time unit (default s, min or h):")

while True:
    try: time1 = float(input("Enter maximum time allowed for iterations (in {0}): ".format(unit1)))
    except ValueError: continue
    else: break

if not shrink: print(spr)

while not unit2 in units.keys():
    unit2 = input("Enter ?? time unit (default s, min or h):")

while True:
    try: time2 = float(input("Enter maximum time allowed for iterations (in {0}): ".format(unit2)))
    except ValueError: continue
    else: break

if unit1 == "": unit1 = "s"
if unit2 == "": unit2 = "s"

time1 = time.strftime('%H:%M:%S', time.gmtime(time1*units[unit1]))
time2 = time.strftime('%H:%M:%S', time.gmtime(time2*units[unit2]))

jobfile = jobfile.replace("h_cpu=hh:mm:ss", "h_cpu="+time1)
jobfile = jobfile.replace("s_cpu=hh:mm:ss", "s_cpu="+time2)

name=""

if not shrink: print(spr)

while not len(name)>3:
    name=input("Enter the project name (length>3): ")

jobfile = jobfile.replace("nom_par_defaut", name)

towrite = open("submit.job", "w")
towrite.write(jobfile)
towrite.close()

#os.system("qsub " + "submit.job")

print("Processing..")