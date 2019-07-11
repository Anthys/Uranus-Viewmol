import os, argparse

# HARD-CODE
database_directory = "/home/antys/pycalcview/pycalcview/viewmol/static/data/"
# Directory of the database in the local computer, it's where files are searched by the ViewMol website.
remote_dtb_directory = "xDatabase/"
# Location of the database in the cluster, it's where files are sorted and wait for retrieval.
user_files_directory = "/home/antys/pycalcview/pycalcview/viewmol/static/files_from_users"
# Location where the files from users are put.
remote_wrking_directory = "z_calc/to_be_made/"
# Location of the working directory, in the cluster. That's where files are processed. Here, z_calc is the working
# directory, and to_be_made is a temporary directory for files that are waiting to be processed.
ssh_adress = "frontale"
# keyword or adress

args = ""
method = "method"
basis = "basis"
m_and_b = method + "/" + basis

def retrieve():
    os.chdir(database_directory)
    if not os.path.isdir("temp"):
        os.mkdir("temp")
    os.system("scp -r " + ssh_adress + ":" + remote_dtb_directory + "* ./temp/")
    for i in os.listdir("temp"):
        if os.path.isdir(i):
            print("Already exists")
        else:
            os.mkdir(i)
            os.mkdir(i + "/" + method)
            os.mkdir(i + "/"+ m_and_b)
            os.system("mv temp/" + i + "/* " + i + "/" + m_and_b + "/")
            os.system("rm -r temp/" + i)

def send(maxfiles):
    count = 0
    os.chdir(user_files_directory)
    for i in os.listdir():
        if count<maxfiles:
            print("Sending " + i)
            count += 1
            os.system("scp "+ i +" " + ssh_adress + ":" + remote_wrking_directory)
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