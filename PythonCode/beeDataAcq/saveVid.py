

import numpy as np
import cv2
import datetime
import PyCapture2 as fc2
import sys
import time
import os
import re
import skimage.io as io
import csv
from itertools import islice


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
### Resize images (for speed)
####################################################################          
        
        
def reduceSize(dat, originalShape = [1024, 1280], proportion = 1/10):
    # reduce resolution by 4X to make it faster

    def downsample_to_proportion(rows, proportion=1):
        return(list(islice(rows, 0, len(rows), int(1/proportion))))

    def writeArr(ctr, proportion = 0.25):
        return(downList[int(ctr*originalShape[1]*proportion):\
                        int((ctr+1)*originalShape[1]*proportion)])
    
    downList = downsample_to_proportion(dat, proportion = proportion)
    lstLst =   [writeArr(ctr, proportion = proportion)\
                for ctr in range(originalShape[0])]
    new_list = downsample_to_proportion(lstLst, proportion =proportion)
    smallImg = np.array(new_list)
    return(smallImg)
             
        
        
####################################################################
### Check if there is a bee close to the flower
####################################################################       
        
        
def beeInImage(calImg, frame, blurAmt = (5,5), areaThreshold= 5):
    '''
    Returns True if a bee is detected in the image
    
    Detects bees by size of dark blobs in the image
    --if it doesn't work, try including light blobs.
    
    Parameters
    ----------
    calImg : np.array(int16) -- note that it is NOT uint8, which is default
        Calibration image (no bee visible)
    frame : np.array(int16) 
        frame of current image to compare with calibration image

    Returns
    -------
    bool
        True if there is a bee in the frame
   
    '''
    
    # check dtype
    if calImg.dtype != "int16":
        calImg = calImg.astype('int16') 
    if frame.dtype != "int16":
        frame = frame.astype('int16')
    
    # get image difference
    im1Diff = (calImg - frame) 
    height,width = im1Diff.shape
    
    # crop image to a circle
    mask_circ = np.zeros((height,width), np.uint8)
    cv2.circle(mask_circ,(int(width/2),int(height/2)),int(np.min([width,height])/2),(255),thickness=-1)
    imDiff_cropped = cv2.bitwise_and(im1Diff, im1Diff, mask=mask_circ)

    # gaussian blur
    # 121, 121 works for full sized image, 15,15 works for 4x smaller image
    # 5,5 works for 1/10 size
    blur = cv2.GaussianBlur(imDiff_cropped, blurAmt ,0)
    
    # get darker sections (positive threshold gives dark areas)
    ret_dark,th3_dark = cv2.threshold(blur,70,255,cv2.THRESH_BINARY)
    
    # get areas
    img, cnts, _ = cv2.findContours(th3_dark.astype('uint8'), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.ones(th3_dark.shape[:2], dtype="uint8") * 0 # create a blank black mask

    areas = np.array([cv2.contourArea(c, False) for c in cnts])
    
    if len(areas) == 0:
        areas = np.array([0])
    else:
        print(max(areas))

    # if there is at least one area over areaThreshold, then it's a bee
    return(any(areas > areaThreshold), max(areas))






####################################################################
### Save data and write csv file from each image
####################################################################

def saveAviHelper2_process(conn, cam, camCal1, cam2, camCal2, 
                           fileFormat, fileName, fileName2, csvFileName,
                           frameRate, maxImgs = 500):
    
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
        csvFileName (str): filename for writing data about frames
        frameRate (int): should be set to max (the arduino is actually in charge of fps)
        maxImgs (int): number of images before quitting.
    
    '''
    
    
    numImages = 0
    tmpDat = np.empty(5, dtype = '<U26')

    avi = fc2.AVIRecorder()
    avi2 = fc2.AVIRecorder()
    
    # resize calibration images 4x
    camCal1 = camCal1[::10,::10]
    camCal2 = camCal2[::10,::10]

    for i in range(maxImgs):
        
        try:
            tmpDat[0] = str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S_%f")[:-3])
            image = cam.retrieveBuffer()
            image2 = cam2.retrieveBuffer()
            
            dat1,dat2 = image.getData(), image2.getData()
            
            # make images smaller
            frame1 = reduceSize(dat1, (image.getRows(), image.getCols()), proportion = 1/10)
            frame2 = reduceSize(dat2, (image2.getRows(), image2.getCols()), proportion = 1/10)
            
## refref: here is where I could do some image processing with opencv
## refref: write to dataset -- timestamp, camera1BeeInFrame, camera2BeeInFrame
            tmpDat[1], tmpDat[2] = beeInImage(camCal1, frame1)
            tmpDat[3], tmpDat[4] = beeInImage(camCal2, frame2)
        
            # write to file      
            with open(csvFileName, 'a+', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                if i == 0:
                    wr.writerow(["datetime", "beeInImage1", "darkArea1", "beeInImage2", "darkArea2"]) #write header
                wr.writerow(tmpDat)
            
            
        except fc2.Fc2error as fc2Err:
            print("Error retrieving buffer : ", fc2Err)
            continue

        #print("Grabbed image {}".format(i))
        
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
        #print("Appended image {}...".format(i))

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
    
    
    
    
################################################################
#### MAIN
################################################################
    
    
    
    
def main(conn, camCal1, camCal2, directory = "C:\\Users\\Combes4\\Desktop\\TempVids"):
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
    csvFileName = os.path.join(directory,  movieID + ".csv")
    conn.send(os.path.join(directory,   movieID))
#     saveAviHelper2(conn, c,d, "AVI", fileName.encode("utf-8"), fileName2.encode("utf-8"), 10, maxImgs = 10000)
    saveAviHelper2_process(conn, c, camCal1, d, camCal2, 
                           "MJPG", fileName.encode("utf-8"), fileName2.encode("utf-8"), 
                           csvFileName,
                           10, maxImgs = 10000)

# MJPG is slower than AVI
    
    
if __name__ == "__main__":
    main(directory)
   