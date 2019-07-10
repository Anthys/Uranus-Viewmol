import os.path
import subprocess
import re
import time
"""
a = input("Enter thing: ")
print(a)
print("--\n--"*5)
"""

a = open("Sun").read()

time1 = ""
time2 = ""
unit1 = " "
unit2 = " "

units = {"s":1, "min":60, "h":60*60, "":""}

while not unit1 in units.keys():
    unit1 = input("Enter maximum time unit (default s, min or h):")

if unit1 == "": unit1 = "s"

while True:
    try: time1 = float(input("Enter maximum time allowed for iterations (in {0}): ".format(unit1)))
    except ValueError: continue
    else: break

while not unit2 in units.keys():
    unit2 = input("Enter ?? time unit (default s, min or h):")

while True:
    try: time2 = float(input("Enter maximum time allowed for iterations (in {0}): ".format(unit2)))
    except ValueError: continue
    else: break

if unit1 == "": unit1 = "s"
if unit2 == "": unit2 = "s"

time1 = time.strftime('%H:%M:%S', time.gmtime(time1*units[unit1]))
time2 = time.strftime('%H:%M:%S', time.gmtime(time2*units[unit2]))

a = a.replace("h_cpu=hh:mm:ss", "h_cpu="+time1)
a = a.replace("s_cpu=hh:mm:ss", "s_cpu="+time2)
print(a)