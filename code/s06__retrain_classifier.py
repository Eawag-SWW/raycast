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


def retrain_classifier(config, debug):
    # identify latest training data
    new_classifier_dir = os.path.join(config['iteration_directory'],
                                      settings.general['iterations_structure']['retrain'])
    training_image_dir_pos = os.path.join(settings.general['working_directory'],
                                          settings.general['preparations_subdir'],
                                          settings.general['preparations_structure']['extract'], 'images', 'positives')
    training_image_dir_neg = os.path.join(config['iteration_directory'],
                                          settings.general['iterations_structure']['refresh'], 'negatives')

    positives_dat_path = os.path.join(training_image_dir_pos, 'info.dat')
    negatives_dat_path = os.path.join(training_image_dir_neg, 'info.dat')
    positives_xml_path = os.path.join(training_image_dir_pos, 'positives.xml')
    positives_numsamples = len(os.listdir(os.path.join(training_image_dir_pos, 'img')))
    negatives_numsamples = len(os.listdir(os.path.join(training_image_dir_neg, 'img')))

    # create positive examples xml
    path_vec = os.path.join(settings.general['opencv'], 'opencv_createsamples.exe')
    call(args=['opencv_createsamples.exe',
               '-info', str(positives_dat_path),
               '-vec', str(positives_xml_path),
               '-w', str(settings.training_images['width']),
               '-h', str(settings.training_images['height']),
               '-num', str(positives_numsamples)],
         executable=path_vec)

    # create folder to store classifier products
    if not os.path.exists(new_classifier_dir):
        os.makedirs(new_classifier_dir)
    # convert classifier settings into list
    args = ['opencv_traincascade.exe']
    args.extend(['-data', new_classifier_dir])
    args.extend(['-vec', positives_xml_path])
    args.extend(['-bg', negatives_dat_path])
    for key, value in settings.haarClassiferArgs.iteritems():
        args.append('-' + key)
        args.append(str(value))
    args.extend(['-numPos', str(int(positives_numsamples * settings.classifer_training['positive_sample_ratio']))])
    args.extend(['-numNeg', str(min(negatives_numsamples, positives_numsamples*settings.classifer_training['neg_pos_ratio']))])

    print args
    # Call script to create train classifier
    # logfile = open(os.path.join(current_iter_dir, 'log_training.txt'), 'w+')
    call(args=args, executable=os.path.join(settings.general['opencv'], 'opencv_traincascade.exe'))
    # logfile.close()

    return 0
