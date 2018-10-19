# Eye-Tracker
### To use:
# 1. Launch (py -2.7) imageprocess.py
# 2. Press ESC when your camera is setup
# 3. Coordinates of your eyes are printed in the console

Eye tracking using OpenCV, Python.

A simple eye tracker using OpenCV library, written in pure python.

Was written with the intention of being able to track eyes on low res cameras(640x480 and below), when regular gaze tracking methods don't work(Haar circle, etc.)

Easy to setup, works on many PCs, cameras and lighting conditions, not just mine.

Many comments, the code is easy to follow.

TODO:

1. Make it an OBS-overlay. Work in progress. Using JS/Electron.
2. Introduce multithreading/multiprocessing for the sake of performance.
