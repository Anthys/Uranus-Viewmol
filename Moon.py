"""
import logging
import os
import re

path = os.getcwd()
try:
    tfile = open("job.last")
except Exception as e:
    logging.info("Error in " + path + " -- " + str(e))
else: pass
tread = tfile.read()
tfile.close()
match = re.search('number of occupied orbitals :[ ]*([0-9]*)', tread)
mx_orbital = 0
if match:
    mx_orbital = match.group(1)
    print(mx_orbital)
else:
    logging.info("Error in " + path + " -- No occupied orbitals found in submit.job")
"""
import sched
import time
import curses
import sys
s = sched.scheduler(time.time, time.sleep)


sm = 1
total = 2
compt = 0
progstring = ["test", "test2"]

def checkloop():
    report_progress(progstring)
    s.enter(1, 1, checkloop)

def report_progress(progstring):
    global compt
    compt += 1
    """progress: 0-10"""
    stdscr.addstr(0, 0, "Total progress: {0}/{1} [{2:11}]".format(str(sm), str(total),"#" * (compt%11)))
    for i in range(len(progstring)):
        stdscr.addstr(i+1, 5, progstring[i])
    stdscr.refresh()

if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    s.enter(0, 1, checkloop)
    s.run()
    """
    try:
        for i in range(10):
            report_progress("file_{0}.txt".format(i), i+1)
            time.sleep(1)
    finally:
        curses.echo()
        curses.nocbreak()
        curses.endwin()
    """