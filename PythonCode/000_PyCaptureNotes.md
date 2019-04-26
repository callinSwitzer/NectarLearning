## PyCapture is difficult to install. 

### System information:
I'm using (Python Installer) PyCapture2-2.13.31.win-amd64-py3.6.msi and (Flycap SDK) FlyCapture_2.13.3.31_x64.exe

* ### Problem 1: DLL Failed to load
Solutions: Install Visual Studio 2013
1. I emailed pt grey support: 
>Dear Point Grey Support Team,

>I'm hoping you can help me use my Chameleon3 cameras with Python.

>I'm having trouble using the Python bindings for the FlyCapture SDK. Maybe the simplest solution is just to give me the older versions of FlyCapture and PyCapture2. Is there a way I can download and use older versions?

>I am setting up my cameras on a new computer, and cannot get PyCapture2 to work. I had it working with my other computer, using FlyCapture 2.11.3.121. and PyCapture2-2.11.121 (also running 64 bit Windows 10, same as my new computer).

>Here are the steps I took:

>I downloaded and installed FlyCapture SDK. I did this by downloading the file, "FlyCapture_2.13.3.31_x64.exe" from the ptgrey downloads website (https://www.ptgrey.com/support/downloads).

>I downloaded python 3.6.8 from python.org and installed it in C:\Python3.
>I navigated to that directory and ran
```C:/Python3/python.exe -m pip install setuptools cython numpy```

>I downloaded "PyCapture2-2.13.31.win-amd64-python2_3.zip" from the ptgrey website, unzipped it, and double clicked the file, "PyCapture2-2.13.31.win-amd64-py3.6.msi"

>I allowed it to install to Python 3.6 from registry.

>When I run python and try to import PyCapture2, I get the error, "ImportError: DLL load failed: The specified module could not be found."

>Here is the code I ran:

```
C:\Python3>python.exe
Python 3.6.8 (tags/v3.6.8:3c6b436a57, Dec 24 2018, 00:16:47) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> sys.executable
'C:\\Python3\\python.exe'
>>> sys.version
'3.6.8 (tags/v3.6.8:3c6b436a57, Dec 24 2018, 00:16:47) [MSC v.1916 64 bit (AMD64)]'
>>> import PyCapture2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: DLL load failed: The specified module could not be found.
```

Point Grey Responded very promptly: 

>This is an issue that we are aware of and the cause is that it is trying to link to some Visual Studio 2013 debug libraries that will only be present if you have an installation of Visual Studio 2013. We should have a fix for this shortly but in the mean time we recommend that you either revert back to FlyCapture 2.12 or install Visual Studio 2013.
 
>Here are some links to FlyCapture 2.12 if you do not have it:
>Windows 64bit: https://flir.box.com/s/XXXXX
 
>Here is the PyCapture 2.12 installers:
>https://flir.box.com/s/XXXXXXX
 
>Please make sure to uninstall the PyCapture 2.13, delete all the files under "C:\Users\xxx\AppData\Local\Temp" if possible, then restart your computer and reinstall PyCapture2.12. This step is necessary as your system might still "remember" the old path in cache and will give the same error even after you roll back to PyCapture2.12.


* ### Problem: I can import PyCapture2 in ipython, but not in jupyter lab:
Solutions: 
Adding conda.pth to "site-packages" directory
