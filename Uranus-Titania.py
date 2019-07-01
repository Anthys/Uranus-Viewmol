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
progname = "Uranus-Titania"
loc_mypanama = "/home/barres/mypanama"
dir_spyctrum = "/home/barres/spyctrum/spyctrum/spyctrum.py"
user_input = True
shrink = False
panaplot = True
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
    "c1": ["a"],
    "c2": ["a", "b"]
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
wrking = False #If function is called in the cluster, is set to True
visu = True

def get_input():

    if wrking:
        operations = []
        for i in args.operations:
            operations += [i]
        return operations, ("all_files" if not args.name else args.name), False

    if args.operations and args.name:
        operations = []
        for i in args.operations:
            operations += [i]
        return operations, ("all_files" if not args.name else args.name), False

    name = ""
    if args.name:
        name = args.name
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
                    if i not in ["o", "f", "O", "x", "X", "F", "$", "£"]:
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
                        if operations[indx+1:]:
                            operations = operations.replace("X", "")
                            operations += "X"
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
    try:
        pass
        #subprocess.run("define", input=b'\ny\ndesy 1\n*\nno\n\n*\n\n*\n') #GET BETTER SYMMETRY
    except Exception as e:
        subprocess.run(["tp", "-g", xyz])
    logging.info("Turbo file created for " + xyz)
    os.chdir(rroot)
    return rwork

def main():

    global compt, shrink, rroot, name, operations, advancement, total

    if not is_valid(args.file): quit()

    shrink = (True if args.shrink else False)

    operations, name, useturbo = get_input()

    logging.info('Operations chosen: ' + str(operations))

    if args.away: #FOR THE MOMENT DOESNT CONSIDER FOLDER OF FILES
        operations = "".join(operations)
        os.system("gtm")
        make_command(startcmd="scl enable rh-python36 'python3 " + progname + ".py -o " + operations + " -n " + name + " -nosub " + args.file + " > superNone.log'", endcmd="rsync -rva" + " --exclude lost+found --exclude 'MPI-*' --exclude 'NodeFile.*' ${TMPDIR}/ ${SGE_O_WORKDIR}/")
        os.system("qsub -N " + name + "_global" + " submit.job")
        logging.info("Files all sent to cluster.")
        sys.exit(0)

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


    if not wrking:
        if visu:
            initcurse()
        s.enter(0, 1, checkloop)
        s.run()
    else:
        for path in advancement["all"]:
            for i in operations:
                launch_job(path, i)
                logging.info('Remote, ' + i  + " done in "+ path)


def launch_job(path, operation):

    os.chdir(path)
    
    if operation == 'o':
        os.system("gtm")
        time.sleep(0.1)
        if wrking:
            os.system("jobex -c 100")
        else:
            os.system("qsub -N " + name + "_minimum" + " submit.job")
        logging.info("Optimisation minimum started in " + path)

    elif operation == "O":
        os.system("gtm")
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
        for orbicur in [mx_orbital, str(int(mx_orbital)+1)]:
            o_file = open("control")
            r_file = o_file.read()
            o_file.close()
            if not "$pointval" in r_file:
                r_file = r_file.replace("$end", "$pointval fmt=cub mo " + orbicur + "\n$end")
            else:
                mtc = re.search("\$pointval.*\n", r_file)
                r_file = r_file.replace(mtc.group(), "$pointval fmt=cub mo " + orbicur + "\n")
            o_file = open("control", "w")
            o_file.write(r_file)
            o_file.close()

            if wrking:
                os.system("jobex -c 100")
                #THIS IS NOT IN THE NON-AWAY VERSION BECAUSE IM LAZY
                for i in os.listdir():
                    if i[-4:]==".cub":
                        os.system("mv " + i + " " + ('homo.cube' if orbicur == mx_orbital else "lumo.cube"))
            else:
                make_command(endcmd="rsync -rva" + " --exclude lost+found --exclude 'MPI-*' --exclude 'NodeFile.*' ${TMPDIR}/ ${SGE_O_WORKDIR}/")
                os.system("qsub -N " + name + "_orbitals" + " submit.job")
            logging.info("Orbital calculation started in " + path)
    
    elif operation == "f":
        if "aoforce.log" in os.listdir():
            os.remove("aoforce.log")
        if wrking:
            os.system("aoforce > aoforce.log")
        else:
            make_command(startcmd='aoforce > aoforce.log', endcmd="rsync -rva" + " --exclude lost+found --exclude 'MPI-*' --exclude 'NodeFile.*' " + "${TMPDIR}/" + " ${SGE_O_WORKDIR}/")
            os.system("qsub -N " + name + "_frequency" + " submit.job")
        logging.info("Frequency calculation started in " + path)

    elif operation == "x":
        if "escf.log" in os.listdir():
            os.remove("escf.log")
        write_sym()
        if wrking:
            os.system("escf > escf.log")
        else:
            make_command(startcmd="escf > escf.log", endcmd="rsync -rva escf.log ${SGE_O_WORKDIR}/")
            os.system("qsub -N " + name + "_exited" + " submit.job")
        logging.info("Exited states calculation started in " + path)

    elif operation == "X":
        if not operations == ["X"]:
            copyfile("../" + progname + ".py", "./" + progname + ".py")
        if wrking:
            panama_("paper")
        else:
            make_command(endcmd="rsync -rva panama_files ${SGE_O_WORKDIR}",startcmd="scl enable rh-python36 'python3 " + progname + ".py -panama panaNone > panama.log'")
            os.system("qsub -N " + name + "_panama" + " submit.job")
        logging.info("Panama calculations started in " + path)

    elif operation == "F":
        logging.info("Creating file molden.input in " + path)
        if "molden.input" in os.listdir():
            os.remove("molden.input")
        subprocess.run("tm2molden", input="\nn\n\nn\n".encode()) #Seems to work
        subprocess.run("tm2molden", input="mos.in\ny\nn\nn\n".encode())
        cut_mos_in()

    elif operation == "$":
        os.system("touch test.tset")

    elif operation == "£":
        os.system("touch test2.tset")

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

def sort_a_file(start_file, end_dir = "", name=""):
    main_path = "/home/barres/xDatabase"
    main_path_list = [i for i in main_path.split("/")]
    main_path_list = []
    for i in range(len(main_path_list)):
        tdir = "/" + "/".join(main_path_list)
        if not os.path.isdir(tdir):
            subprocess.run(["mkdir", tdir])
    if not os.path.isdir(main_path):
        subprocess.run(["mkdir", main_path])
    if not os.path.isdir(main_path + "/" + args.file[:-4]):
        subprocess.run(["mkdir", main_path + "/" +  args.file[:-4]])
    if end_dir and not os.path.isdir(main_path + "/" + args.file[:-4] + "/" + end_dir):
        subprocess.run(["mkdir", main_path + "/" + args.file[:-4] + "/" + end_dir])
    #os.rename(start_file, main_path + "/" + end_dir + "/" + name)
    print("---")
    print(start_file)
    print(main_path + "/" + args.file[:-4] + "/" + (end_dir + "/" if end_dir else "") + name)
    if start_file == "panama_files":
        os.system("cp -r panama_files " + main_path + "/" + args.file[:-4] + "/" + (end_dir + "/" if end_dir else ""))
        return
    if args.forcing or not (name if name else start_file) in os.listdir(main_path + "/" + args.file[:-4] + "/" + (end_dir + "/" if end_dir else "")):
        copyfile(start_file, main_path + "/" + args.file[:-4] + "/" + (end_dir + "/" if end_dir else "") + (name if name else start_file))
    else:
        print('File exists')

def cleaner(path):
    os.chdir(path)
    if "escf.log" in os.listdir(): os.system("python "+ dir_spyctrum + " -t escf.log -m convolution -l 1 1000") #Sale
    thedict = {"aoforce.log":"aoforce.log", "molden.input":"freq.in", "mos.in":"mos.in", "mos_cut.in": "mos_cut.in", "exspectrum":"exspectrum"}
    for i in os.listdir():
        print(i)
        if i in ["aoforce.log","molden.input", "mos.in", "geom.in", "mos_cut.in", "exspectrum"]:
            sort_a_file(i, name=thedict[i])
        if i == "escf.log":
            sort_a_file(i, "exited_orbitals")
        if i == "panama_files":
            sort_a_file(i)
        if len(i)>5:
            if i[-4:] == ".cub":
                sort_a_file(i, name=i+"e")
            if i[-5:] == ".cube":
                sort_a_file(i)
            if i[-4:] == ".xyz":
                if i == "coord.xyz":
                    sort_a_file(i, name="geom.xyz")
                else:
                    sort_a_file(i, "geometry")
            if i[-5:] == ".plot":
                if i == "absorption.plot":
                    sort_a_file(i)
                else:
                    sort_a_file(i, "spectra")
            if i[-4:] == ".csv":
                sort_a_file(i)
    os.chdir("../")

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
    if visu:
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
    if not wrking: print("")
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
            if not wrking: print("Error may have occured: Queue is still full")
        clean_quit()
    return sm

def panama_(paper):
    def panama_to_cub():
        ffile = open("control")
        rfile = ffile.read()
        ffile.close()
        mtc = re.search("\$pointval.*\n", rfile)
        if mtc:
            rfile = rfile.replace(mtc.group(), "$pointval fmt=cub\n")
            ffile = open("control", "w")
            ffile.write(rfile)
            ffile.close()
        else:
            logging.info("Error in panama_to_cub")

    subprocess.run(["mkdir", "panama_files"])
    rep = 1
    paper = "escf.log"
    fobj = open(paper, "r")
    mtc = ""
    cmpt = 0
    for line in fobj:
      if "I R R E P" in line:
          cmpt = 0
          mtc = re.search("I R R E P[ ]*([0-9a-z\"\']+)[ ]*", line)
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
                      subprocess.run(loc_mypanama, input=tempstr.encode())
                      panama_to_cub()
                      subprocess.run(["dscf", "-proper"])
                      os.rename("td.cub", "./panama_files/"  + mtc + "_orb_" + str(cmpt) + ".cub")
                      break
    fobj.close()
    if panaplot:
        subprocess.run("panama", input=b"1\nescf.log\n\n\n\n0.3\n\n")
        ffile = open("data.plot")
        A = 10 ** 9
        H = 6.6260693 * (10 ** (-34))
        C = 299792458
        E = 1.60217653 * (10 ** (-19))

        def make_x_y():
            x = []
            y = []
            for line in ffile:
                line = line.replace("\n", "")
                line = line.split()
                x += [float(line[0])]
                y += [float(line[1])]
            return x, y
        x, y = make_x_y()
        for i in range(len(x)):
            x[i] = A * H * C / (E * x[i])
            x[i] = round(x[i], 1)
        x.reverse()
        y.reverse()
        ffile.close()
        ffile = open("absorption.plot", "w+")
        ffile.write(str(x) + "\n" + str(y))
        ffile.close()
    else:
        #os.system("python " + dir_spyctrum + " -t escf.log -m convolution -l 1 1000") JE SUIS QUASI SUR QUE CA FONCTIONNERA PAS, LA SOLUTION SALE EST AU DEBUT DE CLEANER
        pass

    if not wrking: print('ALL FILES DONE')

def cut_mos_in():
    plus_or_min = 10
    ffile = open("mos.in")
    numb_line_middle = 0
    compt_line = 0
    the_lines = ["", ""]
    the_number = 0
    output = ""
    for line in ffile:
        mtc = re.search("[ ]*Sym=", line)
        if mtc:
            compt_line += 1
        if compt_line < 1:
            output += line
        elif compt_line >1:
                mtc2 = re.search("[ ]*(\d*)[ ]", the_lines[0])
                if mtc2:
                    the_number = int(mtc2.group(1))+5
                break
        the_lines.append(line)
        the_lines.pop(0)
    compt_line=0
    ffile.close()
    ffile = open("mos.in")
    for line in ffile:
        numb_line_middle+=1
        mtc = re.search("Occup=[ ]*((-)?(\d)?\.\d+(E[+-]\d*)?)", line)
        if mtc:
            numb = mtc.group(1)
            numb =float(numb)
            if numb == 0.0:
                numb_line_middle-=3
                break
    ffile.close()
    ffile = open("mos.in")
    for line in ffile:
        compt_line += 1
        if compt_line >= numb_line_middle - (plus_or_min*the_number) and compt_line < numb_line_middle + plus_or_min*the_number:
            output += line
        elif compt_line >= numb_line_middle + plus_or_min*the_number:
            break
    ffile.close()
    ffile = open("mos_cut.in", "w+")
    ffile.write(output)
    ffile.close()


def initlog():
    logging.basicConfig(filename='/home/barres/log.log', level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
    logging.info("__________________________")
    logging.info("Process started" + (" in cluster" if wrking else ""))


def initargs():

    global parser, args, turbocheck, wrking, visu

    parser = argparse.ArgumentParser(description='SaturnCommand')
    parser.add_argument("file", help='file or directory name (format xyz to be processed)', type=str)
    parser.add_argument("-s", "--shrink", action='store_true', help="remove input spacing")
    parser.add_argument("-c", "--complete", action="store_true", help="customize process")
    parser.add_argument("-t", "--turbo", action="store_true", help="use turbo files")
    parser.add_argument('-create', "--creation_only", action="store_true", help="only creates turbomole files, doesn't qsub them")
    parser.add_argument("-panama", "--panama", action="store_true", help="DO NOT CALL DIRECTLY, is used for panama calculations")
    parser.add_argument("-force", "--forcing", action="store_true", help="DO NOT CALL, force operations to be processed")
    parser.add_argument("-ns", "--nosort", action="store_true", help="do not sort files and put them in folders")
    parser.add_argument("-o", dest="operations", help="DO NOT CALL, decides which operations to use")
    parser.add_argument("-away", "--away", action="store_true", help="All the operations will be called in the cluster. No feedback can be given, but the process can continue without interuption.")
    parser.add_argument("-n", dest="name", help="Give a name for remote operations. Usually, do not call.")
    parser.add_argument("-clean", '--clean', help="Just clean files", action="store_true")
    parser.add_argument("-nosub", '--nosub', help="make all calculations on the computer where the program is launched", action="store_true")
    parser.add_argument("-novisu", '--novisu', help="no visual", action="store_true")
    args = parser.parse_args()

    if args.turbo: turbocheck = True
    if args.nosub: wrking = True
    if args.novisu: visu = False


def initcurse():
    global stdscr
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()


def clean_quit():

    curses.echo()
    curses.nocbreak()
    curses.endwin()
    if not wrking:
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

    elif args.clean:
        for i in os.listdir():
            if os.path.isdir(i):
                try:
                    cleaner(i)
                except Exception as e:
                    logging.info(e)
        sys.exit(0)

    try:
        main()
    except KeyboardInterrupt:
        if not wrking: print("Interrupted")
        logging.info("Process terminated by user command")
        logging.info("__________________________")
    except Exception as e:
        logging.info(str(e))
        logging.info("__________________________")

    if wrking or not visu:
        sys.exit(0)

    curses.echo()
    curses.nocbreak()
    curses.endwin()
    sys.exit(0)