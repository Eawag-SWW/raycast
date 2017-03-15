'''
Creates training image sets for the new generation of classifier
- combines previous training data with newly extracted negative samples (we assume that there are no new positive samples)
- if this is the first iteration, then only the initial training data is used
'''

import os
import shutil
import default_settings as s


def refresh_training_sets(config, debug):
    # copy negative samples to one place
    training_image_dir = os.path.join(config['iteration_directory'], s.general['iterations_structure']['refresh'])
    neg_dir = os.path.join(training_image_dir, 'negatives')

    # remove all previous
    if os.path.exists(neg_dir):
        shutil.rmtree(neg_dir)

    # remake folder
    neg_dir_img = os.path.join(neg_dir, 'img')
    if not os.path.exists(neg_dir_img):
        os.makedirs(neg_dir_img)
        if debug: print "directory created: {directory}".format(directory=dir)

    # todo: deal with copying an image that already exists

    # Copy all the files over
    for dir_src in [config['neg_samples_initial_dir'], config['neg_samples_new_dir']]:
        if dir_src != '':
            for filename in os.listdir(dir_src):
                shutil.copy(os.path.join(dir_src, filename), neg_dir_img)

    # Write dat file
    img_list = os.listdir(neg_dir_img)
    with open(os.path.join(neg_dir, "info.dat"), "w+") as list_file:
        for path in img_list:
            list_file.writelines(os.path.join(neg_dir_img, "{}\n".format(path)))

    return 0
