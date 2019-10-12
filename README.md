# In-Air-HandWriting-SNAC

## Data collection for In-Air-HandWriting project

## Overview
A data collection program written by Python


## Installation Guide

Pre-Install:
* Tkinter
* Leap
* matplotlib

Run command to build package:\
``` pyinstaller -F 'GUI_Pack.py' --hidden-import='PIL._tkinter_finder'```

Run command to execute directly:\
``` python GUI_Pack.py```

## Use

Run command to give permission for file:\
``` chmod 777 dist/GUI_Login ```

Run command to give permission for CDC:\
``` chmod 666 /dev/ttyACM0 ```


## Support
Windows\
Linux\
Mac OS does not work well