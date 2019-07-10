import os, sys, subprocess, re, argparse


parser = argparse.ArgumentParser(description='SaturnCommand')
args={}

def initarg():
    global parser, args
    parser.add_argument("dir", help='directory name (format xyz to be processed)', type=str)
    parser.add_argument("-o", "--opti", action='store_true', help="optimisation")
    parser.add_argument("-x", "--escf", action="store_true", help="escf")
    parser.add_argument("-ox", "--optix", action="store_true", help='opti_exited')
    parser.add_argument("-p", "--panam", action="store_true", help='panama')
    args = parser.parse_args()

    os.chdir(args.dir)

    if args.opti:
        opti()
    elif args.escf:
        escf()
    elif args.optix:
        optix()
    elif args.panam:
        panam()


def opti():
    ffile = ""
    for i in os.listdir():
        if i[-4:]==".xyz":
            ffile= i
            break
    if ffile:
        os.system("tp -g " + ffile)
        os.system("gtm")
        os.system("qsub submit.job")

def panam():
    curmax = get_best_ex()
    minenerg, maxenerg = curmax[0]-0.001, curmax[0]+0.001
    tstring="2\nescf.log\n1\n" + str(minenerg) + "\n" + str(maxenerg) + "\n"
    subprocess.run("panama", input=tstring.encode())
    panama_to_cub()
    make_command(startcmd="ridft -proper")
    os.system("qsub submit.job")

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
        print("Error in panama_to_cub")

def get_best_ex():
    ffile = open("exspectrum")
    check = False
    curmax = [100, 0]
    for line in ffile:
        if not check and line[0] != "#":
            check = True
        if check:
            if line[0] == "#":
                break
            else:
                ttab = line.split()
                if float(ttab[3]) < curmax[0]:
                    curmax[0] = float(ttab[3])
                    curmax[1] = ttab[1]
    ffile.close()
    return curmax

def optix():
    curmax = get_best_ex()

    ffile=open("control")
    output=""
    check = True
    for line in ffile:
        if not check and line[0]!=" ":
            check=True
        if "$soes" in line:
            output+=line
            output+= " " + curmax[1] + "    1\n"
            check = False
        if check:
            output+= line
    ffile.close()
    ffile=open("control", "w+")
    ffile.write(output)
    ffile.close()
    make_command(startcmd="jobex -c 100 -ex")
    os.system("qsub submit.job")


def escf():
    ffile = open("control")
    check = False
    output = ""
    for line in ffile:
        if '$closed shells' in line:
            check=True
        elif check:
            if line[0] != " ":
                check=False
                break
            else:
                ttab = line.split()
                output += " " + ttab[0] + "     1" + "\n"
    ffile.close()
    ffile = open("control", "r")
    rfile = ffile.read()
    tstring = "$scfinstab rpas \n$soes\n" + output + "$denconv 1d-7\n$end\n"
    rfile = rfile.replace("$end", tstring)
    ffile.close()
    ffile = open("control", "w")
    ffile.write(rfile)
    ffile.close()
    make_command(startcmd="escf > escf.log")
    os.system("qsub submit.job")


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

initarg()