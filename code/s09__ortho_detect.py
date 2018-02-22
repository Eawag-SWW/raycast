"""
Args:
 - trained classifiers
 - orthophoto
 - boundary file
Writes:
 - detected objects
 - clusters

"""

from s07__detect_objects_2d import cascade_detect
import os



def ortho_detect(config, debug, settings):
    # clipped orthophoto location
    ortho_path = settings['inputs']['orthophoto']

    # loop through folds
    for fold_i in range(settings['general']['do_folds']):
        print('-- FOLD {} --'.format(fold_i))
        # detected locations should be stored here
        output_folder = os.path.join(config['iteration_directory'],
                                     settings['general']['iterations_structure']['ortho_detect'],
                                     'fold_{}'.format(fold_i))
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # classifier data found here
        classifier_xml = os.path.join(config['iteration_directory'],
                                      settings['general']['iterations_structure']['train'],
                                      'classifier_{}'.format(fold_i), 'cascade.xml')

        cascade_detect(
            ortho_path,
            output_folder,
            classifier_xml,
            settings
        )

    return 0
