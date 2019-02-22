import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import serial
import re
import csv
import seaborn as sns

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



    
    
    
# list ports

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





# save every sample, keep last XX in memory
def readAndSave(serial_con, maxTime = 600, wait_time = 0, 
                returnVals = True, saveData = True, dataDir = "Need Path", 
               PORT = "COM8", timeout = 10):
    
    """
    Reads data from Arduino, saves each line to a file
  
    Parameters: 
    maxTime (int): Max number of seconds the function run
    wait_time (float): number of seconds between readings
    returnVals (logical): True means return a data frame of values
    saveData (logical): True means save data (in dataDir)
    dataDir (diretory): folder where data are stored
    PORT (string): the port from which we're reading
    timeout (int): number of seconds to continue recording, if there is no action
    
    Returns: 
    array: data from the most recent 10 readings 
  
    """

    startTime = time.time()
    tmp = np.empty((1, 6), dtype = '<U26')
    topSensorLastData = 999
    timeOfLastVisit = time.time()
    ctr = 0
    if PORT == "COM8":
        topSensorPosition = 2
    
    
    while msvcrt.kbhit():
        msvcrt.getch()
        print('clearing characters ...')
    
    while (time.time() - startTime) < maxTime:    
        serial_con.write("r".encode("utf-8"))
        txt = serial_con.readline().decode("utf-8")
        tmp[0, 0:5] = [int(i) for i in txt.split(',')]
        tmp[0, 5] = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        time.sleep(wait_time)
        
        if saveData:
            if ctr == 0:
                s = tmp[0, 5]
                s = re.sub(r'[^\w\s]','_',s)
                s = re.sub(" ", "__", s)[0:] + ".csv"
                if PORT == "COM8":
                    with open(os.path.join(dataDir, s), 'w+', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerows([np.array(["mid_sensor", "top_sensor", "base_sensor", 
                                               "limit_1", "limit_2", "timestamp"], dtype = '<U26')])
                #refref add COM7        
                        
                    
            with open(os.path.join(dataDir, s), 'a+', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerows(tmp)
        
        # stop if there is no action for XX sec
        if (abs(topSensorLastData - int(tmp[0, topSensorPosition])) > 5) and (ctr > 0):
            #print("ACTION")
            timeOfLastVisit = time.time()
        # break if there is no action for XX sec
        elif(time.time() - timeOfLastVisit > timeout):
            print("No action for " + str(timeout) + " sec")
            break
        
        # update top sensor last data
        topSensorLastData = int(tmp[0, topSensorPosition])
        
        if msvcrt.kbhit(): # if q is pressed, then break
            k = msvcrt.getch()
            if(k == b'q') | (k == b'\x1b') | (k == b'\x0b') :
                print("keyboard break")
                winsound.MessageBeep()
                break
        ctr += 1
    # read in data, if returnVals is True
    if returnVals and saveData: 
        return(pd.read_csv(os.path.join(dataDir, s)))