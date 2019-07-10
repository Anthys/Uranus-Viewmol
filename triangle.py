def every_numb(l):
    for i in l:
        if not is_numb(i):
            return False
    return True

def is_numb(n):
    try:
        a = int(n)
    except Exception as e:
        print(e)
        return False
    else:
        return True

def main():
    numb_cycl = ""
    while not (numb_cycl and is_numb(numb_cycl)):
        numb_cycl = input("Number of cycles: ")
    numb_cycl = int(numb_cycl)
    final = []
    for i in range(numb_cycl):
        super = ""
        while not (len(super.split())==3 and every_numb(super.split())):
            super = input("Atoms indx: (Ex: 1 2 3): ")
        print("Done")
        final.append([int(i)-1 for i in super.split()])

    ffile = open("coord")
    atoms = []
    compt = 0
    for line in ffile:
        if compt!=0:
            if line[0]!=" ":
                break
            ttab = line.split()
            atoms.append([float(ttab[0]), float(ttab[1]), float(ttab[2])])
        compt+=1
    ffile.close()
    output = []
    for set_at in final:
        x=0
        for i in range(3):
            x += atoms[set_at[i]][0]
        x=x/3
        y = 0
        for i in range(3):
            y += atoms[set_at[i]][1]
        y = y / 3
        z = 0
        for i in range(3):
            z += atoms[set_at[i]][2]
        z = z / 3
        output.append([x, y, z])
    ffile = open("coord")
    replace = ""
    for line in ffile:
        if "$redundant" in line:
            for i in output:
                replace += "    " + str(i[0]) + "   " + str(i[1]) + "   " + str(i[2]) + "  q\n"
        replace+=line
    ffile.close()
    ffile=open("coord", "w+")
    ffile.write(replace)
    ffile.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)