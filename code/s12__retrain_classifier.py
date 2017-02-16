"""
Args:
 - retrain classifier with latest image samples
Writes:
 - a Cascade classifier xml file
   - location: [project home directory]/s12__retrain_classifier/
Tasks:
 - create positive training data
 - train classifier

"""

from subprocess import call
import default_settings as settings
import os


def retrain_classifier(structure, debug):
    # identify latest training data
    iteration_dirs = os.listdir(os.path.join(settings.general['working_directory'], settings.general['iterations_subdir']))
    current_iter_dir = os.path.join(
        os.path.join(settings.general['working_directory'], settings.general['iterations_subdir']),
        sorted(iteration_dirs, reverse=True)[0])  # get latest iteration

    positives_dat_path = os.path.join(current_iter_dir, 'positives', 'info.dat')
    positives_xml_path = os.path.join(current_iter_dir, 'positives', 'positives.xml')
    positives_numsamples = len(os.listdir(os.path.join(current_iter_dir, 'positives', 'img')))

    # create positive examples xml
    call(args=['opencv_createsamples.exe',
               '-info', str(positives_dat_path),
               '-vec', str(positives_xml_path),
               '-w', str(settings.training_images['width']),
               '-h', str(settings.training_images['height']),
               '-num', str(positives_numsamples)],
         executable=os.path.join(settings.general['opencv'], 'opencv_createsamples.exe'))

    # convert settings into list
    args = []
    for key, value in settings.haarClassiferArgs.iteritems():
        args.append('-'+key)
        args.append(str(value))
    # Call script to create positive training data
    # call(args=args, )

    return 1