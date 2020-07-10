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

def column(matrix, i):
    return [row[i] for row in matrix]

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
    folder = bagName.rstrip(".bag")
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
        filename = (folder + '/' + topicName.replace('/', '_slash_') + '.csv')
        with open(filename, 'w+') as csvfile:
            filewriter = csv.writer(csvfile, delimiter = ',')
            firstIteration = True	#allows header row
            for subtopic, msg, t in bag.read_messages(topicName):	# for each instant in time that has data for topicName
                #parse data from this instant, which is of the form of multiple lines of "Name: value\n"
                #	- put it in the form of a list of 2-element lists
                msgString = str(msg)
                msgList = msgString.split('\n')
                instantaneousListOfData = []
                for nameValuePair in msgList:
                    splitPair = nameValuePair.split(':')
                    for i in range(len(splitPair)):	#should be 0 to 1
                        splitPair[i] = splitPair[i].strip()
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

    dataname1=(folder + '/_slash_Flight_Data.csv')
    dataname2=(folder + '/Flight_Data.csv')
    if os.path.exists(dataname1) or os.path.exists(dataname2): # Check for both naming conventions
        if os.path.exists(dataname1):
            dataname=dataname1
        else:
            dataname=dataname2
        with open(dataname, 'rt') as f:
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
            processed=np.zeros((len(data)-2,18))
            time=np.float_(column(data,4)[1:len(data)])+np.float_(column(data,5)[1:len(data)])/10**9-(float(data[1][4])+float(data[1][5])/10**9) # message publish time        
            processed[:,0]=time[0:len(processed)]  
            processed[:,1]=time[1:(len(processed)+1)]-time[0:len(processed)]      
            processed[:,2]=(np.float_(column(data,16)[1:(len(processed)+1)])-1500)/1000 # Roll pwm scaled
            processed[:,3]=(np.float_(column(data,17)[1:(len(processed)+1)])-1500)/1000 # Pitch pwm scaled
            processed[:,4]=(np.float_(column(data,18)[1:(len(processed)+1)])-1000)/1000 # Thrust pwm scaled
            processed[:,5]=(np.float_(column(data,19)[1:(len(processed)+1)])-1500)/1000 # Yawrate pwm scaled
            if (np.shape(data)[1]>=53):
                for j in range(6,18):
                    processed[:,j] = np.float_(column(data,j+17)[1:(len(processed)+1)]) # x y z roll pitch yaw vx vy vz wx wy wz
            else:
                for j in range(6,18):
                    processed[:,j] = np.float_(column(data,j+14)[1:(len(processed)+1)]) # x y z roll pitch yaw vx vy vz wx wy wz
    
            for i in range(1,len(processed)-1): # remove ground contact        

                if processed[i][8]>-0.0001 and processed[i][8]<0:
                    processed[i][8]=0.0
                elif processed[i][8]<=-0.0001:
                    print(processed[i][8])
                    processed=np.delete(processed,list(range(i,len(processed))),0)
                    #print('break')
                    break

            processed=processed[~np.all(processed == 0, axis=1)] # not sure if we still need this
            print(np.shape(processed))
            filename_processed=folder + '/Processed.csv'
            np.savetxt(filename_processed, processed, delimiter=",", header="time,dt,R,P,T,Y,x,y,z,r,p,y,vx,vy,vz,wx,wy,wz")


print ("Done reading all " + numberOfFiles + " bag files.")
