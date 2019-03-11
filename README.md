# Eye-Tracker
Eye tracking using OpenCV, Python.
[Youtube Video Demonstration](https://youtu.be/zDN-wwd5cfo "Eye tracking")

## Overview
A **very** accurate eye-tracking software.
![What it looks like](https://i.imgur.com/DQRmibk.png)

## Features
- Works with glasses
- Does not require high-end hardware, works well even with 640*480 webcam
- Has two algorithms(Hough circles and Blob detection) implemented with very comfortable sliders to adjust on any enviroment
- Highly extensible/flexible

## Requirements
- Python 2.7
- PyQT 5  for Python 2.7 (pip install python-qt5)
- OpenCV 3.4.3.18
- NumPy 1.15.2

## Guide
- When **Blob** is selected, only changing **Threshold** slider affects the result
- When **Circle** is selected, **every** slider but threshold slider affect the result
- To launch, open track.py with Python 2.7 with all the required libraries installed(listed above)

## Developer
- Stepan Filonov (@stepacool) stepanfilonov@gmail.com
