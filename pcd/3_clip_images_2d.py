"""
Clip each image with its corresponding projected boundary file

Reads:
 - 2D boundary multipolygon file for each camera
 - image for each camera
Writes:
 - N clipped images, where N is the number of cameras
Tasks:
 - clip each image using the corresponding multipolygon
Tools:
 - rasterclipper.py
"""