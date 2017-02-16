"""
Args:
 - create new set of training images (positive and negative) for object detection
Writes:
 - two folders containing sample images, positive samples and negative samples
   - location: [project home directory]/s11__refresh_training_images/
   - format: as required by openCV traincascade
Tasks:
 - Read evaluation results
 - For each image, clip out all negative samples and apply transformations to increase diversity

"""


import csv
import os

def refresh_training_images(structure, debug):
    return 0