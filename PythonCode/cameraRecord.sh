#!/bin/bash
# usage
# ./cameraRecord.sh Directory
#chmod +x cameraRecord.sh makes it so that you can type "./" instead of "bash" 

# want to save here
# C:\\Users\\Combes4\\Desktop\\TempVids

dirName=$1

C:\\Users\\Combes4\\Anaconda2\\envs\\python3_5_pyfly\\python.exe beeDataAcq $dirName 
