

import numpy as np
import cv2
import datetime
import PyCapture2 as fc2
import sys
import time
import os
import re
import skimage.io as io


import beeDataAcq.cameraSetup as cs



####################################################################
### Get a calibration image from each camera
####################################################################
def getCalibrationImages():
    '''
    Get images so I can do background subtraction.
    
    Note that two cameras must be connected.
        - This can be checked by running cameraSetup first
    '''
    try:
        bus = fc2.BusManager()
        numCams = bus.getNumOfCameras()

        cam1 = fc2.Camera()
        cam1.connect(bus.getCameraFromIndex(0))

        cam2 = fc2.Camera()
        cam2.connect(bus.getCameraFromIndex(1))

        # start capture
        cs.enableEmbeddedTimeStamp(cam1, True)
        cam1.startCapture()
        cs.enableEmbeddedTimeStamp(cam1, True)
        cam2.startCapture()    

        image = cam1.retrieveBuffer()
        image2 = cam2.retrieveBuffer()

        # show still image
        img = np.concatenate((cs.img2array(image), cs.img2array(image2)), axis = 1)
        io.imshow(img)
        
        # save images with specific filenames
        return(cs.img2array(image).astype(np.int16), cs.img2array(image2).astype(np.int16))
    
    except:
        print("error on calibration images")



####################################################################
### Save data and write csv file from each image
####################################################################

def saveAviHelper2_process(conn, cam, camCal1, cam2, camCal2, 
                           fileFormat, fileName, fileName2, frameRate, maxImgs = 500):
    
    '''
    Saves video as .avi
    Saves dataset -- each row is a single timestep, when frames were retreived
    
    Arguments:
        conn (connection): a child_connection for multiprocessing
        cam (camera): camera 1
        camCal1 (np.array): background image for cam
        cam2 (camera): camera 2
        camCal2 (np.array): background image for cam2
        fileFormat (string): should be avi
        filename, filename2: (str) filenames for recorded videos
        frameRate (int): should be set to max (the arduino is actually in charge of fps)
        maxImgs (int): number of images before quitting.
    
    '''
    
    
    numImages = 0
    tmpDat = np.empty(3, dtype = '<U26')

    avi = fc2.AVIRecorder()
    avi2 = fc2.AVIRecorder()

    for i in range(maxImgs):
        
        try:
            tmpDat[0] = str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S_%f")[:-3])
            image = cam.retrieveBuffer()
            image2 = cam2.retrieveBuffer()
            
## refref: here is where I could do some image processing with opencv
## refref: write to dataset -- timestamp, camera1BeeInFrame, camera2BeeInFrame
            
            
        except fc2.Fc2error as fc2Err:
            print("Error retrieving buffer : ", fc2Err)
            continue

        print("Grabbed image {}".format(i))
        
        # check connection, and break of something is received
        if conn.poll():
            print(str(i) + str(conn.recv()))
            for jj in range(10):
                cv2.destroyAllWindows()
            break


        if (i == 0):
            if fileFormat == "AVI":
                avi.AVIOpen(fileName, frameRate)
                avi2.AVIOpen(fileName2, frameRate)
            elif fileFormat == "MJPG":
                avi.MJPGOpen(fileName, frameRate, 75)
                avi2.MJPGOpen(fileName2, frameRate, 75)
            elif fileFormat == "H264":
                avi.H264Open(fileName, frameRate, image.getCols(), image.getRows(), 1000000)
                avi2.H264Open(fileName2, frameRate, image2.getCols(), image2.getRows(), 1000000)
            else:
                print("Specified format is not available.")
                return
            
            # show still image
            img = np.concatenate((cs.img2array(image), cs.img2array(image2)), axis = 1)

            # Display the resulting frame
            cv2.imshow('image', img)
            

        # break when "q" is pressed on keyboard
        k = cv2.waitKey(1) & 0xFF

        if (k  == ord('q')) or (k == 27):
            for jj in range(10):
                cv2.destroyAllWindows()
            break

        # refref add image timestamp
        avi.append(image)
        avi2.append(image2)
        numImages += 1
        print("Appended image {}...".format(i))

    # close windows if loop ends
    for jj in range(10):
        cv2.destroyAllWindows()
        
    print("Appended {} images to {} file: {}...".format(numImages, fileFormat, fileName))
    avi.close()
    avi2.close()

####################################################################
### Save data but do no processing
####################################################################

def saveAviHelper2(conn, cam, cam2, fileFormat, fileName, fileName2, frameRate, maxImgs = 500):
    
    numImages = 0

    avi = fc2.AVIRecorder()
    avi2 = fc2.AVIRecorder()

    for i in range(maxImgs):
        
        try:
            image = cam.retrieveBuffer()
            image2 = cam2.retrieveBuffer()
            
## refref: here is where I could do some image processing with opencv
## refref: write to dataset -- timestamp, camera1BeeInFrame, camera2BeeInFrame
            
            
        except fc2.Fc2error as fc2Err:
            print("Error retrieving buffer : ", fc2Err)
            continue

        print("Grabbed image {}".format(i))
        
        # check connection, and break of something is received
        if conn.poll():
            print(str(i) + str(conn.recv()))
            for jj in range(10):
                cv2.destroyAllWindows()
            break


        if (i == 0):
            if fileFormat == "AVI":
                avi.AVIOpen(fileName, frameRate)
                avi2.AVIOpen(fileName2, frameRate)
            elif fileFormat == "MJPG":
                avi.MJPGOpen(fileName, frameRate, 75)
                avi2.MJPGOpen(fileName2, frameRate, 75)
            elif fileFormat == "H264":
                avi.H264Open(fileName, frameRate, image.getCols(), image.getRows(), 1000000)
                avi2.H264Open(fileName2, frameRate, image2.getCols(), image2.getRows(), 1000000)
            else:
                print("Specified format is not available.")
                return
            
            # show still image
            img = np.concatenate((cs.img2array(image), cs.img2array(image2)), axis = 1)

            # Display the resulting frame
            cv2.imshow('image', img)
            

        # break when "q" is pressed on keyboard
        k = cv2.waitKey(1) & 0xFF

        if (k  == ord('q')) or (k == 27):
            for jj in range(10):
                cv2.destroyAllWindows()
            break

        # refref add image timestamp
        avi.append(image)
        avi2.append(image2)
        numImages += 1
        print("Appended image {}...".format(i))

    # close windows if loop ends
    for jj in range(10):
        cv2.destroyAllWindows()
        
    print("Appended {} images to {} file: {}...".format(numImages, fileFormat, fileName))
    avi.close()
    avi2.close()
    
def main(conn, directory = "C:\\Users\\Combes4\\Desktop\\TempVids"):
    # avi recording function
    bus = fc2.BusManager()
    numCams = bus.getNumOfCameras()


    c = fc2.Camera()
    c.connect(bus.getCameraFromIndex(0))
    d = fc2.Camera()
    d.connect(bus.getCameraFromIndex(1))

    # start capture
    cs.enableEmbeddedTimeStamp(c, True)
    c.startCapture()
    cs.enableEmbeddedTimeStamp(c, True)
    d.startCapture()
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    #directory = os.path.join("C:\\Users\\Combes4\Desktop\\temp3")
    movieID = str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S_%f")[:-3])
    fileName = os.path.join(directory,   movieID + "_cam1" + ".avi")
    fileName2 = os.path.join(directory,  movieID + "_cam2" + ".avi")
    conn.send(os.path.join(directory,   movieID))
    saveAviHelper2(conn, c,d, "AVI", fileName.encode("utf-8"), fileName2.encode("utf-8"), 10, maxImgs = 10000)


    
    
if __name__ == "__main__":
    main(directory)
   