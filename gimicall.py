import sys, re, os, time, subprocess

def main():
    all_comb = []
    ffile = open("input.txt")
    for line in ffile:
        if line[0] != "#":
            ttab = line.split()
            all_comb.append([ttab[0], ttab[1]])
    ffile.close()
    print(all_comb)
    for comb in all_comb:
        ffile = open("gimic.inp")
        rfile = ffile.read()
        ffile.close()
        mtc = re.search(" bond=\[\d+,\d+\]", rfile)
        if mtc:
            print(mtc.group())
            rfile = rfile.replace(mtc.group(), " bond=[" + comb[0] + "," + comb[1] + "]")
        ffile = open("gimic.inp", "w+")
        ffile.write(rfile)
        ffile.close()
        os.system("gimic > gimic.out")
        print("Done.")
        ffile=open("gimic.out")
        check = False
        output = [comb[0], comb[1]]
        for line in ffile:
            if "Magnetic field <x,y,z>" in line:
                check = True
            if check:
                if "Induced current (au)" in line:
                    output.append(get_float(line))
                if "Positive contribution" in line:
                    output.append(get_float(line))
                if "Negative contribution" in line:
                    output.append(get_float(line))
                    break
        ffile.close()
        ffile=open("OUTPUT.OUT", "a+")
        ffile.write(str(output) + "\n")
        ffile.close()

def get_float(line):
    mtc = re.search("-?\d+\.\d+", line)
    if mtc:
        return mtc.group()
    else:
        return "NOTHING"

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)