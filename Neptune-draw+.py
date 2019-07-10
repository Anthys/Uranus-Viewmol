import os, argparse,re
import matplotlib.pyplot as plt


logfile= ""

parser = argparse.ArgumentParser(description='Show bonds lengths, default gradient')
args={}

def initarg():
    global parser, args
    parser.add_argument("-n", dest="numb", help="number of structure to show")
    parser.add_argument("-p", "--points", action="store_true", help="show labels")
    args = parser.parse_args()
    return args

def make_mol():
    ffile = ""
    for i in os.listdir():
        if i[-4:]==".xyz":
            ffile = i
    if not ffile:
        return
    ffile = open(ffile)
    count = 0
    output = []
    for line in ffile:
        if count>1:
            ttab = line.split()
            output.append([float(ttab[1]), float(ttab[2]), float(ttab[3]), ttab[0], count-1])
        count+=1
    return output

def hamilt_mol():
    global logfile
    namefile= ""
    getter = False
    for i in os.listdir():
        if i[-4:]==".log":
            if namefile:
                getter=True
            namefile = i
    if getter or not namefile:
        print("Here: ")
        print(os.listdir())
        namefile = ""
        while not namefile in os.listdir():
            namefile = input("Namefilelog: ")

    logfile = namefile
    ffile = open(namefile)
    check = False
    HAMILT = []
    for line in ffile:
        if not check and "TOPO matrix for the leading resonance structure:" in line:
            check = True
        if check:
            if "Resonance" in line:
                check = False
                break
            if "Atom" in line:
                labels = line.split()
                count = 0
                for line2 in ffile:
                    if line2.split() == []:
                        break
                    elif not '---' in line2:
                        ttab = line2.split()
                        if len(HAMILT)>count:
                            for i in ttab[2:]:
                                HAMILT[count].append(i)
                        else:
                            HAMILT.append(ttab[2:])
                        count += 1
    for i in HAMILT:print(i)
    print(len(HAMILT))
    return HAMILT

import re


def ajust(args, hamilt):
    ffile = open(logfile)
    check = False
    numb = args.numb
    fig.canvas.set_window_title("N = " + numb)
    fig.suptitle("N = " + numb)
    for line in ffile:
        if "Added(Removed)" in line:
            for line2 in ffile:
                ttab = line2.split()
                if ttab[0].replace("*", "")==numb:
                    ttab = line2.split(",")
                    for i in ttab:
                        mtc = re.search("[^\d]*(\d+)-[^\d]*(\d+)(\)?)",i)
                        if mtc:
                            x = int(mtc.group(1)) - 1
                            y = int(mtc.group(2)) - 1
                            optio = -1 if mtc.group(3) else 1
                            print(x, y, "+1" if optio==1 else optio)
                            hamilt[x][y]= str(int(hamilt[x][y]) + optio)
                    for line3 in ffile:
                        if line3.split()[0].replace("*", "") == str(int(numb)+1):
                            return hamilt
                        else:
                            ttab = line3.split(",")
                            for i in ttab:
                                mtc = re.search("[^\d]*(\d+)-[^\d]*(\d+)(\)?)",i)
                                if mtc:
                                    x = int(mtc.group(1)) - 1
                                    y = int(mtc.group(2)) - 1
                                    optio = -1 if mtc.group(3) else 1
                                    print(x, y, optio)
                                    hamilt[x][y] = str(int(hamilt[x][y]) + optio)



def draw_mol(hamilt, mol, args):
    for i in range(len(hamilt)):
        for j in range(i, len(hamilt)):
            if hamilt[i][j]!="0":
                p1 = [mol[i][0], mol[j][0]]
                p2 = [mol[i][1], mol[j][1]]
                color = "#FFFFFF"
                if hamilt[i][j]=="1":
                    color = "#FFFF00"
                elif hamilt[i][j]=="2":
                    color = "#FF0000"
                plt.plot(p1, p2, color, linewidth=5)
        plt.plot(mol[i][0], mol[i][1], 'ko')
        if args.points:
            plt.text(mol[i][0]+0.2, mol[i][1]+0.2, mol[i][4], color="black")

initarg()
fig = plt.figure()
hamilt = hamilt_mol()
if args.numb:
    hamilt = ajust(args, hamilt)
mol = make_mol()
draw_mol(hamilt, mol, args)

plt.show()