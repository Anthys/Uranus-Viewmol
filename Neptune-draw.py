import matplotlib.pyplot as plt
import math
import os, sys, subprocess, re, argparse


parser = argparse.ArgumentParser(description='Show bonds lengths, default gradient')
args={}

def initarg():
    global parser, args
    parser.add_argument("-p", "--points", action='store_true', help="show atoms labels")
    parser.add_argument("-diff", dest="diff", help="difference between two molecules, default binary")
    parser.add_argument("-g", "--gradient", action='store_true', help="gradient")
    parser.add_argument("-b", "--binary", action='store_true', help="binary")
    parser.add_argument("-yz", "--yzaxis", action="store_true", help="represent y-z insntead of x-y")
    parser.add_argument("-xz", "--xzaxis", action="store_true", help="represent x-z insntead of x-y")
    args = parser.parse_args()
    return args

def get_matrix_atoms():
    ffile = open("coord")
    check = False
    matrix = []
    distlist=[]
    count=0
    for line in ffile:
        if check:
            count+=1
            if line[0]!=" ":
                break
            else:
                ttab=line.split()
                if ttab[3]=="c":
                    matrix.append([float(ttab[0]), float(ttab[1]), float(ttab[2]), ttab[3], count])
        if "$coord" in line:
            check = True
    ffile.close()
    HAMILT = [[0 for i in range(len(matrix))] for i in range(len(matrix))]

    for i in range(len(matrix)):
        for j in range(len(matrix)):
            dist = math.sqrt((matrix[j][0]-matrix[i][0])**2+(matrix[j][1]-matrix[i][1])**2+(matrix[j][2]-matrix[i][2])**2)
            if i!=j and 0<dist<2.9:
                HAMILT[i][j]=dist
                distlist.append(dist)

    for i in range(len(HAMILT)):
        print(HAMILT[i])

    return matrix, HAMILT, distlist

def draw_atoms(matrix, HAMILT, args, q1, q3, diff=False):

    for i in range(len(HAMILT)):
        for j in range(i, len(HAMILT[i])):
            if HAMILT[i][j]!=0:
                if args.yzaxis:
                    p1 = [matrix[i][1], matrix[j][1]]
                    p2 = [matrix[i][2], matrix[j][2]]
                elif args.xzaxis:
                    p1 = [matrix[i][0], matrix[j][0]]
                    p2 = [matrix[i][2], matrix[j][2]]
                else:
                    p1 = [matrix[i][0], matrix[j][0]]
                    p2 = [matrix[i][1], matrix[j][1]]
                if args.gradient or not diff:
                    if HAMILT[i][j]<=q1:
                        color = "#FFFF00"
                    elif HAMILT[i][j]>=q3:
                        color = "#FF0000"
                    else:
                        color = "#FFA500"
                else:
                    if HAMILT[i][j]<0:
                        color="#0000FF"
                    else:
                        color="#FF0000"
                plt.plot(p1, p2, color, linewidth=5)


    for i in range(len(matrix)):
        print(matrix[i][0], matrix[i][1])
        if args.yzaxis:
            p1 = matrix[i][1]
            p2 = matrix[i][2]
        elif args.xzaxis:
            p1 = matrix[i][0]
            p2 = matrix[i][2]
        else:
            p1 = matrix[i][0]
            p2 = matrix[i][1]
        plt.plot(p1, p2, 'ko')
        if args.points:
            plt.text(p1+0.2, p2+0.2, matrix[i][4], color="black")

def extract(l):
    l.sort()
    mean = sum(l)/len(l)
    med = l[len(l)//2]
    cv = len(l)//4
    q1=l[cv]
    q3=l[cv*3]
    return mean, med, q1, q3


def get_variation(dir):
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
    matrix1, HAMILT1, distlist1 = get_matrix_atoms()
    os.chdir("../" + folder2)
    matrix2, HAMILT2, distlist2 = get_matrix_atoms()
    OUTPUT = [[0 for i in range(len(HAMILT1))] for i in range(len(HAMILT1))]
    for i in range(len(HAMILT1)):
        for j in range(i, len(HAMILT1)):
            if HAMILT1[i][j]!=0:
                OUTPUT[i][j] = HAMILT2[i][j]-HAMILT1[i][j]
                distlist.append(HAMILT2[i][j]-HAMILT1[i][j])
    mean, med, q1, q3 = extract(distlist)
    draw_atoms(matrix1, OUTPUT, args, q1, q3, diff=True)
    fig.suptitle("Mean: " + str(mean) + " Median: " + str(med))


if __name__=="__main__":
    try:
        args = initarg()
        fig = plt.figure()
        temp = os.getcwd()
        temp = temp.split("/")
        temp = temp[-1]
        fig.canvas.set_window_title(temp)
        if args.diff:
            get_variation(args.diff)
            plt.show()
        else:
            matrix, HAMILT, distlist = get_matrix_atoms()
            mean, med, q1, q3 = extract(distlist)
            print("yes")
            print(mean, med, q1, q3)
            draw_atoms(matrix, HAMILT, args, q1, q3)
            fig.suptitle("Mean: " + str(mean) + " Median: " + str(med))
            plt.show()
    except Exception as e:
        print(e)
