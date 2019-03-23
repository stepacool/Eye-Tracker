# Eye-Tracker
Eye tracking using OpenCV, Python.
[Youtube Video Demonstration](https://youtu.be/zDN-wwd5cfo "Eye tracking")

## Overview
A **very** accurate eye-tracking software.
![What it looks like](https://i.imgur.com/DQRmibk.png)

## Features
- Cross-platform
- Works with glasses
- Does not require high-end hardware, works well even with a 640*480 webcam
- Uses blob detection algorithm, but earlier versions used circle detection too.
- Highly extensible/flexible

## Requirements
- Python 3(will work with 2.7 if you install custom PyQT5 for it)
- PyQT 5(to install it for 2.7 use **pip install python-qt5** WARNING: Windows-only)
- OpenCV 3.4 +
- NumPy 1.15.2 +

## Guide
- To run: python main.py
- adjust thresholds for different lighting conditions(low for dark, high for bright)
- Detailed development guide: https://medium.com/@stepanfilonov/tracking-your-eyes-with-python-3952e66194a6

## Developer
- Stepan Filonov (@stepacool) stepanfilonov@gmail.com
