"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("square", type=int,
                    help="display a square of a given number")
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
                    help="increase output verbosity")
args = parser.parse_args()
answer = args.square**2
if args.verbosity == 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity == 1:
    print("{}^2 == {}".format(args.square, answer))
else:
    print(answer)
"""

"""
import subprocess
import os
from shutil import copyfile

rroot = os.getcwd()
rwork = rroot + "/temp"
file = "Venus.py"
subprocess.run(["mkdir", "temp"])
os.chdir(rwork)
copyfile(rroot + "/" + file, rwork + "/" + file)
open("Test.txt", "w")
"""
"""
import sched, time, os, logging
s = sched.scheduler(time.time, time.sleep)


dirlist = [1, 2]
maxdir = 1

def checkloop(sc):
    if not dirlist:
        print("All files done.")
        return
    #for i in dirlist:
    #    check_end(i)
    dirlist.append(3)
    print(str(len(dirlist) - maxdir) + "/" + str(maxdir) + " files done.", end="\r")
    s.enter(5, 1, checkloop, (sc,))


s.enter(0, 1, checkloop, (s,))
s.run()


def check_end(path):
    os.chdir(path)
    if "GEO_CONVERGED" in os.listdir():h)
logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
        logging.info("Process successful in " + path)
        dirlist.remove(path)
    elif "GeO_NOT_CONVERGED" in os.listdir():
        logging.info("Process failed in " + path)
        dirlist.remove(path)
    else: pass

"""
"""
import logging

logging.basicConfig(filename='/home/antys/log/log.log', level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
logging.info("__________________________")
logging.info("Process started")
"""
import re
a = "LVZFVHFDIVB :f zeFZEK EF \n ZEfzefZEFIF ZEOF truc:      20284ezjvfz"
p = re.compile("truc:[ ]*")
match = re.search('truc:[ ]*([0-9]*)', a)
print(match)
if match:
    print(match.group(1))