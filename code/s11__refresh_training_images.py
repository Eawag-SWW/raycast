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


def refresh_training_images(structure, debug):
    # Create folder structure for the current iteration
    iteration_dir = os.path.join(settings.general['working_directory'],
                                 settings.general['iterations_subdir'], datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
    # # identify latest training data
    # iteration_dirs = os.listdir(
    #     os.path.join(settings.general['working_directory'], settings.general['iterations_subdir']))
    # iteration_dir = os.path.join(
    #     os.path.join(settings.general['working_directory'], settings.general['iterations_subdir']),
    #     sorted(iteration_dirs, reverse=True)[0])  # get latest iteration

    for directory in ['positives/img', 'negatives/img']:
        dir = os.path.join(iteration_dir, directory)
        if not os.path.exists(dir):
            os.makedirs(dir)
            if debug: print "directory created: {directory}".format(directory=dir)
    pass

    # PROCESS POINTS
    # load points
    candidates = pd.read_csv(
        os.path.join(settings.general['working_directory'], structure[9], '3dpoints_evaluated.csv'),
        sep=' ')

    # for each image, do clipping
    for image_name in list(candidates.image.unique()):
        sys.stdout.write('.')
        # Load image
        image = ndimage.imread(os.path.join(settings.general['working_directory'], structure[2], image_name + '.tif'),
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
            filename = '{}_({}-{}).jpg'.format(image_name, cd['img_x'], cd['img_y'])
            misc.imsave(os.path.join(iteration_dir, subdir, filename), crop1)

    print 'done clipping. Writing dat files'

    # save list of file names
    for directory in ['positives', 'negatives']:
        img_list = os.listdir(os.path.join(
            iteration_dir, directory, 'img'))
        list_file = open(os.path.join(iteration_dir, directory, "info.dat"), "w+")
        for path in img_list:
            # positives and negatives require a different format
            if directory == 'positives':
                list_file.writelines(os.path.join('img', "{} 1 0 0 {} {}\n".format(
                    path, settings.training_images['width'], settings.training_images['height'])))
            elif directory == 'negatives':
                list_file.writelines(os.path.join(iteration_dir, directory, 'img', "{}\n".format(path)))
        list_file.close()

    return 0
