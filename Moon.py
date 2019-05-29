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
