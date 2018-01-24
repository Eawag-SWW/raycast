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
import pandas as pd
import datetime
import os
import default_settings as settings
from scipy import ndimage
from scipy import misc
import sys
from Tkinter import *
from tkMessageBox import *


def extract_candidate_images(config, debug, training_image_dir='', points_file=''):
    # Output of candidate images
    if training_image_dir == '':
        training_image_dir = os.path.join(config['iteration_directory'], settings.general['iterations_structure']['extract'])

    # Input of points
    if points_file == '':
        points_file = os.path.join(config['iteration_directory'], settings.general['iterations_structure']['evaluate'],
                                   '3dpoints_evaluated.csv')

    for directory in ['positives/img', 'negatives/img']:
        dir = os.path.join(training_image_dir, directory)
        if not os.path.exists(dir):
            os.makedirs(dir)
            if debug: print "directory created: {directory}".format(directory=dir)
    pass

    # PROCESS POINTS
    # load points
    candidates = pd.read_csv(points_file, sep=' ')

    # Todo: load positives and negatives from previous generation

    # for each image, extract the hard negatives from that image.
    for image_name in list(candidates.image.unique()):
        sys.stdout.write('.')
        # Load image
        image_file = os.path.join(settings.general['working_directory'], settings.general['preparations_subdir'],
                                  settings.general['preparations_structure']['clip'],
                                  image_name + '.'+settings.inputs['image_extension'])
        if not os.path.isfile(image_file):
            continue

        image = ndimage.imread(image_file,
                               flatten=True)
        # Process candidates from that image
        filtered_cd = candidates[candidates['image'] == image_name]
        for index, cd in filtered_cd.iterrows():
            # Clip image
            # Make box
            box_left = cd['img_x'] - settings.training_images['width'] / 2
            box_upper = cd['img_y'] - settings.training_images['height'] / 2
            box_right = cd['img_x'] + settings.training_images['width'] / 2
            box_lower = cd['img_y'] + settings.training_images['height'] / 2

            crop1 = image[box_upper:box_lower, box_left:box_right]
            # Based on whether it is a hit or miss, save it in the right place
            subdir = 'positives/img'
            if cd['is_match'] == 0:
                subdir = 'negatives/img'
            # Save image and write filename
            filename = '{}_{}_({}-{}).jpg'.format(cd['x'], image_name, cd['img_x'], cd['img_y'])
            misc.imsave(os.path.join(training_image_dir, subdir, filename), crop1)

            # If it's a miss, save as such


    print 'done clipping. Writing dat files'
    showwarning(title='Verify samples', message='Please verify that the sample images in %s are correct.' %
                                                training_image_dir)

    # save list of file names
    for directory in ['positives', 'negatives']:
        img_list = os.listdir(os.path.join(
            training_image_dir, directory, 'img'))
        list_file = open(os.path.join(training_image_dir, directory, "info.dat"), "w+")

        # positives and negatives require a different format
        if directory == 'positives':
            for path in img_list:
                list_file.writelines(os.path.join('img', "{} 1 0 0 {} {}\n".format(
                    path, settings.training_images['width'], settings.training_images['height'])))
        elif directory == 'negatives':
            for path in img_list:
                list_file.writelines(os.path.join(training_image_dir, directory, 'img', "{}\n".format(path)))
        list_file.close()

    return 0
