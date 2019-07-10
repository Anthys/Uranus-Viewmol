"""
print(1)
a = input()
print(2)
print(a)
b = input()
print(3)
print(b)
"""
"""
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


make_command(endcmd="rsync -rva panama_files ${SGE_O_WORKDIR}", startcmd="scl enable rh-python36 'python3 Moon.py > Moon.log'")
"""

def giveexener(fescfout):
    output = ""
    rep = 1
    fescfout = "escf.log"
    fobj = open(fescfout, "r")
    for line in fobj:
      if "I R R E P" in line:
          output += line[30:47]
      if "Excitation energy / eV:" in line:
            energ = line[40:48]
            for line2 in fobj:
                if rep == 1:
                   if "velocity representation:" in line2:
                      osc = line2[40:65]
                      output += energ + " " + osc
                      break
                if rep == 2:
                   if "length representation:" in line2:
                      osc = line2[40:65]
                      output += energ + " " + osc
                      break
                if rep == 3:
                   if "mixed representation:" in line2:
                      osc = line2[40:65]
                      output += energ + " " + osc
                      break
    fobj.close() #close escf.out file
    fobj = open("exited.file", "w")
    fobj.write(output)
    fobj.close()

def panama_(paper):
    subprocess.run(["mkdir", "panama_files"])
    rep = 1
    paper = "escf.log"
    fobj = open(paper, "r")
    mtc = ""
    cmpt = 0
    orbitals_per_sym = 5
    for line in fobj:
      if "I R R E P" in line:
          cmpt = 0
          mtc = re.search("I R R E P[ ]*([0-9a-z\"\']+)[ ]*", line)
          mtc = mtc.group(1)
      if "Excitation energy / eV:" in line and cmpt<orbitals_per_sym:
            cmpt += 1
            energ = line[40:48]
            for line2 in fobj:
                if rep == 1:
                   if "velocity representation:" in line2:
                      osc = line2[40:65]
                      osc = int(osc)
                      energ = int(energ)
                      minenerg = energ - 0.0001
                      maxenerg = energ + 0.0001
                      tempstr = "2\nescf.log\n1\n" + str(minenerg) + "\n" + str(maxenerg) + "\n"
                      subprocess.run("panama", input=tempstr.encode())
                      subprocess.run(["dscf", "-proper"])
                      os.rename("td.plt", "./panama_files/"  + mtc + "_orb_" + str(cmpt))
                      break
    fobj.close()
    print('ALL FILES DONE')

print(set(["a", "c"]).issubset("anfcoafj"))