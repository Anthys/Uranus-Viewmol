import os, argparse

database_directory = "/home/antys/pycalcview/pycalcview/viewmol/static/data/"
remote_dtb_directory = "xDatabase/"
user_files_directory = "/home/antys/pycalcview/pycalcview/viewmol/static/files_from_users"
remote_wrking_directory = "z_calc/to_be_made/"
args = ""

def retrieve():
    os.chdir(database_directory)
    if not os.path.isdir("temp"):
        os.mkdir("temp")
    os.system("scp -r frontale:" + remote_dtb_directory + "* ./temp/")
    for i in os.listdir("temp"):
        if os.path.isdir(i):
            print("Already exists")
        else:
            os.mkdir(i)
            os.mkdir(i + "/method")
            os.mkdir(i + "/method/basis")
            os.system("mv temp/" + i + "/* " + i + "/method/basis/")
            os.system("rm -r temp/" + i)

def send(maxfiles):
    count = 0
    os.chdir(user_files_directory)
    for i in os.listdir():
        if count<maxfiles:
            print("Sending " + i)
            count += 1
            os.system("scp "+ i +" frontale:" + remote_wrking_directory)
            os.system("rm " + i)

def init_args():
    global args
    parser = argparse.ArgumentParser(description='SaturnCommand')
    parser.add_argument("-s", dest="send", help="Send given number of files to cluster", type=int)
    parser.add_argument("-r", "--retrieve", action="store_true", help="Get files from remote database")
    args = parser.parse_args()

if __name__=="__main__":
    init_args()
    try:
        if args.send:
            send(args.send)
        if args.retrieve:
            retrieve()
    except Exception as e:
        print(e)