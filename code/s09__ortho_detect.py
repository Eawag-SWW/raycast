"""
Args:
 - trained classifiers
 - orthophoto
 - boundary file
Writes:
 - detected objects
 - clusters

"""

from subprocess import call
from s07__detect_objects_2d import cascade_detect
import default_settings as s
import os, cv2, sys
import helpers



def ortho_detect(config, debug):
    # clipped orthophoto location
    ortho_path = s.inputs['orthophoto']

    # loop through folds
    for fold_i in range(s.general['do_folds']):
        print('-- FOLD {} --'.format(fold_i))
        # detected locations should be stored here
        output_folder = os.path.join(config['iteration_directory'],
                                     s.general['iterations_structure']['ortho_detect'],
                                     'fold_{}'.format(fold_i))
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # classifier data found here
        classifier_xml = os.path.join(config['iteration_directory'],
                                      s.general['iterations_structure']['train'],
                                      'classifier_{}'.format(fold_i), 'cascade.xml')

        cascade_detect(
            ortho_path,
            output_folder,
            classifier_xml)

    return 0

