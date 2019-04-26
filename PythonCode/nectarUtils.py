import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import serial
import re
import csv
import seaborn as sns
import warnings

import glob
import msvcrt
import winsound
import sklearn
import time

import time
import os
import shutil
import sys
from datetime import datetime

import threading
import queue



# packages for calibration
from sklearn.cluster import KMeans
import peakutils



##############################################################
# list ports
##############################################################


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

##############################################################
# Reward Bee
##############################################################

## refref: add baseSensorThreshold to the read and reward function, so I can specify from jupyter notebook
# refref: eventually have mach learning involved to choose these values
def Reward(serial_con, 
           numSteps =15, 
           rewardSeconds= 2.0, 
           nectarState = "low", 
           saveFileName = "tmp.csv", 
           dataDir = "Need Path",
           backAmt = 20,
           saveData = False, 
           baseSensorThreshold = 300, 
          baseSensorPosition = 2, 
          ignoreWarnings = False, 
          resetSteps = 50,
          rewardType = ""):
    """
    Moves nectar up the tube, so that it is accessible by the bees.
    
    Only moves nectar if 
        (1) nectar is low
        (2) limit switches are open                   
    
    Parameters:
        serial_con (string): arduino serial connection
        numSteps (int): number or steps to move the motor forward (too high will overflow)
        rewardSeconds (float): number of seconds to make reward available
        nectarState (string): "high" or "low"
        saveFileName (filename): File for saving data 
        dataDir (directory): Which folder should data be saved in
        backAmt (int): number of additional steps back to take after reward
        saveData (logical): True means the data should be saved
        baseSensorThreshold (int): threshold where nectar is "seen" by base sensor
        baseSensorPosition (int): the column of the data the is the base sensor
        ignoreWarnings (bool): True means warnings won't be printed
        resetSteps (int): max number of forward steps taken to reset nectar at correct level
        rewardType (str): either "" or "sham"
    
    Returns: 
        None
    """
    
    while msvcrt.kbhit():
        msvcrt.getch()
        print('clearing characters ...')

    if nectarState != "low":
        print('Nectar is not in the correct position')
    else:
        tmp = np.empty((1, 8), dtype = '<U26')
        tmp[0, 6] = serial_con.port
        
        # move forward
        for ii in range(numSteps):
            # move forward one step
            serial_con.write("f".encode("utf-8"))
        
            # check to see if limit switch has been hit
            serial_con.write("r".encode("utf-8"))
            txt = serial_con.readline().decode("utf-8")
            tmp[0, 0:5] = [int(i) for i in txt.split(',')]
            tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            
            if ii == 0:
                tmp[0, 7] = rewardType + "reward Triggered"
            else:
                tmp[0,7] = ""
                
            # notify if limit switch is hit
            if (tmp[0, 3] == "1") or (tmp[0, 4] == "1"):
                winsound.MessageBeep()
                warnings.warn("Limit switch hit")
                
            # append to file
            if saveData:
                with open(os.path.join(dataDir, saveFileName), 'a+', newline='') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerows(tmp)

            
        
        # wait and record data before retracting reward
        #time.sleep(rewardSeconds)
        timeStart = time.time()
        while (time.time() - timeStart) < rewardSeconds:
            # check to see if limit switch has been hit
            serial_con.write("r".encode("utf-8"))
            txt = serial_con.readline().decode("utf-8")
            tmp[0, 0:5] = [int(i) for i in txt.split(',')]
            tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            # notify if limit switch is hit
            if (tmp[0, 3] == "1") or (tmp[0, 4] == "1"):
                winsound.MessageBeep()
                warnings.warn("Limit switch hit")
                
            # append to file
            if saveData:
                with open(os.path.join(dataDir, saveFileName), 'a+', newline='') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerows(tmp)
                    #print("Data written", tmp[0,5])

        

        # return nectar to bottom position
        # move at least as far as it went up, and then slowly move forward until the lowest
        # photogate changes
        for jj in range(numSteps + backAmt):
            
            # break by keyboard option
            if msvcrt.kbhit(): # if q, or escape is pressed, then break
                k = msvcrt.getch()
                if(k == b'q') | (k == b'\x1b') | (k == b'\x0b') :
                    print("keyboard break")
                    winsound.MessageBeep()
                    break

            serial_con.write("b".encode("utf-8"))
            
            # check to see if limit switch has been hit
            serial_con.write("r".encode("utf-8"))
            txt = serial_con.readline().decode("utf-8")
            tmp[0, 0:5] = [int(i) for i in txt.split(',')]
            tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            # notify if limit switch is hit
            if (tmp[0, 3] == "1") or (tmp[0, 4] == "1"):
                winsound.MessageBeep()
                warnings.warn("Limit switch hit")
                
            # append to file
            if saveData:
                with open(os.path.join(dataDir, saveFileName), 'a+', newline='') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerows(tmp)

        
        # we must wait for the motor to stop moving
        time.sleep(0.5)
        
        # move back forward until the base sensor is seeing the liquid

        for ii in range(resetSteps):
            
            serial_con.write("r".encode("utf-8"))
            txt = serial_con.readline().decode("utf-8")
            #print(txt)
            tmp[0, 0:5] = [int(i) for i in txt.split(',')]
            tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            
            # append to file
            if saveData:
                with open(os.path.join(dataDir, saveFileName), 'a+', newline='') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerows(tmp)

            
            # notify if limit switch is hit
            if (tmp[0, 3] == "1") or (tmp[0, 4] == "1"):
                winsound.MessageBeep()
                warnings.warn("Limit switch hit")
               
                
            # note: tmp[0,2] is the base sensor for COM8
            # refref
            if int(tmp[0, baseSensorPosition]) < baseSensorThreshold:
                break
                             
            serial_con.write("ff".encode("utf-8"))
            time.sleep(0.1)
            
        # warning if nectar never reaches the bottom sensor
        if int(tmp[0, baseSensorPosition]) > baseSensorThreshold:
            if ignoreWarnings == False:
                warnings.warn("Check Nectar -- it may be too low!!")


            
            
            
            
##############################################################
# save every sample, keep last XX in memory
# also do rewards
##############################################################

def readAndSave(serial_con = None, maxTime = 600, wait_time = 0, 
                returnVals = True, saveData = True, 
                dataDir = "Need Path",
               reward = True, 
               calibrationInfo = "", 
               flagPos = 0):
    
    """   
    Reads data from Arduino, saves each line to a file
  
    Parameters: 
    maxTime (int): Max number of seconds the function run
    wait_time (float): number of seconds between readings
    returnVals (logical): True means return a data frame of values
    saveData (logical): True means save data (in dataDir)
    dataDir (diretory): folder where data are stored
    reward (logical): should the bee be rewarded
    calibrationInfo (dict): calibration information (saved to first line of csv file)
    flagPos (int): 0 or 1 for ser1 or ser2
    
    
    Returns: 
    array: data from the most recent 10 readings 
  
    """

#     timeout = int(maxTime - 1)
    timeout = 5*60 # five minute timeout
    startTime = time.time()
    tmp = np.empty((1, 8), dtype = '<U260')
    tmp[0, 6] = serial_con.port
    topSensorLastData = 999
    timeOfLastVisit = time.time()
    minSinceLastVisit = 999
    ctr = 0
    resetting = False
    global flag
    flag = [0, 0]
    
    global rewardCounter
    rewardCounter = [0,0]
    maxRewards = 100
    
    minRewardThreshold = int(1.10*calibrationInfo["topBaseline"]) 
    colNames = calibrationInfo["colNames"] 
    baseSensorThreshold = calibrationInfo['base_dec_bound']
    topSensorPosition = np.where(colNames == "top")[0][0]
    baseSensorPosition = np.where(colNames == "base")[0][0]
    
    # initialize nectar to correct level
    Reward(serial_con, numSteps=0, rewardSeconds=0, dataDir = dataDir,
                   saveData = False, saveFileName = "tmp", backAmt = 30, 
          baseSensorThreshold = baseSensorThreshold, 
          baseSensorPosition = baseSensorPosition)
    


       
    
    while msvcrt.kbhit():
        msvcrt.getch()
        print('clearing characters ...')
    
    while ((time.time() - startTime) < maxTime): 
        
        if flag == [1,1]:
            print("no action at either flower for ", timeout, " seconds")
            winsound.PlaySound("*", winsound.SND_ALIAS)
            break
        
        if sum(rewardCounter) >= maxRewards:
            print("bee reached " + str(maxRewards) + " rewards")
            winsound.PlaySound("*", winsound.SND_ALIAS)
            break
        
        # print time
        if np.mod(ctr, 1000) == 0:
            print(np.round(time.time() - startTime), "seconds elapsed")
        
        serial_con.write("r".encode("utf-8"))
        txt = serial_con.readline().decode("utf-8")
        tmp[0, 0:5] = [int(i) for i in txt.split(',')]
        tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        if (ctr == 0):
            s = tmp[0, 5]
            s = re.sub(r'[^\w\s]','_',s)
            s = re.sub(" ", "__", s)[0:] + ".csv"
        minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
        
        # if baseline gets too high (i.e. nectar is going down), reset it
        if int(tmp[0, baseSensorPosition]) > calibrationInfo['base_dec_bound']:
            print("Nectar is drifting -- resetting")
            Reward(serial_con, numSteps=0, rewardSeconds=0, dataDir = dataDir,
                       saveData = saveData, saveFileName = s,  backAmt = 30,
                   baseSensorThreshold = baseSensorThreshold, 
                      baseSensorPosition = baseSensorPosition)
            tmp[0, -1:] = "auto-reset nectar position"
            resetting = True
            
            
        
        time.sleep(wait_time)
        
        # refref: can cause a problem if the nectar resets on ctr == 0
        
        if saveData:
            if (ctr == 0):
                # add colnames
                with open(os.path.join(dataDir, s), 'w+', newline='') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerows([np.hstack([colNames[0:3], 
                                            ["limit_1", "limit_2", "timestamp", "port", "notes"]]).astype('<U26')])       
                        
                    
            with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                if ctr == 0:
                    calCopy = calibrationInfo.copy() 
                    calCopy.pop("calbData") # remove the calbData key from the dict
                    tmp[0, -1:] = str(calCopy)
                wr.writerows(tmp)
        
        # reset notes
        tmp[0, -1:] = ""
        
        # stop if there is no action for XX sec
        if (topSensorLastData - int(tmp[0, topSensorPosition]) < -2) and (ctr > 0):
            
            timeOfLastVisit = time.time()
            #  reward bee
            # refref: only reward bee if bee has pulled out of flower before last visit
            if minSinceLastVisit < minRewardThreshold:
                # add one to reward counter
                rewardCounter[flagPos] += 1
                print("ACTION ", rewardCounter, serial_con.port)
                
                Reward(serial_con, numSteps=15, rewardSeconds=2.0, dataDir = dataDir,
                       saveData = saveData, saveFileName = s, baseSensorThreshold = baseSensorThreshold, 
                      baseSensorPosition = baseSensorPosition)
               
                # reset min threshold to high
                minSinceLastVisit = 999
 
        elif((time.time() - startTime) > (maxTime - 5)):
            print("Timeout at ", time.time() - startTime, " seconds")
            break

        # if bee doesn't visit for timeout seconds
        if((time.time() - timeOfLastVisit) > timeout):
            flag[flagPos] = 1
        else:
            flag[flagPos] = 0
        
        # update top sensor last data
        serial_con.write("r".encode("utf-8"))
        txt = serial_con.readline().decode("utf-8")
        tmp[0, 0:5] = [int(i) for i in txt.split(',')]
        minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
        topSensorLastData = int(tmp[0, topSensorPosition])
        
        if msvcrt.kbhit(): # if q, or escape is pressed, then break
            k = msvcrt.getch()
            if(k == b'q') | (k == b'\x1b') | (k == b'\x0b') :
                print("keyboard break")
                winsound.MessageBeep()
                break
                
            # allow researcher to move nectar manually
            elif (k == b'b'):
                serial_con.write("bb".encode("utf-8"))
                serial_con.write("r".encode("utf-8"))
                txt = serial_con.readline().decode("utf-8")
                #print(txt)
                tmp[0, 0:5] = [int(i) for i in txt.split(',')]
                tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                tmp[0, 7] = "manual b"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)
                            
            elif (k == b'f'):
                serial_con.write("ff".encode("utf-8"))
                serial_con.write("r".encode("utf-8"))
                txt = serial_con.readline().decode("utf-8")
                #print(txt)
                tmp[0, 0:5] = [int(i) for i in txt.split(',')]
                tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                tmp[0, 7] = "manual f"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)
                
            elif (k == b'r'):
                
                serial_con.write("r".encode("utf-8"))
                txt = serial_con.readline().decode("utf-8")
                #print(txt)
                tmp[0, 0:5] = [int(i) for i in txt.split(',')]
                tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                tmp[0, 7] = "manual reward"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)
                
                #  manually reward bee
                Reward(serial_con, numSteps=15, rewardSeconds=2.0, dataDir = dataDir,
                       saveData = saveData, saveFileName = s, baseSensorThreshold = baseSensorThreshold, 
                      baseSensorPosition = baseSensorPosition)
            # reset note column
            tmp[0, 7] = ""
            resetting = False
        #print(minSinceLastVisit)
        ctr += 1
    # read in data, if returnVals is True
    if returnVals and saveData: 
        return(pd.read_csv(os.path.join(dataDir, s)), s)
    

    
######################################################################   
## SHAM Read and Save
######################################################################
    
    
def shamReadAndSave(serial_con = None, maxTime = 600, wait_time = 0, 
                returnVals = True, saveData = True, 
                dataDir = "Need Path",
               reward = True, 
               calibrationInfo = "", 
               flagPos = 0):
    
    """
    Reads data from Arduino, saves each line to a file. Does not reward bee.
  
    Parameters: 
    maxTime (int): Max number of seconds the function run
    wait_time (float): number of seconds between readings
    returnVals (logical): True means return a data frame of values
    saveData (logical): True means save data (in dataDir)
    dataDir (diretory): folder where data are stored
    reward (logical): should the bee be rewarded
    calibrationInfo (dict): calibration information (saved to first line of csv file)
    flagPos (int): 0 or 1 for ser1 or ser2
    
    
    Returns: 
    array: data from the most recent 10 readings 
  
    """

#     timeout = int(maxTime - 1)
    timeout = 5*60 # five minute timeout
    startTime = time.time()
    tmp = np.empty((1, 8), dtype = '<U260')
    tmp[0, 6] = serial_con.port
    topSensorLastData = 999
    timeOfLastVisit = time.time()
    minSinceLastVisit = 999
    ctr = 0
    resetting = False
    global flag
    flag = [0, 0]
    
    global rewardCounter
    rewardCounter = [0,0]
    maxRewards = 100
    
    minRewardThreshold = int(1.10*calibrationInfo["topBaseline"]) 
    colNames = calibrationInfo["colNames"] 
    baseSensorThreshold = calibrationInfo['base_dec_bound']
    topSensorPosition = np.where(colNames == "top")[0][0]
    baseSensorPosition = np.where(colNames == "base")[0][0]
    
    # initialize nectar to correct level
    Reward(serial_con, numSteps=0, rewardSeconds=0, dataDir = dataDir,
                   saveData = False, saveFileName = "tmp", backAmt = 30, 
          baseSensorThreshold = baseSensorThreshold, 
          baseSensorPosition = baseSensorPosition, ignoreWarnings = True,
          resetSteps = 0, rewardType = "sham ")
    


       
    
    while msvcrt.kbhit():
        msvcrt.getch()
        print('clearing characters ...')
    
    while ((time.time() - startTime) < maxTime): 
        
        if flag == [1,1]:
            print("no action at either flower for ", timeout, " seconds")
            winsound.PlaySound("*", winsound.SND_ALIAS)
            break
            
        if sum(rewardCounter) >= maxRewards:
            print("bee reached " + str(maxRewards) + " rewards")
            winsound.PlaySound("*", winsound.SND_ALIAS)
            break
        
        # print time
        if np.mod(ctr, 1000) == 0:
            print(np.round(time.time() - startTime), "seconds elapsed")
        
        serial_con.write("r".encode("utf-8"))
        txt = serial_con.readline().decode("utf-8")
        tmp[0, 0:5] = [int(i) for i in txt.split(',')]
        tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        if (ctr == 0):
            s = tmp[0, 5]
            s = re.sub(r'[^\w\s]','_',s)
            s = re.sub(" ", "__", s)[0:] + ".csv"
        minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
        
#         # if baseline gets too high (i.e. nectar is going down), reset it
#         if int(tmp[0, baseSensorPosition]) > calibrationInfo['base_dec_bound']:
#             print("Nectar is drifting -- resetting")
#             Reward(serial_con, numSteps=0, rewardSeconds=0, dataDir = dataDir,
#                        saveData = saveData, saveFileName = s,  backAmt = 30,
#                    baseSensorThreshold = baseSensorThreshold, 
#                       baseSensorPosition = baseSensorPosition)
#             tmp[0, -1:] = "auto-reset nectar position"
#             resetting = True
            
            
        
        time.sleep(wait_time)
        
        # refref: can cause a problem if the nectar resets on ctr == 0
        
        if saveData:
            if (ctr == 0):
                # add colnames
                with open(os.path.join(dataDir, s), 'w+', newline='') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerows([np.hstack([colNames[0:3], 
                                            ["limit_1", "limit_2", "timestamp", "port", "notes"]]).astype('<U26')])       
                        
                    
            with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                if ctr == 0:
                    calCopy = calibrationInfo.copy() 
                    calCopy.pop("calbData") # remove the calbData key from the dict
                    tmp[0, -1:] = str(calCopy)
                wr.writerows(tmp)
        
        # reset notes
        tmp[0, -1:] = ""
        
        # stop if there is no action for XX sec
        if (topSensorLastData - int(tmp[0, topSensorPosition]) < -2) and (ctr > 0):

            timeOfLastVisit = time.time()
            #  reward bee
            # refref: only reward bee if bee has pulled out of flower before last visit
            if minSinceLastVisit < minRewardThreshold:
                # add one to reward counter
                rewardCounter[flagPos] += 1
                print("ACTION ", rewardCounter, serial_con.port)
                
                Reward(serial_con, numSteps=16, rewardSeconds=2.0, dataDir = dataDir,
                       saveData = saveData, saveFileName = s, baseSensorThreshold = baseSensorThreshold, 
                      baseSensorPosition = baseSensorPosition, ignoreWarnings = True, backAmt = 30,
                      resetSteps = 15, rewardType = "sham " )
                
                # reset min threshold to high
                minSinceLastVisit = 999
 
        elif((time.time() - startTime) > (maxTime - 5)):
            print("Timeout at ", time.time() - startTime, " seconds")
            break

        # if bee doesn't visit for timeout seconds
        if((time.time() - timeOfLastVisit) > timeout):
            flag[flagPos] = 1
        else:
            flag[flagPos] = 0
        
        # update top sensor last data
        serial_con.write("r".encode("utf-8"))
        txt = serial_con.readline().decode("utf-8")
        tmp[0, 0:5] = [int(i) for i in txt.split(',')]
        minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
        topSensorLastData = int(tmp[0, topSensorPosition])
        
        if msvcrt.kbhit(): # if q, or escape is pressed, then break
            k = msvcrt.getch()
            if(k == b'q') | (k == b'\x1b') | (k == b'\x0b') :
                print("keyboard break")
                winsound.MessageBeep()
                break
                
            # allow researcher to move nectar manually
            elif (k == b'b'):
                serial_con.write("bb".encode("utf-8"))
                serial_con.write("r".encode("utf-8"))
                txt = serial_con.readline().decode("utf-8")
                #print(txt)
                tmp[0, 0:5] = [int(i) for i in txt.split(',')]
                tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                tmp[0, 7] = "manual b"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)
                            
            elif (k == b'f'):
                serial_con.write("ff".encode("utf-8"))
                serial_con.write("r".encode("utf-8"))
                txt = serial_con.readline().decode("utf-8")
                #print(txt)
                tmp[0, 0:5] = [int(i) for i in txt.split(',')]
                tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                tmp[0, 7] = "manual f"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)
                
            elif (k == b'r'):
                
                serial_con.write("r".encode("utf-8"))
                txt = serial_con.readline().decode("utf-8")
                #print(txt)
                tmp[0, 0:5] = [int(i) for i in txt.split(',')]
                tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                tmp[0, 7] = "manual reward"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)
                
                #  manually reward bee
                Reward(serial_con, numSteps=15, rewardSeconds=2.0, dataDir = dataDir,
                       saveData = saveData, saveFileName = s, baseSensorThreshold = baseSensorThreshold, 
                      baseSensorPosition = baseSensorPosition)
            # reset note column
            tmp[0, 7] = ""
            resetting = False
        #print(minSinceLastVisit)
        ctr += 1
    # read in data, if returnVals is True
    if returnVals and saveData: 
        return(pd.read_csv(os.path.join(dataDir, s)), s)
    
    
    
######################################################################
##  Machine learning calibration
######################################################################
def calibrate(serial_con):
    '''
    Calibrates the sensor



    Returns: baseSensorThreshold to use in experiments, list of column names
    '''
    # make sure that the experiment is ready:
#     ready = input("Is nectar at the end of the tube, and the tube inserted correctly? [y/n] ")
#     if ready[0].lower() != "y":
#         warnings.warn("Calibration not completed")
#         return(np.nan)
    if False:
        return(np.nan)
    
    # move nectar
    else:
        df = pd.DataFrame(columns=['a','b','c','d', 'e', 'f'], index=np.arange(0, 40))
        tmp = np.empty((1, 6), dtype = '<U26')
        for jj in range(df.shape[0]):
            if jj > 5:
                serial_con.write("bb".encode("utf-8"))
            serial_con.write("r".encode("utf-8"))
            txt = serial_con.readline().decode("utf-8")
            #print(txt)
            tmp[0, 0:5] = [int(i) for i in txt.split(',')]
            tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            df.loc[jj] = tmp[0,:]
            
            if int(tmp[0, 3]) == 1 or int(tmp[0, 4]) == 1:
                print("Limit switch hit")
                return(np.nan)
            
        df['timestamp'] = pd.to_datetime(df['f'])
        df.loc[:,['a','b','c','d', 'e']] = df.loc[:,['a','b','c','d', 'e']].apply(pd.to_numeric, errors='coerce')
        
        calb = df
        onsets = np.zeros(calb.shape[1]-2, dtype = 'int')
        calb.columns = ['a', 'b', 'c', 'd', 'e', "time", "timestamp"]

        for jj in range(calb.shape[1] - 2):
            dat = calb.iloc[:, jj].rolling(window=3, min_periods = 1, center = True).var()
            # peaks, hts = find_peaks(dat, height=100)
            peaks= np.array(peakutils.indexes(dat, thres=0.5, min_dist=2))
            hts = np.array(dat[peaks])
            

            if(peaks.shape[0] > 0):
                # if peaks are small, it's electronic noise, so ignore
                if np.max(hts) < 10:
                    peaks = np.array([])
                    onsets[jj] = 0
                else:
                    onsets[jj] = peaks[np.argmax(hts)]
                #dat.plot()
                #plt.scatter(x = peaks[np.argmax(hts['peak_heights'])], y = hts["peak_heights"][np.argmax(hts['peak_heights'])])
        #         calb.plot(y=['a', 'b', 'c', 'd', 'e'], style='-')
        #         plt.vlines(x = peaks[np.argmax(hts['peak_heights'])], ymin = 0, ymax = 700)
        #         plt.show()

        # if there is not enough nectar movement, quit

        if np.sum(np.array(onsets) != 0) < 2:
            numSeen = str(np.sum(np.array(onsets) != 0))
            print("Nectar movement detected by " + numSeen + 
                  " detector(s) on " + serial_con.port + ". Should be 2.\n")
            return(np.nan)
            
        medVals = [np.median(calb.iloc[:,jj]) for jj in range(5)]

        columns = np.zeros(5, dtype = 'object')
        columns[onsets.argsort()[3]], columns[onsets.argsort()[4]] = "mid", "base"
        columns[(columns != "mid") & (columns !="base") & (np.array(medVals) > 2)] = "top"
        columns[columns == 0] = "limit"

        columns = np.hstack([columns, ["time_S", "time"]])

        calb.columns = columns
        #calb.head()
        # calb.plot(y=['top', 'mid', 'base'], style='-')
        
        # add cluster for outliers
        kmc = KMeans(n_clusters = 3)
#         ctr2 = 0
#         colors = ["red", 'blue']
        decBounds = {"base": "", "mid": "", 
                     "topBaseline": "", "midBaseline": "", "baseBaseline": "", 
                    "colNames": "", 
                    "port": serial_con.port}
        for location in ["base", "mid"]:
            classData = calb[location].copy()
            
            # refref: inefficient -- calculating rolling mean again
            dat = classData.rolling(window=3, min_periods = 1, center = True).var()
            
            # label outliers as -99
            classData.loc[dat > 0.1*np.max(dat)] = -99
            
            classes = kmc.fit_predict(np.array(classData).reshape(-1, 1))
            # remove outlier classes
            classMeds = np.array([np.median(classData[classes == cc]) for cc in np.unique(classes)])
            classesNoOutlier = np.unique(classes)[np.unique(classes) != np.unique(classes)[classMeds < 0][0]]
            
            # calculate decision boundaries
            decBound = np.abs((np.median(np.array(classData)[classes == classesNoOutlier[0]]) + 
                np.median(np.array(classData)[classes == classesNoOutlier[1]])) / 2).astype(int)
            
            calb[location + "_classes"] = classes
            decBounds[location] = decBound
#             plt.plot(calb[location][classes == 0], 'bo', label = "")
#             plt.plot(calb[location][classes == 1], 'ro', label = "")
#             plt.hlines(y = decBound, xmin = 0, xmax = calb.shape[0], 
#                        linestyle = "--", color = colors[ctr2], label = "dec. bound. -" + str(location))
#             ctr2 += 1
#         plt.ylabel("sensor light reading")
#         plt.xlabel("sample number")
#         plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2),
#                   fancybox=True, shadow=True, ncol=5)
        
        # refref: return top sensor baseline, bottom sensor baseline, and mid sensor baseline, column names
        decBounds["topBaseline"] = np.mean(calb["top"][0:])
        decBounds["midBaseline"] = np.mean(calb["mid"][0:4])
        decBounds["baseBaseline"] = np.mean(calb["base"][0:4])
        decBounds["colNames"] = np.array(calb.columns)[0:5]
        
        if np.abs(np.max(calb["top"]) - np.min(calb["top"])) > 10:
            warnings.warn(str(serial_con.port) + ": Top sensor changed during calibration -- may need to recalibrate")
        
        # rename keys
        decBounds["base_dec_bound"] = decBounds.pop("base")
        decBounds["mid_dec_bound"] = decBounds.pop("mid")
        decBounds["calbData"] = calb
        
#         print(decBounds)
#         plt.show()
        
        return(decBounds)

    
    
def plotCalibration(calibName):
    '''
    Plots calibration data (must have already conducted calibration)
    '''
    calibName["calbData"].plot(y = ["top", "mid", "base"])
    plt.hlines(y = calibName["base_dec_bound"], xmin = 0, xmax = len(calibName["calbData"]), 
               linestyle = "--", color = 'tab:green', label = "base_dec_bound")
    plt.hlines(y = calibName["mid_dec_bound"], xmin = 0, xmax = len(calibName["calbData"]), 
               linestyle = "--", color = 'tab:orange', label = "mid_dec_bound")
    plt.ylabel("sensor light reading")
    plt.xlabel("sample number")
    plt.legend(loc='center right', bbox_to_anchor=(1.4, 0.5), ncol=1, title=calibName['port'])
    plt.show() 
    
    
    
# plot data
def plotTrial(trialData):
    '''
    Plots data from one trial
    '''
    
    trialData['timestamp'] = pd.to_datetime(trialData['timestamp'])
    #trialData['delta'] = (trialData['timestamp']-trialData['timestamp'].shift()).fillna(pd.Timedelta(seconds=0))

    trialData.plot(y=['top', 'mid', 'base'], x = "timestamp", style='-', figsize=np.array([15, 5]))

    plt.scatter(y=trialData['top'], x = trialData["timestamp"])
    plt.vlines(trialData[trialData.notes == "reward Triggered"]["timestamp"], ymin = 0, ymax = 1000, label = "reward")
    plt.show()
    
    
    
def enthread_calib(target, args):
    q = queue.Queue()
    def wrapper():
        q.put(target(*args))
    t = threading.Thread(target=wrapper)
    t.start()
    return(q)    
    
def multiCalibrate(*serialPorts):
    qs = [enthread_calib(target = calibrate, args=(serialP,)) for serialP in serialPorts]
    cals = [qs[ii].get(timeout=10) for ii in range(len(qs))]
    if len(cals) == 1:
        cals = cals[0]
    return(cals)


def enthread_read(target, kwargs):
    q = queue.Queue()
    def wrapper():
        q.put(target(**kwargs))
    t = threading.Thread(target=wrapper)
    t.start()
    return(q)

def multiReadAndSave(ser1, ser2, cal1, cal2,
                     dataDir = "dataDir", maxTime = 15, 
                    serCOM3Treatment = "reward", 
                    serCOM4Treatment = "sham"):

    q1Target = readAndSave if serCOM3Treatment == "reward" else shamReadAndSave
    q2Target = readAndSave if serCOM4Treatment == "reward" else shamReadAndSave
    
    
    q1 = enthread_read(target = q1Target, 
                  kwargs={ "serial_con" : ser1, 
                           "calibrationInfo" : cal1 , 
                           "dataDir" : dataDir, 
                           "maxTime" : maxTime, 
                           "flagPos" : 0})
    q2 = enthread_read(target = q2Target, 
                  kwargs={ "serial_con" : ser2, 
                           "calibrationInfo" : cal2 ,
                           "dataDir" : dataDir, 
                           "maxTime" : maxTime, 
                           "flagPos" : 1})
    
    dat1, dat1_file = q1.get(timeout=maxTime)
    dat2, dat2_file = q2.get(timeout=maxTime)

    return(dat1, dat1_file, dat2, dat2_file)


