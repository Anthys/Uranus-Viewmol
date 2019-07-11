import matplotlib.pyplot as plt
import math, ast
import os, sys, subprocess, re, argparse


parser = argparse.ArgumentParser(description='Show bonds lengths, default gradient')
args={}

def initarg():
    global parser, args
    parser.add_argument("-p", "--points", action='store_true', help="show atoms labels")
    parser.add_argument("-iwant", type=int, dest="iwant", help="get 0-INDUCEDCURRENT|1-POSITIVE CONTRIBUTION|2-NEGATIVE CONTRIBUTION")
    parser.add_argument("-yz", "--yzaxis", action="store_true", help="represent y-z insntead of x-y")
    parser.add_argument("-xz", "--xzaxis", action="store_true", help="represent x-z insntead of x-y")
    parser.add_argument("-fx", "--flipx", action="store_true", help="flip x axis")
    parser.add_argument("-s", "--save", action="store_true", help="save to pics folder")
    parser.add_argument("-showv", "--showvalues", action="store_true", help="show values")
    parser.add_argument("-wh", nargs=2, dest="size", help="weight and height of figure", type=int)
    args = parser.parse_args()
    return args

def get_matrix_atoms(args):
    ffile = open("coord")
    check = False
    matrix = []
    count=0
    optio = -1 if args.flipx else 1
    for line in ffile:
        if check:
            count+=1
            if line[0]!=" ":
                break
            else:
                ttab=line.split()
                if True:
                    matrix.append([float(ttab[0])*optio, float(ttab[1]), float(ttab[2]), ttab[3], count])
        if "$coord" in line:
            check = True
    ffile.close()
    glob_list = []
    ffile = open("OUTPUT.OUT")
    for line in ffile:
        glob_list.append(ast.literal_eval(line))
    print(glob_list)

    return matrix, glob_list


def draw_things(glob_list, atoms, args):
    dico = ["Induced current", "Positive contribution", "Negative contribution"]
    f_ax = 0
    s_ax = 1
    if args.yzaxis:
        f_ax=1
        s_ax=2
    elif args.xzaxis:
        f_ax=0
        s_ax=2
    wwwant = 2
    if args.iwant:
        wwwant = args.iwant + 2
    for i in glob_list:
        print(i)
        print(len(atoms))
        color = "#0000FF"
        p1 = [atoms[int(i[0])-1][f_ax], atoms[int(i[1])-1][f_ax]]
        p2 = [atoms[int(i[0])-1][s_ax], atoms[int(i[1])-1][s_ax]]
        plt.plot(p1, p2, color)
        midx=(p1[0]+p1[1])/2
        midy=(p2[0]+p2[1])/2
        modif = 1 if float(i[wwwant])>0 else -1
        plt.arrow(midx,midy, (p1[1]-midx)*0.5*modif, (p2[1]-midy)*0.5*modif, head_width=0.3,head_length=0.3, fc='k', ec='k')
        props = dict(boxstyle='round', facecolor='white', alpha=1)
        if args.showvalues:
            plt.text((p1[0]+p1[1])/2-1, (p2[0]+p2[1])/2, i[wwwant], color="black", weight="bold", bbox=props)
    fig.suptitle(dico[wwwant-2], weight="bold")
    fig.canvas.set_window_title(fig.canvas.manager.window.wm_title() + dico[wwwant-2].replace(" ", "_"))

def extract(l):
    l.sort()
    mean = sum(l)/len(l)
    med = l[len(l)//2]
    cv = len(l)//4
    q1=l[cv]
    q3=l[cv*3]
    return mean, med, q1, q3


def get_variation(dir, args):
    os.chdir(dir)
    distlist=[]
    print("Here:")
    print(os.listdir())
    folder1, folder2 = "", ""
    while not folder1 in os.listdir():
        folder1 = input("Initial folder: ")
    while not folder2 in os.listdir():
        folder2 = input("Exited files folder: ")
    os.chdir(folder1)
    matrix1, HAMILT1 = get_matrix_atoms(args)
    os.chdir("../" + folder2)
    matrix2, HAMILT2 = get_matrix_atoms(args)
    OUTPUT = [[0 for i in range(len(HAMILT1))] for i in range(len(HAMILT1))]
    for i in range(len(HAMILT1)):
        for j in range(i, len(HAMILT1)):
            if HAMILT1[i][j]!=0:
                OUTPUT[i][j] = HAMILT2[i][j]-HAMILT1[i][j]
                distlist.append(HAMILT2[i][j]-HAMILT1[i][j])
    mean, med, q1, q3 = extract(distlist)
    fig.canvas.set_window_title("from_" + folder1 + "_to_" + folder2)
    fig.suptitle("Mean: " + str(mean) + " Median: " + str(med))
    os.chdir("../")

if __name__=="__main__":
    try:
        args = initarg()
        if args.size:
            fig = plt.figure(figsize=args.size)
        else:
            fig = plt.figure()
        temp = os.getcwd()
        temp = temp.split("/")
        temp = temp[-1]
        fig.canvas.set_window_title(temp)
        matrix, glob_list = get_matrix_atoms(args)
        draw_things(glob_list, matrix, args)
        if args.save:
            if args.size:
                print(args.size)
            print(fig.canvas.manager.window.wm_title())
            if not "pics" in os.listdir():
                os.system("mkdir pics")
            fig.savefig("pics/" + fig.canvas.manager.window.wm_title())
        else:
            plt.show()
    except Exception as e:
        print(e)
