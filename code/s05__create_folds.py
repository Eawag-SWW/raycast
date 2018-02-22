'''
This function creates training and testing folds from the ground truth data.
Output:
- ground truth table for training and testing for each fold
- training image files for each fold
'''

import pandas as pd
from sklearn.model_selection import KFold
import random
import os.path as p
from glob import glob

def create_folds(config, debug, settings):
    random.seed(12345)
    # load ground truth file
    ground_truth = pd.read_csv(settings['inputs']['ground_truth'])

    # create folds
    k_fold = KFold(n_splits=settings['general']['folds'], shuffle=True, random_state=12345)

    # loop through folds and do business
    for i, (train_index, test_index) in enumerate(k_fold.split(ground_truth)):
        gt_train, gt_test = ground_truth.iloc[train_index], ground_truth.iloc[test_index]
        # save data
        gt_train.to_csv(p.join(settings['general']['working_directory'],
                               settings['general']['preparations_subdir'],
                               settings['general']['preparations_structure']['folds'],
                               'gt_train_' + str(i) + '.csv'), index=False)
        gt_test.to_csv(p.join(settings['general']['working_directory'],
                              settings['general']['preparations_subdir'],
                              settings['general']['preparations_structure']['folds'],
                              'gt_test_' + str(i) + '.csv'), index=False)
        # create image collections for classifier training
        thumbnails = []
        # find thumbnails for given sewer inlets
        for _, row in gt_train.iterrows():
            pattern = str(row['id']) + '_*.jpg'
            thumbnails += glob(p.join(settings['general']['working_directory'],
                                      settings['general']['preparations_subdir'],
                                      settings['general']['preparations_structure']['extract'],
                                      'images', 'positives', 'img',
                                      pattern))
        # shuffle thumbnails
        random.shuffle(thumbnails)
        # write to file
        with open(p.join(settings['general']['working_directory'],
                         settings['general']['preparations_subdir'],
                         settings['general']['preparations_structure']['folds'],
                         'info_' + str(i) + '.dat'), "w+") as list_file:
            for path in thumbnails:
                list_file.writelines("{} 1 0 0 {} {}\n".format(
                    p.join('..', settings['general']['preparations_structure']['extract'], 'images', 'positives', 'img', p.basename(path)),
                    settings['training_images']['width'], settings['training_images']['height']))
    return 0
