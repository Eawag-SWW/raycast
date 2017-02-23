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
                                      settings.general['iterations_structure'][5])
    training_image_dir = os.path.join(config['iteration_directory'],
                                      settings.general['iterations_structure'][4])

    positives_dat_path = os.path.join(training_image_dir, 'positives', 'info.dat')
    negatives_dat_path = os.path.join(training_image_dir, 'negatives', 'info.dat')
    positives_xml_path = os.path.join(training_image_dir, 'positives', 'positives.xml')
    positives_numsamples = len(os.listdir(os.path.join(training_image_dir, 'positives', 'img')))
    negatives_numsamples = len(os.listdir(os.path.join(training_image_dir, 'negatives', 'img')))

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
    training_dir = os.path.join(new_classifier_dir, 'haar_training/')
    if not os.path.exists(training_dir):
        os.makedirs(training_dir)
    # convert classifier settings into list
    args = ['opencv_traincascade.exe']
    args.extend(['-data', training_dir])
    args.extend(['-vec', positives_xml_path])
    args.extend(['-bg', negatives_dat_path])
    for key, value in settings.haarClassiferArgs.iteritems():
        args.append('-' + key)
        args.append(str(value))
    args.extend(['-numPos', str(int(positives_numsamples * settings.classifer_training['positive_sample_ratio']))])
    args.extend(['-numNeg', str(negatives_numsamples)])

    print args
    # Call script to create train classifier
    # logfile = open(os.path.join(current_iter_dir, 'log_training.txt'), 'w+')
    call(args=args, executable=os.path.join(settings.general['opencv'], 'opencv_traincascade.exe'))
    # logfile.close()

    return 0
