"""
Args:
 - evaluate results based on truth file
Writes:
 - each cluster candidate is evaluated and tagged as correct or incorrect
   - location: [project home directory]/10_evaluate_candidates/
   - format: TO BE DEFINED
Tasks:
 - Evaluate the results of the object detection by comparing the 3D candidates to the reference data
 - Assign cluster to train/test groups

"""

import csv
import os
import pandas as pd
from shapely.geometry import Point
from numpy import random
import datetime


# Todo: only evaluate classifier results within the working area in which positives were identified

def evaluate_candidates(config, debug, settings):

    for fold_i in range(settings['general']['do_folds']):
        print('-- FOLD {} --'.format(fold_i))
        # input files
        ground_truth_file = settings['inputs']['ground_truth']
        clusters_file = os.path.join(config['iteration_directory'], settings['general']['iterations_structure']['cluster'],
                                     '3dclusters_{}.csv'.format(fold_i))
        train_list = os.path.join(settings['general']['working_directory'],
                                  settings['general']['preparations_subdir'],
                                  settings['general']['preparations_structure']['folds'],
                               'gt_train_{}.csv'.format(fold_i))
        test_list = os.path.join(settings['general']['working_directory'],
                                 settings['general']['preparations_subdir'],
                                 settings['general']['preparations_structure']['folds'],
                               'gt_test_{}.csv'.format(fold_i))
        # output files
        out_clusters_train_file = os.path.join(config['iteration_directory'],
                                          settings['general']['iterations_structure']['evaluate'],
                                          '3dclusters_train_{}.csv'.format(fold_i))
        out_clusters_test_file = os.path.join(config['iteration_directory'], settings['general']['iterations_structure']['evaluate'],
                                   '3dclusters_test_{}.csv'.format(fold_i))

        # Do evaluation
        evaluate_clusters(clusters_file, ground_truth_file, out_clusters_train_file, out_clusters_test_file, train_list, test_list, settings)

    return 0


def evaluate_clusters(candidate_file, truth_file, out_clusters_train_file, out_clusters_test_file, train_list, test_list, settings):
    # Load data
    ground_truth = read_point_file(truth_file, delimiter=settings['inputs']['ground_truth_csv_delimiter'], settings=settings)
    clusters = pd.read_csv(candidate_file)
    gt_train = pd.read_csv(train_list)
    gt_test = pd.read_csv(test_list)

    # Re-order clusters (this is important)
    clusters.sort_values(['image_count', 'count'], ascending=False)
    # Add column value
    clusters['matched'] = False
    clusters['matched_id'] = 999
    clusters['missed'] = False

    # Dataframe of misses
    misses = pd.DataFrame(ground_truth, columns=['x', 'y', 'id'])
    misses.columns.values[2] = 'matched_id'
    misses.matched_id = pd.to_numeric(misses.matched_id)
    # Add column value
    misses['matched'] = True
    misses['missed'] = True

    # Do evaluation
    for i, cluster in clusters.iterrows():
        # create buffer
        buffer = Point(float(cluster['x']), float(cluster['y'])).buffer(float(settings['evaluation']['acceptance_radius']))
        # check if a ground truth is within the point's buffer
        for gt in ground_truth:
            if gt['point'].within(buffer) & (not gt['matched']):
                clusters.set_value(i, 'matched', True)
                clusters.set_value(i, 'matched_id', gt['id'])
                # remove matched ground truth from misses
                misses = misses[misses.matched_id != gt['id']]

    # Combine misses and clusters
    clusters_and_misses = clusters.append(misses, ignore_index=True)

    # Separate train and test positive clusters
    train_positives = clusters_and_misses[clusters_and_misses.matched_id.isin(gt_train.id)]
    test_positives = clusters_and_misses[clusters_and_misses.matched_id.isin(gt_test.id)]

    # Divide false positives randomly according to folds ratio
    false_alerts = clusters_and_misses[~clusters_and_misses.matched]
    false_alert_train_mask = random.rand(len(false_alerts)) < float(settings['general']['folds']-1)/settings['general']['folds']
    train_negatives = false_alerts[false_alert_train_mask]
    test_negatives = false_alerts[~false_alert_train_mask]

    # merge positives and negatives
    train_clusters = train_positives.append(train_negatives, ignore_index=True)
    test_clusters = test_positives.append(test_negatives, ignore_index=True)

    # write clusters
    train_clusters.to_csv(out_clusters_train_file, index=False)
    test_clusters.to_csv(out_clusters_test_file, index=False)

    return 0


def read_point_file(filename, delimiter, settings):
    points = []
    with open(filename, 'rb') as f:
        rows = csv.DictReader(f, delimiter=delimiter)
        for row in rows:
            row['point'] = Point(float(row['x']), float(row['y']))
            row['buffer'] = row['point'].buffer(float(settings['evaluation']['acceptance_radius']))
            row['matched'] = False
            row['id'] = int(row['id'])
            points.append(row)
    return points

