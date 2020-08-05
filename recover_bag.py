'''
This script saves each topic in a bagfile as a csv.

Accepts a filename as an optional argument. Operates on all bagfiles in current directory if no argument provided

Written by Nick Speal in May 2013 at McGill University's Aerospace Mechatronics Laboratory
www.speal.ca

Supervised by Professor Inna Sharf, Professor Meyer Nahon 

Edited by PandaPilot to post-process data
'''

import rosbag, sys, csv
import time
import string
import numpy as np
import os #for file management make directory
import shutil #for file management, copy file

#verify correct input arguments: 1 or 2
if (len(sys.argv) > 2):
    print ("invalid number of arguments:   " + str(len(sys.argv)))
    print ("should be 2: 'bag2csv.py' and 'bagName'")
    print ("or just 1  : 'bag2csv.py'")
    sys.exit(1)
elif (len(sys.argv) == 2):
    listOfBagFiles = [sys.argv[1]]
    numberOfFiles = "1"
    print ("reading only 1 bagfile: " + str(listOfBagFiles[0]))
elif (len(sys.argv) == 1):   
    listOfFolders = [x[0] for x in os.walk(".") if x[0][2:6] == "test"]
else:
    print ("bad argument(s): " + str(sys.argv))	#shouldnt really come up
    sys.exit(1)
listOfBagfile=[]
for bagfiles in range(len(listOfFolders)):
    listOfBagfile=([f for f in os.listdir(listOfFolders[bagfiles]) if f[-4:] == ".bag"])	#get list of only bag files in current dir.
    
    shutil.copyfile(listOfFolders[bagfiles] + '/' + listOfBagfile[0], listOfBagfile[0])

    



count = 0

#for bagFile in listOfBagFiles:
#    count += 1
#    print ("reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile)
#    #access bag
#    bag = rosbag.Bag(bagFile)
#    bagContents = bag.read_messages()
#    bagName = bag.filename


#print ("Done recovering all " + numberOfFiles + " bag files.")
