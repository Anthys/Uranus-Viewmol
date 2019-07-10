import time
import argparse
import logging
import subprocess
import os.path
import os
import sys
from shutil import copyfile
from collections import OrderedDict
import sched
import re
import curses

user_input = True
shrink = False
spr = "---\n"*5
mx_parallel_calculations = 4
texto = {
    "o": "optimisation minimum",
    "O": "top orbitals calculation",
    "f": "force calculations",
    "x": "exited states calculation"
}
symtable = {
    "d2h": ["ag", "b1g", "b2g", "b3g", "au", "b1u", "b2u", "b3u"],
    "d2": ["a", "b1", "b2", "b3"],
    "c2h": ["ag", "bg", "au", "bu"],
    "c2v": ["a1", "a2", "b1", "b2"],
    "cs": ["a'", 'a"'],
    "c1": ["a"]
}
s = sched.scheduler(time.time, time.sleep)
turbocheck = False
stdscr = ""

rroot = os.getcwd()
args = ""
parser = ""
compt = 0
name = "alphatest"
operations = ""
advancement = {}
total = 0
tempstring = []
sm = 0

def get_input():

    name = ""
    useturbo = 0
    operations = "oOfx"

    if not shrink: print(spr)

    while not len(name) > 3:
        name = input("##  Enter the project name (length>3): ")

    if not shrink: print(spr)
    
    if turbocheck:
        for i in os.listdir():
            if i in ["control", "coord", "basis", "auxbasis"]:
                print("Turbomole files detected, use them (u) or generate new turbomole files from .xyz (DEFAULT n)?")
                while not useturbo in ["", "u", "n"]:
                    useturbo = input("Enter choice: ")

                if useturbo in ['', "n"]: useturbo = False
                elif useturbo == "u": useturbo = True
                break

    if args.complete:
        print("##  Operations choice:")
        print("D default process (optimisation minimum + Orbitals .cub + frequency calculation + exited states")
        for i,j in texto.items():
            print(i + " " + j)
        done1 = False
        while not done1:
            operations = input("Enter operations required (can do multiple, order matters):")
            done1 = True
            input_error=""
            operations = operations.replace(" ", "")
            if operations == "": operations = "D"
            if operations == "D": operations = "oOfx"
            else:
                for indx in range(len(operations)):
                    i = operations[indx]
                    if i not in ["o", "f", "O", "x"]:
                        done1 = False
                        print("Wrong character")
                        break
                    elif i in ["O", "f", "x"]:
                        if not useturbo and "o" not in operations[:indx]:
                            input_error+= texto[i].capitalize() + " found without optimal minimum.\n"
                            operations = "o" + operations[:]
                    elif i == "t":
                        print("Need translational vector")
                        done1 = False
                        break
                if input_error:
                    print(input_error)
                    print("New chain of operation: " + operations)
    
    operations = list(OrderedDict.fromkeys([i for i in operations]))
    logging.info('Operations chosen: ' + str(operations))

    return operations, name, useturbo

def is_valid(arg):

    if not os.path.exists(arg):
        parser.error("File %s doesn't exist" % arg)
    elif not arg[-4:] == ".xyz":
        parser.error('Format not .xyz')
    else:
        return arg


def create_turbo_files(xyz, name, label = ""):

    rwork = rroot + "/" + name + label
    subprocess.run(["mkdir", name + label])
    os.chdir(rwork)
    copyfile(rroot + "/" + xyz, rwork + "/" + xyz)
    subprocess.run(["tp", "-g", xyz])
    logging.info("Turbo file created for " + xyz)
    os.chdir(rroot)
    return rwork

def main():

    global compt, shrink, rroot, name, operations, advancement, total

    if not is_valid(args.file): quit()

    shrink = (True if args.shrink else False)

    operations, name, useturbo = get_input()

    for i in operations:
        advancement[i] = []
    
    advancement["waiting"] = {i:[] for i in advancement.keys()}
    advancement["compteur"] = {i:0 for i in advancement["waiting"].keys()}
    total = len(operations)

    os.chdir(rroot)
    if not useturbo:
        if os.path.isdir(args.file):
            rroot = rroot + "/" + args.file
            os.chdir(rroot)
            for i in os.listdir():
                if i[-4:] == ".xyz":
                    advancement["waiting"][operations[0]].append(create_turbo_files(i, label="_" + i[:-4].replace(".", "_"), name=name))
        elif os.path.isfile(args.file):
            advancement["waiting"][operations[0]].append(create_turbo_files(args.file, name=name))
    else:
        advancement["waiting"][operations[0]].append(rroot)

    advancement["all"] = advancement["waiting"][operations[0]][:]

    if args.creation_only:
        logging.info("Stopped after creating turbomole files.")
        logging.info("__________________________")
        quit()


    initcurse()

    s.enter(0, 1, checkloop)
    s.run()


def launch_job(path, operation):

    os.chdir(path)
    
    if operation == 'o':
        """
        for i in ["GEO_OPT_CONVERGED", "GEO_OPT_FAILED"]:
            if i in os.listdir():
                os.remove(i)
        """
        os.system("gtm")
        time.sleep(0.1)
        os.system("qsub -N "+ name + "_minimum" + " submit.job")
        logging.info("Optimisation minimum started in " + path)

    elif operation == "O":
        #os.system("gtm " + "-r" + " " + "-o") # To de-comment when I'm certain that this command make the jobex -c 100 in the submit.job bu doesn't modify the other files.
        """
        for i in os.listdir():
            if ".cub" in i:
                os.remove(i)
        """
        try:
            o_file = open("job.last")
        except Exception as e:
            logging.info("Error in " + path + " -- " + str(e))
            return
        r_file = o_file.read()
        o_file.close()
        match = re.search('number of occupied orbitals :[ ]*([0-9]*)', r_file)
        mx_orbital = 0
        if match:
            mx_orbital = match.group(1)
            logging.info("For " + path + " , highest occupied orbital: " + str(mx_orbital))
        else:
            logging.info("Error in " + path + " -- No occupied orbitals found in submit.job")
            return
        o_file = open("control")
        r_file = o_file.read()
        o_file.close()
        r_file = r_file.replace("$end", "$pointval fmt=cub mo " + mx_orbital + "," + str(int(mx_orbital)+1) + "\n$end")
        o_file = open("control", "w")
        o_file.write(r_file)
        o_file.close()
        os.system("qsub -N "+ name + "_orbitals" + " submit.job")
        logging.info("Orbital calculation started in " + path)
    
    elif operation == "f":
        if "aoforce.log" in os.listdir():
            os.remove("aoforce.log")
        """
        try:
            o_file= open("submit.job")
        except Exception as e:
            logging.info("Error in " + path + " -- " + str(e))
            return
        else: pass
        """
        write_submit("aoforce > aoforce.log")
        os.system("qsub -N " + name + "_frequency" + " submit.job")
        logging.info("Frequency calculation started in " + path)

    elif operation == "x":
        if "escf.log" in os.listdir():
            os.remove("escf.log")
        write_sym()
        write_submit("escf > escf.log")
        os.system("qsub -N " + name + "_exited" + " submit.job")
        logging.info("Exited states calculation started in " + path)


def write_sym():
    a = open("control")
    b = a.read()
    mtc = re.search("\$symmetry (\w*)\n", b)
    tsym = ''
    if mtc:
        tsym = mtc.group(1)
        logging.info("Symmetry of molecule: " + tsym)
    else: logging.info("No symmetry found")

    tstring = ''
    for i in symtable[tsym]:
        tstring += " " + i + "          " + str(100//len(symtable[tsym])) + "\n"

    b = b.replace("$end", "$scfinstab rpas\n$soes\n" + tstring + "$denconv 1d-7\n$last step     define\n$end")
    logging.info(b)
    a.close()
    a = open("control", "w")
    a.write(b)
    a.close()


def get_sym(path):
    os.chdir(path)
    pass


def force_sym(path):
    pass

def remove_clean_end(path, include="", exclude = ""):
    if include:
        include = "*" + include
    os.chdir(path)
    ofile = open("submit.job")
    rfile = ofile.read()
    ofile.close()
    rfile = rfile.replace("#trap 'CleanExit", "#")
    excl = "--exclude lost+found --exclude 'MPI-*' --exclude 'NodeFile.*' " + ("--exclude '*." + exclude + "' " if exclude else "")
    rfile = rfile.replace("CleanExit", "rsync -rva" + excl + "${TMPDIR}/" + include + " ${SGE_O_WORKDIR}/")
    ofile = open("submit.job")
    ofile.write(rfile)
    ofile.close()

def write_submit(arg):
    ffile = open("submit.job")
    fread = ffile.read()
    ffile.close()

    mtc = re.search(r"###BEGIN_COMMANDS\n(.*)\n###END_COMMANDS\n", fread, re.MULTILINE)

    if mtc:
        fread = fread.replace(mtc.group(), "###BEGIN_COMMANDS\n" + arg + "\n###END_COMMANDS\n")

    ffile = open("submit.job", "w")
    ffile.write(fread)
    ffile.close()

def checkloop():

    global compt, advancement, tempstring, sm
    compt+=1

    if compt%2 == 0:
        csum = 0 #Current processing files sum
        wsum = 0 #Waiting files sum
        for indx in range(len(operations)):
            i = operations[indx]
            for tpath in advancement["waiting"][i]:
                wsum += 1
            for path in advancement[i]:
                csum += 1

                os.chdir(path)

                if i == "o":
                    if "GEO_OPT_CONVERGED" in os.listdir():
                        logging.info("Optimisation minimum successful in " + path)
                        advancement[i].remove(path)
                        advancement["compteur"][i] += 1
                        nextoperation(path, indx)
                    elif "GEO_OPT_FAILED" in os.listdir() or "not.converged" in os.listdir():
                        logging.info("Optimisation failed in " + path)
                        logging.info("Stopping process of this file to prevent global disaster")
                        advancement[i].remove(path)
                        progagate_error(indx)

                if i == "O":
                    tcompt = 0
                    for j in os.listdir():
                        if ".cub" in j:
                            tcompt+=1
                    if tcompt>=2:
                        logging.info("Two orbitals found in " + path)
                        advancement[i].remove(path)
                        advancement["compteur"][i] += 1
                        #nextoperation(path, indx) # Is already handled by the nextoperation function

                if i == "f":
                    if "aoforce.log" in os.listdir():
                        logging.info("Frequency successfully calculated in " + path)
                        advancement[i].remove(path)
                        advancement["compteur"][i] += 1
                        nextoperation(path, indx)

                if i == "x":
                    if "escf.log" in os.listdir():
                        logging.info("Exited states successfully calculated in " + path)
                        advancement[i].remove(path)
                        advancement["compteur"][i] += 1
                        nextoperation(path, indx)

        os.chdir(rroot)
        while csum <= mx_parallel_calculations and wsum>0:
            csum, wsum = checktoadvance(csum, wsum)
        sm = check_end()
        #print(" "*5, end='\r')
        tempstring = []
        for i in operations:
            tempstring+= [texto[i].capitalize() + ": " + str(advancement["compteur"][i]) + "/" + str(len(advancement["all"]))]
        #tempstring+= "Total progress: " + str(sm) + "/" + str(total) + "["+"."*(compt%4)+"]"
        #print(tempstring, end="\r")
    reportprogress(tempstring, sm, total)
    s.enter(1, 1, checkloop)

def reportprogress(progstring, sm, total):
    """progress: 0-10"""
    stdscr.clear()
    stdscr.addstr(0, 0, "Total progress: {0}/{1} [{2:11}]".format(str(sm), str(total), "#" * (compt % 11)))
    for i in range(len(progstring)):
        stdscr.addstr(i + 1, 5, progstring[i])
    stdscr.refresh()

def progagate_error(i_of_error):
    
    global total
    total -= len(operations) - i_of_error
    print("")
    logging.info("Error found at step " + str(i_of_error) + " ," + str(len(operations)-i_of_error) + " operations won't be done.")


def nextoperation(path, lastindx):
    global advancement
    if lastindx + 1 < len(operations):

        advancement["waiting"][operations[lastindx + 1]].append(path)

        if operations[lastindx+1] in ["O"]: #List of the operations that doesn't modify the turbo files, and can thus be done at the same time with others calculations
            nextoperation(path, lastindx+1)



def checktoadvance(csum, wsum):

    global advancement

    for indx in range(len(operations)):
        i = operations[indx]
        for path in advancement["waiting"][i]:
            advancement[i].append(path)
            advancement["waiting"][i].remove(path)
            launch_job(path, i)
            return csum + 1, wsum - 1

    logging.info("Non.")


def check_end():
    sm = sum(i for i in advancement["compteur"].values())
    if sm >= total:
        if subprocess.getoutput(["qstat"]) == "":
            clean_quit()
    return sm


def initlog():
    logging.basicConfig(filename='/home/barres/log.log', level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
    logging.info("__________________________")
    logging.info("Process started")


def initargs():

    global parser, args, turbocheck

    parser = argparse.ArgumentParser(description='SaturnCommand')
    parser.add_argument("file", help='file or directory name (format xyz to be processed)', type=str)
    parser.add_argument("-s", "--shrink", action='store_true', help="remove input spacing")
    parser.add_argument("-c", "--complete", action="store_true", help="customize process")
    parser.add_argument("-t", "--turbo", action="store_true", help="use turbo files")
    parser.add_argument('-create', "--creation_only", action="store_true", help="only creates turbomole files, doesn't qsub them")
    args = parser.parse_args()

    if args.turbo: turbocheck = True

def initcurse():
    global stdscr
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()

def clean_quit():
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    print("")
    print("All files done.")
    logging.info("All files were computed")
    logging.info("__________________________")
    sys.exit(0)


if __name__ == "__main__":

    initargs()
    initlog()

    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        logging.info("Process terminated by user command")
        logging.info("__________________________")
    except Exception as e:
        logging.info(str(e))
        logging.info("__________________________")

    curses.echo()
    curses.nocbreak()
    curses.endwin()
    sys.exit(0)