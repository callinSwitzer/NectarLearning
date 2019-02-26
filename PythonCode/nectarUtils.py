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
           baseSensorThreshold = 300):
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
        
    Returns: 
        None
    """


    if nectarState != "low":
        print('Nectar is not in the correct position')
    else:
        tmp = np.empty((1, 7), dtype = '<U26')
        
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
                tmp[0, 6] = "reward Triggered"
            else:
                tmp[0,6] = ""
                
            # notify if limit switch is hit
            if (tmp[0, 3] == "1") or (tmp[0, 4] == "1"):
                winsound.MessageBeep()
                warnings.warn("Limit switch hit")
                
            # append to file
            if saveData:
                if serial_con.port == "COM8":
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
                if serial_con.port == "COM8":
                    with open(os.path.join(dataDir, saveFileName), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)
                        #print("Data written", tmp[0,5])

        

        # return nectar to bottom position
        # move at least as far as it went up, and then slowly move forward until the lowest
        # photogate changes
        for jj in range(numSteps+ backAmt):
            
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
                if serial_con.port == "COM8":
                    with open(os.path.join(dataDir, saveFileName), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)

        
        # we must wait for the motor to stop moving
        time.sleep(0.5)
        
        # move back forward until the base sensor is seeing the liquid

        for ii in range(50):
            
            serial_con.write("r".encode("utf-8"))
            txt = serial_con.readline().decode("utf-8")
            #print(txt)
            tmp[0, 0:5] = [int(i) for i in txt.split(',')]
            tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            
            # append to file
            if saveData:
                if serial_con.port == "COM8":
                    with open(os.path.join(dataDir, saveFileName), 'a+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows(tmp)

            
            # notify if limit switch is hit
            if (tmp[0, 3] == "1") or (tmp[0, 4] == "1"):
                winsound.MessageBeep()
                warnings.warn("Limit switch hit")
               
                
            # note: tmp[0,2] is the base sensor for COM8
            if int(tmp[0, 2]) < baseSensorThreshold:
                break
                             
            serial_con.write("ff".encode("utf-8"))
            time.sleep(0.1)
            
        # warning if nectar never reaches the bottom sensor
        if int(tmp[0, 2]) > 300:
            warnings.warn("Check Nectar -- it may be too low")


            
            
            
            
##############################################################
# save every sample, keep last XX in memory
# also do rewards
##############################################################

def readAndSave(serial_con, maxTime = 600, wait_time = 0, 
                returnVals = True, saveData = True, 
                dataDir = "Need Path", timeout = 10, 
               reward = True, 
               minRewardThreshold = 150):
    
    """
    Reads data from Arduino, saves each line to a file
  
    Parameters: 
    maxTime (int): Max number of seconds the function run
    wait_time (float): number of seconds between readings
    returnVals (logical): True means return a data frame of values
    saveData (logical): True means save data (in dataDir)
    dataDir (diretory): folder where data are stored
    timeout (int): number of seconds to continue recording, if there is no action
    reward (logical): should the bee be rewarded
    minRewardThreshold (int): minimum value top sensor must reach in order to reward again
    
    Returns: 
    array: data from the most recent 10 readings 
  
    """

    startTime = time.time()
    tmp = np.empty((1, 7), dtype = '<U26')
    topSensorLastData = 999
    timeOfLastVisit = time.time()
    minSinceLastVisit = 999
    ctr = 0
    
    # initialize nectar to correct level
    Reward(serial_con, numSteps=0, rewardSeconds=0, dataDir = dataDir,
                   saveData = False, saveFileName = "tmp", backAmt = 30)
    
    
    if serial_con.port == "COM8":
        topSensorPosition = 1
    
    
    while msvcrt.kbhit():
        msvcrt.getch()
        print('clearing characters ...')
    
    while (time.time() - startTime) < maxTime:    
        serial_con.write("r".encode("utf-8"))
        txt = serial_con.readline().decode("utf-8")
        tmp[0, 0:5] = [int(i) for i in txt.split(',')]
        tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
        
        time.sleep(wait_time)
        
        if saveData:
            if ctr == 0:
                s = tmp[0, 5]
                s = re.sub(r'[^\w\s]','_',s)
                s = re.sub(" ", "__", s)[0:] + ".csv"
                if serial_con.port == "COM8":
                    with open(os.path.join(dataDir, s), 'w+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows([np.array(["mid_sensor", "top_sensor", "base_sensor", 
                                               "limit_1", "limit_2", "timestamp", "notes"], dtype = '<U26')])
                #refref add COM7        
                        
                    
            with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerows(tmp)
        
        # stop if there is no action for XX sec
        if (topSensorLastData - int(tmp[0, topSensorPosition]) < -2) and (ctr > 0):
            print("ACTION")
            timeOfLastVisit = time.time()
            #  reward bee
            # refref: only reward bee if bee has pulled out of flower before last visit
            
            if minSinceLastVisit < minRewardThreshold:
                Reward(serial_con, numSteps=15, rewardSeconds=2.0, dataDir = dataDir,
                       saveData = saveData, saveFileName = s)
                # reset min threshold to high
                minSinceLastVisit = 999
            
            
        # break if there is no action for XX sec
        elif(time.time() - timeOfLastVisit > timeout):
            print("No action for " + str(timeout) + " sec")
            break
        
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
                tmp[0, 6] = "manual f"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    if serial_con.port == "COM8":
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
                tmp[0, 6] = "manual f"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    if serial_con.port == "COM8":
                        with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                            wr.writerows(tmp)
                
            elif (k == b'r'):
                
                serial_con.write("r".encode("utf-8"))
                txt = serial_con.readline().decode("utf-8")
                #print(txt)
                tmp[0, 0:5] = [int(i) for i in txt.split(',')]
                tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                tmp[0, 6] = "manual reward"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    if serial_con.port == "COM8":
                        with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                            wr.writerows(tmp)
                
                #  manually reward bee
                Reward(serial_con, numSteps=15, rewardSeconds=2.0, dataDir = dataDir,
                       saveData = saveData, saveFileName = s)
            # reset note column
            tmp[0, 6] = ""
        #print(minSinceLastVisit)
        ctr += 1
    # read in data, if returnVals is True
    if returnVals and saveData: 
        return(pd.read_csv(os.path.join(dataDir, s)))
    

    
    
    
##############################################################    
# save every sample, keep last XX in memory
##############################################################

def readOnly(serial_con, maxTime = 5, wait_time = 0, 
                returnVals = True, saveData = True, 
                dataDir = "Need Path", timeout = 10):
    
    """
    Reads data from Arduino, saves each line to a file
  
    Parameters: 
    maxTime (int): Max number of seconds the function run
    wait_time (float): number of seconds between readings
    returnVals (logical): True means return a data frame of values
    saveData (logical): True means save data (in dataDir)
    dataDir (diretory): folder where data are stored
    timeout (int): number of seconds to continue recording, if there is no action
    
    Returns: 
    array: data from the most recent 10 readings 
  
    """

    startTime = time.time()
    tmp = np.empty((1, 7), dtype = '<U26')
    topSensorLastData = 999
    timeOfLastVisit = time.time()
    minSinceLastVisit = 999
    ctr = 0
    
    if serial_con.port == "COM8":
        topSensorPosition = 1
    
    
    while msvcrt.kbhit():
        msvcrt.getch()
        print('clearing characters ...')
    
    while (time.time() - startTime) < maxTime:    
        serial_con.write("r".encode("utf-8"))
        txt = serial_con.readline().decode("utf-8")
        tmp[0, 0:5] = [int(i) for i in txt.split(',')]
        tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
        
        time.sleep(wait_time)
        
        if saveData:
            if ctr == 0:
                s = tmp[0, 5]
                s = re.sub(r'[^\w\s]','_',s)
                s = re.sub(" ", "__", s)[0:] + ".csv"
                if serial_con.port == "COM8":
                    with open(os.path.join(dataDir, s), 'w+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows([np.array(["mid_sensor", "top_sensor", "base_sensor", 
                                               "limit_1", "limit_2", "timestamp", "notes"], dtype = '<U26')])
                #refref add COM7        
                        
                    
            with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerows(tmp)
        
        # stop if there is no action for XX sec
        if (topSensorLastData - int(tmp[0, topSensorPosition]) < -2) and (ctr > 0):
            print("ACTION")
            timeOfLastVisit = time.time()
            
            
        # break if there is no action for XX sec
        elif(time.time() - timeOfLastVisit > timeout):
            print("No action for " + str(timeout) + " sec")
            break
        
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
                tmp[0, 6] = "manual f"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    if serial_con.port == "COM8":
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
                tmp[0, 6] = "manual f"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    if serial_con.port == "COM8":
                        with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                            wr.writerows(tmp)
                
            elif (k == b'r'):
                
                serial_con.write("r".encode("utf-8"))
                txt = serial_con.readline().decode("utf-8")
                #print(txt)
                tmp[0, 0:5] = [int(i) for i in txt.split(',')]
                tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                tmp[0, 6] = "manual reward"
                minSinceLastVisit = np.min([int(tmp[0, topSensorPosition]), minSinceLastVisit])
            
                # append to file
                if saveData:
                    if serial_con.port == "COM8":
                        with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                            wr.writerows(tmp)
                
                #  manually reward bee
                Reward(serial_con, numSteps=15, rewardSeconds=2.0, dataDir = dataDir,
                       saveData = saveData, saveFileName = s)
            # reset note column
            tmp[0, 6] = ""
        #print(minSinceLastVisit)
        ctr += 1
    # read in data, if returnVals is True
    if returnVals and saveData: 
        return(pd.read_csv(os.path.join(dataDir, s)))
    
    
######################################################################
## REFREF: Machine learning calibration
######################################################################