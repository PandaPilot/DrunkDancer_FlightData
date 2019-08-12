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
    listOfBagFiles = [f for f in os.listdir(".") if f[-4:] == ".bag"]	#get list of only bag files in current dir.
    numberOfFiles = str(len(listOfBagFiles))
    print ("reading all " + numberOfFiles + " bagfiles in current directory: \n")
    for f in listOfBagFiles:
        print (f)
    print ("\n press ctrl+c in the next 0 seconds to cancel \n")
    time.sleep(0)
else:
    print ("bad argument(s): " + str(sys.argv))	#shouldnt really come up
    sys.exit(1)

count = 0
for bagFile in listOfBagFiles:
    count += 1
    print ("reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile)
    #access bag
    bag = rosbag.Bag(bagFile)
    bagContents = bag.read_messages()
    bagName = bag.filename


    	#create a new directory
    folder = string.rstrip(bagName, ".bag")
    try:	#else already exists
        os.makedirs(folder)
    except:
        pass
    shutil.copyfile(bagName, folder + '/' + bagName)


    #get list of topics from the bag
    listOfTopics = []
    for topic, msg, t in bagContents:
        if topic not in listOfTopics:
            listOfTopics.append(topic)


    for topicName in listOfTopics:
        #Create a new CSV file for each topic
        filename = (folder + '/' + string.replace(topicName, '/', '_slash_') + '.csv')
        with open(filename, 'w+') as csvfile:
            filewriter = csv.writer(csvfile, delimiter = ',')
            firstIteration = True	#allows header row
            for subtopic, msg, t in bag.read_messages(topicName):	# for each instant in time that has data for topicName
                #parse data from this instant, which is of the form of multiple lines of "Name: value\n"
                #	- put it in the form of a list of 2-element lists
                msgString = str(msg)
                msgList = string.split(msgString, '\n')
                instantaneousListOfData = []
                for nameValuePair in msgList:
                    splitPair = string.split(nameValuePair, ':')
                    for i in range(len(splitPair)):	#should be 0 to 1
                        splitPair[i] = string.strip(splitPair[i])
                    instantaneousListOfData.append(splitPair)
                #write the first row from the first element of each pair
                if firstIteration:	# header
                    headers = ["rosbagTimestamp"]	#first column header
                    for pair in instantaneousListOfData:
                        headers.append(pair[0])
                    filewriter.writerow(headers)
                    firstIteration = False
                # write the value from each pair to the file
                values = [str(t)]	#first column will have rosbag timestamp
                for pair in instantaneousListOfData:
                    if len(pair) > 1:
                        values.append(pair[1])
                filewriter.writerow(values)
    bag.close()
    os.remove(bagFile)
    
    # open file for processing and normalising
    # Data out (in order from left-right):
    # time roll(pwm) pitch(pwm) thrust(pwm) yawrate(pwm) x y z roll(rad) pitch(rad) yaw(rad)  vx vy vz wx wy wz
    with open(filename, 'rb') as f:
        Processing = 0
        k=0
        data = list(csv.reader(f))

    #for row in reader:
        # row is a list of strings
        # use string.join to put them together
        #print(row[0])
        print(np.shape(data))
#        for i in range(1,len(data)-1):
#            if data[i][7]=='"Position"' or data[i][7]=='"MPC"':
#                processed=np.zeros((len(data)-i+1,18))
#                break
        processed=np.zeros((len(data),18))
        for i in range(1,len(processed)-1):                       

    #(float(data[i][0])-float(data[1][0]))/10**9 # rosbag time in row 1
            processed[i][0]=(float(data[i][4])+float(data[i][5])/10**9)-(float(data[1][4])+float(data[1][5])/10**9) # message publish time
            processed[i][1]=(float(data[i+1][4])+float(data[i+1][5])/10**9)-(float(data[1][4])+float(data[1][5])/10**9)-processed[i][0] # message publish time
            if data[i][7]=='"Disarmed"':
                processed[i][2:5]=0
            else:
                processed[i][2]=(float(data[i][16])-1500)/1000 # Roll pwm scaled
                processed[i][3]=(float(data[i][17])-1500)/1000 # Pitch pwm scaled
                processed[i][4]=(float(data[i][18])-1000)/1000 # Thrust pwm scaled
                processed[i][5]=(float(data[i][19])-1500)/1000 # Yaw pwm scaled
            for j in range(6,18):
                processed[i][j] =float(data[i][j+17]) # x y z roll pitch yaw vx vy vz wx wy wz
            # if normalise position
            #processed[i][9] =processed[i][9]-floatfloat(data[i][35])
            #processed[i][10] =processed[i][10]-floatfloat(data[i][36])
            #processed[i][11] =processed[i][11]-floatfloat(data[i][37])
        processed=processed[~np.all(processed == 0, axis=1)]
        print(np.shape(processed))
        filename_processed=folder + '/Processed.csv'
        np.savetxt(filename_processed, processed, delimiter=",", header="time,dt,R,P,T,Y,x,y,z,r,p,y,vx,vy,vz,wx,wy,wz")

print ("Done reading all " + numberOfFiles + " bag files.")
