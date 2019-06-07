"""
import logging
import os
import re

path = os.getcwd()
try:
    tfile = open("job.last")
except Exception as e:
    logging.info("Error in " + path + " -- " + str(e))
else: pass
tread = tfile.read()
tfile.close()
match = re.search('number of occupied orbitals :[ ]*([0-9]*)', tread)
mx_orbital = 0
if match:
    mx_orbital = match.group(1)
    print(mx_orbital)
else:
    logging.info("Error in " + path + " -- No occupied orbitals found in submit.job")
"""

""""
import sched
import time
import curses
import sys
s = sched.scheduler(time.time, time.sleep)


sm = 1
total = 2
compt = 0
progstring = []
for i in ["0", "o", "f"]:
    progstring += ["Files done in 1 YES."]

def checkloop():
    stdscr.clear()
    report_progress(progstring)
    if compt == 3: print("Yes")
    s.enter(1, 1, checkloop)

def report_progress(progstring):
    global compt
    compt += 1
    stdscr.addstr(0, 0, "Total progress: {0}/{1} [{2:11}]".format(str(sm), str(total),"#" * (compt%11)))
    for i in range(len(progstring)):
        stdscr.addstr(i+1, 5, progstring[i])
    stdscr.refresh()

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    s.enter(0, 1, checkloop)
    s.run()    
"""
"""
import re

ffile = open("submit.job")
fread = ffile.read()
ffile.close()

mtc = re.search(r"###BEGIN_COMMANDS\n(.*)\n###END_COMMANDS\n", fread, re.MULTILINE)

if mtc:
   fread = fread.replace(mtc.group(), "###BEGIN_COMMANDS\njobex -c 100\n###END_COMMANDS\n")

ffile = open("submit.job", "w")
ffile.write(fread)
ffile.close()
"""
"""
import subprocess
import os
from subprocess import run, PIPE

FNULL = open(os.devnull, "w")

p = subprocess.Popen(['python3','MinMun.py'],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
print(p.communicate(b'yes')[0].decode())
print(p.communicate(b'no')[0].decode())
"""
import re
import subprocess, os
"""
def giveexener(fescfout):
    output = ""
    rep = 1
    fescfout = "escf.log"
    fobj = open(fescfout, "r")
    for line in fobj:
      if "I R R E P" in line:
          output += line[30:47]
      if "Excitation energy / eV:" in line:
            energ = line[40:48]
            for line2 in fobj:
                if rep == 1:
                   if "velocity representation:" in line2:
                      osc = line2[40:65]
                      output += energ + " " + osc
                      break
                if rep == 2:
                   if "length representation:" in line2:
                      osc = line2[40:65]
                      output += energ + " " + osc
                      break
                if rep == 3:
                   if "mixed representation:" in line2:
                      osc = line2[40:65]
                      output += energ + " " + osc
                      break
    fobj.close() #close escf.out file
    fobj = open("exited.file", "w")
    fobj.write(output)
    fobj.close()

    rfile = open("exited.file", 'r')
    for line in rfile:
        if "I R R E P" in line:
            mtc = re.search("I R R E P[ ]*([0-9a-z\"]+)[ ]*", line)
            print(mtc.group(1))

giveexener("escf.log")

print(b"HJANd\n a")
print("HJANd\n a".encode())
"""
"""
def panama_(paper):
    subprocess.run(["mkdir", "panama_files"])
    rep = 1
    paper = "escf.log"
    fobj = open(paper, "r")
    mtc = ""
    cmpt = 0
    orbitals_per_sym = 5
    for line in fobj:
      if "I R R E P" in line:
          cmpt = 0
          mtc = re.search("I R R E P[ ]*([0-9a-z\"]+)[ ]*", line)
          mtc = mtc.group(1)
      if "Excitation energy / eV:" in line and cmpt<orbitals_per_sym:
            cmpt += 1
            energ = line[40:48]
            energ = energ.replace(" ", "")
            energ = energ.replace("\n", "")
            for line2 in fobj:
                if rep == 1:
                   if "velocity representation:" in line2:
                      osc = line2[40:65]
                      energ = float(energ)
                      minenerg = energ - 0.0001
                      maxenerg = energ + 0.0001
                      tempstr = "2\nescf.log\n1\n" + str(minenerg) + "\n" + str(maxenerg) + "\n"
                      subprocess.run("panama", input=tempstr.encode())
                      subprocess.run(["dscf", "-proper"])
                      os.rename("td.plt", "./panama_files/"  + mtc + "_orb_" + str(cmpt))
                      break
    fobj.close()
    print('ALL FILES DONE')

panama_("escf.log")
"""
"""
a = ["&", "a", "f"]
print("/".join(a))

import argparse

parser = argparse.ArgumentParser(description='SaturnCommand')
parser.add_argument("file", help='file or directory name (format xyz to be processed)', type=str)
parser.add_argument("-s", "--shrink", action='store_true', help="remove input spacing")
parser.add_argument("-c", "--complete", action="store_true", help="customize process")
parser.add_argument("-t", "--turbo", action="store_true", help="use turbo files")
parser.add_argument('-create', "--creation_only", action="store_true",
                    help="only creates turbomole files, doesn't qsub them")
parser.add_argument("-panama", "--panama", action="store_true",
                    help="DO NOT CALL DIRECTLY, is used for panama calculations")
parser.add_argument("-force", "--forcing", action="store_true", help="DO NOT CALL, force operations to be processed")
parser.add_argument("-ns", "--nosort", action="store_true", help="do not sort files and put them in folders")
parser.add_argument("-o", dest="operations", help="DO NOT CALL, decides which operations to use")
args = parser.parse_args()
if args.operations: print(args.operations)
"""
"""
import os
p = subprocess.Popen(["ssh", "frontale", "ls"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
result = p.stdout.readlines()
result = [i.decode() for i in result]
print("".join(result))
"""

a = [1, 2, 1, 1,3]
print(list(filter(lambda x: x != 2, a)))