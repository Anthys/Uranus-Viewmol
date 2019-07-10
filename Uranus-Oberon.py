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


## CONSTANTS
progname = "Uranus-Oberon"
user_input = True
shrink = False
turbocheck = False
spr = "---\n"*5
DEFAULT = "oOfFxX"
texto = {
    "o": "optimisation minimum",
    "O": "top orbitals calculation",
    "f": "force calculations",
    "x": "exited states calculation",
    "X": "panama",
    "F": "frequency input file"
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
stdscr = ""
mx_parallel_calculations = 4
orbitals_per_sym = 5


## GLOBAL VARIABLES
rroot = os.getcwd()
args = ""
parser = ""
operations = ""
name = "alphatest"
advancement = {}
tempstring = []
total = 0
sm = 0
compt = 0
error_compt = 0

def get_input():

    name = ""
    useturbo = 0
    operations = DEFAULT

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
            if operations == "D": operations = DEFAULT
            elif not args.forcing:
                for indx in range(len(operations)):
                    i = operations[indx]
                    if i not in ["o", "f", "O", "x", "X", "F"]:
                        done1 = False
                        print("Wrong character")
                        break
                    elif i in ["O", "f", "x"]:
                        if not useturbo and "o" not in operations[:indx]:
                            input_error+= texto[i].capitalize() + " found without optimal minimum.\n"
                            operations = "o" + operations[:]
                    elif i in ["X"]:
                        if not useturbo and not set(["o", "x"]).issubset(operations[:indx]):
                            operations = "ox" + operations[:]
                    elif i in ["F"]:
                        if not useturbo and "f" not in operations[:indx]:
                            operations = operations[:indx] + "f" + operations[indx:]
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
        #remove_clean_end(path, include=".cub")
        make_command(endcmd="rsync -rva" + " --exclude lost+found --exclude 'MPI-*' --exclude 'NodeFile.*' ${TMPDIR}/ ${SGE_O_WORKDIR}/")
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
        #write_submit("aoforce > aoforce.log")
        make_command(startcmd='aoforce > aoforce.log', endcmd="rsync -rva" + " --exclude lost+found --exclude 'MPI-*' --exclude 'NodeFile.*' " + "${TMPDIR}/" + " ${SGE_O_WORKDIR}/")
        os.system("qsub -N " + name + "_frequency" + " submit.job")
        logging.info("Frequency calculation started in " + path)

    elif operation == "x":
        if "escf.log" in os.listdir():
            os.remove("escf.log")
        write_sym()
        #write_submit("escf > escf.log")
        make_command(startcmd="escf > escf.log", endcmd="rsync -rva escf.log ${SGE_O_WORKDIR}/")
        os.system("qsub -N " + name + "_exited" + " submit.job")
        logging.info("Exited states calculation started in " + path)

    elif operation == "X":
        if not operations == ["X"]:
            copyfile("../" + progname + ".py", "./" + progname + ".py")
        make_command(endcmd="rsync -rva panama_files ${SGE_O_WORKDIR}", startcmd="scl enable rh-python36 'python3 " + progname + ".py -panama panaNone > panama.log'")
        os.system("qsub -N " + name + "_panama" + " submit.job")
        logging.info("Panama calculations started in " + path)

    elif operation == "F":
        logging.info("Creating file molden.input in " + path)
        if "molden.input" in os.listdir():
            os.remove("molden.input")
        subprocess.run("tm2molden", input="\nn\n\nn\n".encode()) #NE MARCHE PAS

def make_command(endcmd="", startcmd=""):
    outputend = ""
    outputstart = ""
    if endcmd:
        rfile = open("submit.job")
        check = False
        for line in rfile:
            if check:
                outputend += line
            elif "###END_COMMANDS" in line:
                check = True
                outputend += line
        rfile.close()

    if startcmd:
        rfile = open("submit.job")
        check = False
        for line in rfile:
            if "###END_COMMANDS" in line:
                check = False
            if check:
                outputstart += line
            elif "###BEGIN_COMMANDS" in line:
                check = True
                outputstart += line
        rfile.close()

    rfile = open("submit.job")
    ftext = rfile.read()
    if startcmd:
        ftext = ftext.replace(outputstart, "###BEGIN_COMMANDS\n" + startcmd + "\n")
    if endcmd:
        ftext = ftext.replace(outputend, "###END_COMMANDS\n" + endcmd + "\n")
    rfile.close()
    wfile = open("submit.job", "w")
    wfile.write(ftext)
    wfile.close()

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
    a.close()
    a = open("control", "w")
    a.write(b)
    a.close()

def remove_clean_end(path, include="", exclude = "", dir=""): #A REMPLACER PAR MAKECOMMAND
    if include:
        include = "*" + include
    os.chdir(path)
    ofile = open("submit.job")
    rfile = ofile.read()
    ofile.close()
    rfile = rfile.replace("#trap 'CleanExit", "#")
    excl = "--exclude lost+found --exclude 'MPI-*' --exclude 'NodeFile.*' " + ("--exclude '*." + exclude + "' " if exclude else "")
    if dir:
        rfile = "rsync -rva panama_files ${SGE_O_WORKDIR}"
    else:
        rfile = rfile.replace("CleanExit", "rsync -rva " + excl + "${TMPDIR}/" + include + " ${SGE_O_WORKDIR}/")
    ofile = open("submit.job")
    ofile.write(rfile)
    ofile.close()

def write_submit(arg): # A REMPLACER PAR MAKECOMMAND
    ffile = open("submit.job")
    fread = ffile.read()
    ffile.close()

    mtc = re.search(r"###BEGIN_COMMANDS\n(.*)\n###END_COMMANDS\n", fread, re.MULTILINE)

    if mtc:
        fread = fread.replace(mtc.group(), "###BEGIN_COMMANDS\n" + arg + "\n###END_COMMANDS\n")

    ffile = open("submit.job", "w")
    ffile.write(fread)
    ffile.close()

def sort_a_file(start_file, end_dir, name=""):
    main_path = "/home/barres/xDatabase"
    if not os.path.isdir(main_path):
        subprocess.run(["mkdir", main_path])
    if not os.path.isdir(main_path + "/" + args.file[:-4]):
        subprocess.run(["mkdir", main_path + "/" +  args.file[:-4]])
    if not os.path.isdir(main_path + "/" + args.file[:-4] + "/" + end_dir):
        subprocess.run(["mkdir", main_path + "/" + args.file[:-4] + "/" + end_dir])
    #os.rename(start_file, main_path + "/" + end_dir + "/" + name)
    copyfile(start_file, main_path + "/" + end_dir + "/" + name)



def checkloop():

    global compt, advancement, tempstring, sm, error_compt
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
                        for j in os.listdir():
                            if ".cub" in j:
                                sort_a_file(j, "top_orbitals")
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

                if i == "X":
                    if "panama_files" in os.listdir():
                        logging.info("Panama files successfully calculated in " + path)
                        advancement[i].remove(path)
                        advancement["compteur"][i] += 1
                        nextoperation(path, indx)

                if i == "F":
                    if "molden.input" in os.listdir():
                        logging.info("File molden.input successfully created in " + path)
                        advancement[i].remove(path)
                        advancement["compteur"][i] += 1
                        nextoperation(path, indx)

        os.chdir(rroot)
        if csum and subprocess.getoutput(["qstat"]) == "":
            if error_compt >2:
                error_compt = 2
            error_compt += 1
        else:
            error_compt = 0
        while csum <= mx_parallel_calculations and wsum>0:
            csum, wsum = checktoadvance(csum, wsum)
        sm = check_end()
        tempstring = []
        for i in operations:
            tempstring+= [texto[i].capitalize() + ": " + str(advancement["compteur"][i]) + "/" + str(len(advancement["all"]))]
    reportprogress(tempstring, sm, total)
    s.enter(1, 1, checkloop)

def reportprogress(progstring, sm, total):
    """progress: 0-10"""
    stdscr.clear()
    stdscr.addstr(0, 0, "Total progress: {0}/{1} [{2:11}]".format(str(sm), str(total), "#" * (compt % 11)))
    for i in range(len(progstring)):
        stdscr.addstr(i + 1, 5, progstring[i])
    if error_compt == 1:
        stdscr.addstr(i + 4, 0, "There may be an error.")
    elif error_compt >= 2:
        stdscr.addstr(i + 4, 0, "An error has occurred.")
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
        if not subprocess.getoutput(["qstat"]) == "":
            print("Error may have occured: Queue is still full")
        clean_quit()
    return sm

def panama_(paper):
    subprocess.run(["mkdir", "panama_files"])
    rep = 1
    paper = "escf.log"
    fobj = open(paper, "r")
    mtc = ""
    cmpt = 0
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
                      os.rename("td.plt", "./panama_files/"  + mtc + "_orb_" + str(cmpt) + ".plt")
                      break
    fobj.close()
    print('ALL FILES DONE')


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
    parser.add_argument("-panama", "--panama", action="store_true", help="DO NOT CALL DIRECTLY, is used for panama calculations")
    parser.add_argument("-force", "--forcing", action="store_true", help="DO NOT CALL, force operations to be processed")
    parser.add_argument("-ns", "--nosort", action="store_true", help="do not sort files and put them in folders")
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

    if args.panama:
        try:
            panama_("escf.log")
        except Exception as e:
            pass
        sys.exit(0)

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