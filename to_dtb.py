import os, argparse

# HARD-CODE
main_directory = "/home/barres/z_calc/"
# Working directory, in the cluster. Where calculations are processed.
database_directory = "/home/barres/xDatabase"
# Database directory, in the cluster. Where files are put when processes are finished.
name_program = "Uranus-Titania"
# Name of the python program to call to process files.


and_remove = False
args = ""


def main():
    for i in os.listdir(main_directory):
        can_sort = False
        name_file = ""
        if os.path.isdir(main_directory + i) and i not in ["to_be_made", "ERRORS"]:
            os.chdir(main_directory + i)
            for j in os.listdir():
                if os.path.isdir(j):
                    can_sort=True
                if j[-4:] == '.xyz':
                    name_file=j
            if name_file and can_sort:
                print(name_file)
                os.system("python ../" + name_program + ".py " + name_file + " -clean")
                if and_remove:
                    os.chdir(main_directory)
                    os.system("rm -r " + i)


def make(maxfiles):
    os.chdir(main_directory)
    count = 0
    for i in os.listdir("to_be_made"):
        if os.path.isfile("to_be_made/" + i) and not os.path.isdir(i[:-4]) and count<maxfiles:
            count += 1
            n_folder = i[:-4]
            os.mkdir(n_folder)
            os.system("mv to_be_made/" + i + " " + n_folder + "/")
            os.system("cp " + name_program  + ".py " + n_folder + "/")
            os.chdir(n_folder)
            os.system("python " + name_program + ".py " + i + " -away -n " + n_folder)
            os.chdir('../')


def init_args():
    global args
    parser = argparse.ArgumentParser(description='SaturnCommand')
    parser.add_argument("-p", dest="process", help="process given number of waiting files", type=int)
    parser.add_argument("-s", "--sort", action="store_true", help="Sort finished files in database")
    args = parser.parse_args()


if __name__ == "__main__":
    init_args()
    try:
        if args.process:
            make(args.process)
        elif args.sort:
            main()
    except Exception as e:
        print(e)