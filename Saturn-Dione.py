import time
import argparse
import logging
import subprocess
import os.path
import os
import sys
from shutil import copyfile
import sched
import xml.etree.ElementTree as ET

user_input = True
shrink = False
spr = "---\n"*5
cores_per_calc=2
mx_parallel_calculations = 4
s = sched.scheduler(time.time, time.sleep)

tcalculations=0
rroot = os.getcwd()
dirlist = []
args = ""
parser = ""
compt = 0
path2name = {}

def get_input():

    if user_input:
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
        logging.info("Arguments for gtm: " + arg1 + " " + arg2)

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
                if tcalculations>1:
                    ttime1 = time1*units[unit1]
                    while not ans in ["y", "n"]:
                        ans = input("Certain [y/n]? Total time = {0}".format(time.strftime('%H:%M:%S', time.gmtime(ttime1*((tcalculations//(mx_parallel_calculations+1))+1)))))
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


def create_job_files(xyz, arg1, arg2, htime, stime, name, label = ""):

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

    jobfile = jobfile.replace("h_cpu=hh:mm:ss", "h_cpu="+htime)
    jobfile = jobfile.replace("s_cpu=hh:mm:ss", "s_cpu="+stime)
    jobfile = jobfile.replace("nom_par_defaut", name + label)
    jobfile = jobfile.replace("-pe mpi 2", "-pe mpi " + str(cores_per_calc))

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
        if len(dirlist)>=mx_parallel_calculations: launch_job(dirlist[mx_parallel_calculations-1])
    elif "GEO_OPT_FAILED" in os.listdir() or "not.converged" in os.listdir():
        logging.info("Process failed in " + path)
        dirlist.remove(path)
        if len(dirlist)>=mx_parallel_calculations: launch_job(dirlist[mx_parallel_calculations-1])
    elif compt%2==0:
        mydoc = ET.fromstring(subprocess.check_output(["qstat", "-xml"]))
        check = False
        for a in mydoc[0]:
            if a[2].text == path2name[path]: check = True
        if not check:
            logging.info("Process failed in "+ path)
            logging.info("Self-deletion in queue")
            dirlist.remove(path)
        '''
        for i in os.listdir():
            if ".o" in i:
                tfile = open(i)
                tread = tfile.read()
                if "program aoforce not found" in tread:
                    logging.info("AOFORCE NOT FOUND - Process failed in " + path)
                    dirlist.remove(path)
                    if len(dirlist) >= mx_parallel_calculations: launch_job(dirlist[mx_parallel_calculations - 1])
                tfile.close()
        '''
    else: pass


def checkloop(sc):

    global dirlist, maxdir, compt
    compt+=1

    if not dirlist:
        print("All files done.")
        logging.info("All files were computed")
        get_result()
        return
    for i in dirlist[:mx_parallel_calculations]:  # Works even if len(dirlist)<mx_parallel_calculations
        check_end(i)
    print(" "*40, end='\r')
    print(str(-len(dirlist)+maxdir) + "/" + str(maxdir) + " files done." + "["+"."*(compt%4)+"]", end="\r")
    s.enter(3, 1, checkloop, (sc,))


def get_result():
    subprocess.run(["mkdir", "Results"])

def main():

    global dirlist, maxdir, compt, shrink, tcalculations, rroot, args, parser

    parser = argparse.ArgumentParser(description='SaturnCommand')
    parser.add_argument("file", help="file or directory name (format xyz to be processed)", type=str)
    parser.add_argument('-f', "--force", action="store_true", help="force the file to be processed")
    parser.add_argument('-s', "--shrink", action="store_true", help="remove input spacing")
    parser.add_argument('-c', "--creation_only", action="store_true", help="only creates turbomole files, doesn't qsub them")
    args = parser.parse_args()

    shrink = (True if args.shrink else False)

    if os.path.isdir(args.file):
        trroot = rroot + "/" + args.file
        os.chdir(trroot)
        for i in os.listdir():
            if i[-4:] == ".xyz":
                tcalculations += 1
    else: tcalculations = 1

    arg1, arg2, time1, time2, name = get_input()

    os.chdir(rroot)
    if os.path.isdir(args.file):
        rroot = rroot + "/" + args.file
        os.chdir(rroot)
        for i in os.listdir():
            os.chdir(rroot)  # To put inside the create_job_file
            if i[-4:] == ".xyz":
                label = "_" + i[:-4].replace(".", "_")
                dirlist.append(create_job_files(i, label=label, arg1=arg1, arg2=arg2, htime=time1, stime=time2, name=name))
                path2name[dirlist[-1]] = name + label
    elif os.path.isfile(args.file):
        dirlist.append(create_job_files(args.file, arg1=arg1, arg2=arg2, htime=time1, stime=time2, name=name))
        path2name[dirlist[-1]] = name

    if args.creation_only:
        logging.info("Stopped after creating turbomole files.")
        logging.info("__________________________")
        quit()

    maxdir = len(dirlist)

    for i in range(mx_parallel_calculations):
        if len(dirlist) > i:
            launch_job(dirlist[i])
        else: break

    s.enter(0, 1, checkloop, (s,))
    s.run()

def initlog():
    logging.basicConfig(filename='/home/barres/log.log', level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
    logging.info("__________________________")
    logging.info("Process started")

if __name__ == "__main__":
    initlog()
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        logging.info("Process terminated by user command")
        logging.info("__________________________")
        sys.exit(0)
    except Exception as e:
        logging.info(str(e))
        logging.info("__________________________")
        sys.exit(0)