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
import default_settings as s
import os


def train_classifier(config, debug):
    # identify latest training data
    training_image_dir_pos = os.path.join(s.general['working_directory'],
                                          s.general['preparations_subdir'],
                                          s.general['preparations_structure']['extract'],
                                          'images', 'positives')
    training_image_dir_neg = os.path.join(s.general['working_directory'],
                                          s.general['preparations_subdir'],
                                          s.general['preparations_structure']['extract'],
                                          'images', 'negatives')

    positives_dat_dir = os.path.join(s.general['working_directory'],
                                     s.general['preparations_subdir'],
                                     s.general['preparations_structure']['folds'])
    negatives_dat_path = os.path.join(training_image_dir_neg, 'bg.txt')
    positives_numsamples = int(len(os.listdir(os.path.join(training_image_dir_pos, 'img')))*(s.general['folds'] - 1)/s.general['folds'])
    negatives_numsamples = len(os.listdir(os.path.join(training_image_dir_neg, 'img')))

    # loop through folds
    for fold_i in range(s.general['folds']):
        # create positive examples xml
        print('training fold {}'.format(fold_i))
        positives_dat_path = os.path.join(positives_dat_dir, 'info_{}.dat'.format(fold_i))
        positives_xml_path = os.path.join(config['iteration_directory'],
                                          s.general['iterations_structure']['train'],
                                          'positives({}).xml'.format(fold_i))
        path_vec = os.path.join(s.general['opencv'], 'opencv_createsamples.exe')
        call(args=['opencv_createsamples.exe',
                   '-info', str(positives_dat_path),
                   '-vec', str(positives_xml_path),
                   '-w', str(s.training_images['width']),
                   '-h', str(s.training_images['height']),
                   '-num', str(positives_numsamples)],
             executable=path_vec)

        # create folder to store classifier products
        new_classifier_dir = os.path.join(config['iteration_directory'],
                                          s.general['iterations_structure']['train'],
                                          'classifier_{}'.format(fold_i))
        if not os.path.exists(new_classifier_dir):
            os.makedirs(new_classifier_dir)
        # convert classifier settings into list
        args = ['opencv_traincascade.exe']
        args.extend(['-data', new_classifier_dir])
        args.extend(['-vec', positives_xml_path])
        args.extend(['-bg', negatives_dat_path])
        for key, value in s.haarClassiferArgs.iteritems():
            args.append('-' + key)
            args.append(str(value))
        num_pos = int(positives_numsamples * s.classifer_training['positive_sample_ratio'])
        num_neg = min(negatives_numsamples, int(positives_numsamples * s.classifer_training['positive_sample_ratio'] * s.classifer_training['neg_pos_ratio']))
        args.extend(['-numPos', str(num_pos)])
        args.extend(['-numNeg', str(num_neg)])

        print args
        # Call script to create train classifier
        # logfile = open(os.path.join(current_iter_dir, 'log_training.txt'), 'w+')
        call(args=args, executable=os.path.join(s.general['opencv'], 'opencv_traincascade.exe'))
        # logfile.close()



    return 0
