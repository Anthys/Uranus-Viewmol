import time
import datetime
import argparse
import logging
import subprocess
import os.path
import os
import sys
from shutil import copyfile
import sched

def get_input():

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
        loggin.info("Arguments for gtm: " + arg1 + " " + arg2)

        if not shrink: print(spr)

        time1 = ""
        time2 = ""
        unit1 = " "
        unit2 = " "

        units = {"s": 1, "min": 60, "h": 60 * 60, "": None}

        while unit1 not in units.keys():
            unit1 = input("Enter maximum time unit (s, default min or h):")
        if unit1 == "": unit1 = "min"

        while True:
            ans = ""
            try:
                time1 = float(input("Enter maximum time allowed for each process (in {0}): ".format(unit1)))
            except ValueError:
                print("Wrong value")
                continue
            else:
                if tcalculs>1:
                    ttime1 = time1*units[unit1]
                    while not ans in ["y", "n"]:
                        ans = input("Certain [y/n]? Total time = {0}".format(time.strftime('%H:%M:%S', time.gmtime(ttime1*((tcalculs//(mx_paralel_calculs+1))+1)))))
                else: break
            if ans == "y": break

        if not shrink: print(spr)

        """

        while unit2 not in units.keys():
            unit2 = input("Enter ?? time unit (s, default min or h):")
        if unit2 == "": unit2 = "min"

        while True:
            try:
                time2 = float(input("Enter maximum time allowed for iterations (in {0}): ".format(unit2)))
            except ValueError:
                print("Wrong value")
                continue
            else:
                break
        """

        time1 = time1 * units[unit1]
        time2 = time1-30
        time1 = time.strftime('%H:%M:%S', time.gmtime(time1))
        time2 = time.strftime('%H:%M:%S', time.gmtime(time2))

        name = ""

        if not shrink: print(spr)

        while not len(name) > 3:
            name = input("Enter the project name (length>3): ")

        return arg1, arg2, time1, time2, name


def is_valid(arg):


    if args.force:
        return arg
    if not os.path.exists(arg):
        parser.error("File %s doesn't exist" % arg)
    elif not arg[-4:] == ".xyz":
        parser.error('Format not .xyz')
    else:
        return arg


def create_job_files(xyz, label = ""):

    if not is_valid(xyz): quit()

    rwork = rroot + "/temp" + label
    subprocess.run(["mkdir", "temp" + label])
    os.chdir(rwork)
    copyfile(rroot + "/" + xyz, rwork + "/" + xyz)
    subprocess.run(["tp", "-g", xyz])

    os.system("gtm " + arg1 + " " + arg2)

    prejobfile = open("submit.job")
    jobfile = prejobfile.read()
    prejobfile.close()

    jobfile = jobfile.replace("h_cpu=hh:mm:ss", "h_cpu="+time1)
    jobfile = jobfile.replace("s_cpu=hh:mm:ss", "s_cpu="+time2)
    jobfile = jobfile.replace("nom_par_defaut", name + label)

    towrite = open("submit.job", "w")
    towrite.write(jobfile)
    towrite.close()
    logging.info(xyz + " added")

    #print("-> Processing of each files." +
    #      " Make them alternate in a given number of cores (ex 20), taking turn each time a file has been completed." +
    #      " Error handling if there is not enough cores available.")
    return rwork


def launch_job(path):
    os.chdir(path)
    os.system("qsub " + "submit.job")
    logging.info("Process started in " + path)


def check_end(path):

    global dirlist

    os.chdir(path)
    if "GEO_OPT_CONVERGED" in os.listdir():
        logging.info("Process successful in " + path)
        dirlist.remove(path)
    elif "GEO_OPT_FAILED" in os.listdir() or "not.converged" in os.listdir():
        logging.info("Process failed in " + path)
        dirlist.remove(path)
    else: pass


def checkloop(sc):

    global dirlist, maxdir, compt
    compt+=1

    if not dirlist:
        print("All files done.")
        return
    for i in dirlist:
        check_end(i)
    print(" "*40, end='\r')
    print(str(-len(dirlist)+maxdir) + "/" + str(maxdir) + " files done." + "["+"."*(compt%4)+"]", end="\r")
    s.enter(3, 1, checkloop, (sc,))


logging.basicConfig(filename='test_log.log',level=logging.DEBUG,\
      format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


logging.info(str(datetime.datetime.now()) + " -- process started")

parser = argparse.ArgumentParser(description='SaturnCommand')
parser.add_argument("file", help="file or directory name (format xyz to be processed)", type=str)
parser.add_argument('-f', "--force", action="store_true", help="force the file to be processed")
parser.add_argument('-s', "--shrink", action="store_true", help="remove input spacing")
args = parser.parse_args()

binput= True
shrink = (True if args.shrink else False)
spr = "---\n"*5
rroot = os.getcwd()

tcalculs=0
mx_paralel_calculs = 4

if os.path.isdir(args.file):
    trroot = rroot + "/" + args.file
    os.chdir(trroot)
    for i in os.listdir():
        os.chdir(trroot)
        if i[-4:] == ".xyz":
            tcalculs += 1
else: tcalculs = 1

arg1, arg2, time1, time2, name = get_input()
dirlist = []
compt = 0


os.chdir(rroot)
if os.path.isdir(args.file):
    print(rroot)
    rroot = rroot + "/" + args.file
    os.chdir(rroot)
    for i in os.listdir():
        os.chdir(rroot)
        if i[-4:] == ".xyz":
            dirlist.append(create_job_files(i, "_" + i[:-4].replace(".", "_")))
elif os.path.isfile(args.file):
    dirlist.append(create_job_files(args.file))

print(dirlist)

maxdir = len(dirlist)

for i in dirlist:
    launch_job(i)


#subprocess.run(["mkdir", "Results"])

s = sched.scheduler(time.time, time.sleep)
s.enter(0, 1, checkloop, (s,))
s.run()