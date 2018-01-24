"""
Args:
 - evaluate results based on truth file
Writes:
 - each point or cluster candidate is evaluated and tagged as correct or incorrect
   - location: [project home directory]/10_evaluate_candidates/
   - format: TO BE DEFINED
Tasks:
 - Evaluate the results of the object detection by comparing the 3D candidates to the reference data
 - Evaluate the results of the statistical binary model

"""

import csv
import os
import pandas as pd
from shapely.geometry import Point
from shapely.ops import cascaded_union
import default_settings as settings
import datetime


# Todo: only evaluate classifier results within the working area in which positives were identified

def evaluate_candidates(config, debug):

    for fold_i in range(settings.general['folds']):
        print('-- FOLD {} --'.format(fold_i))
        # input files
        ground_truth_file = settings.inputs['ground_truth']
        clusters_file = os.path.join(config['iteration_directory'], settings.general['iterations_structure']['cluster'],
                                     '3dclusters_{}.csv'.format(fold_i))
        # output files
        clusters_eval_file = os.path.join(config['iteration_directory'],
                                          settings.general['iterations_structure']['evaluate'],
                                          '3dclusters_{}.csv'.format(fold_i))
        misses_file = os.path.join(config['iteration_directory'], settings.general['iterations_structure']['evaluate'],
                                   'misses_{}.csv'.format(fold_i))

        # Do evaluation
        evaluate_clusters(clusters_file, ground_truth_file, clusters_eval_file, misses_file, config['generation'])

    return 0


def evaluate_clusters(candidate_file, truth_file, clusters_eval_file, misses_file, generation):
    # Load data
    ground_truth = read_point_file(truth_file, delimiter=settings.inputs['ground_truth_csv_delimiter'])
    clusters = pd.read_csv(candidate_file)

    # Re-order clusters
    clusters.sort_values('total_score', ascending=False)
    # Add column value
    clusters['matched'] = False
    clusters['matched_id'] = 999

    # Do evaluation
    for i, cluster in clusters.iterrows():
        # create buffer
        buffer = Point(float(cluster['x']), float(cluster['y'])).buffer(float(settings.evaluation['acceptance_radius']))
        # check if a ground truth is within the point's buffer
        for gt in ground_truth:
            if gt['point'].within(buffer) & (not gt['matched']):
                clusters.set_value(i, 'matched', True)
                clusters.set_value(i, 'matched_id', gt['id'])
                gt['matched'] = True

    # write clusters
    clusters.to_csv(clusters_eval_file, index=False)

    # write misses
    misses_fields = ['x', 'y', 'matched']
    with open(misses_file, 'wb') as csv_file:
        result_writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=misses_fields,
                                       quotechar='"', quoting=csv.QUOTE_MINIMAL, extrasaction='ignore')
        result_writer.writeheader()
        # only write unmatched ground truths
        result_writer.writerows([p for p in ground_truth if not p['matched']])

    # Stats
    # candidates = len(clusters)
    # ground_truth_count = len(ground_truth)
    # hits = len(clusters[clusters['matched'] == True])
    # false_alerts = len(clusters[clusters['matched'] == False])
    # misses = len([p for p in ground_truth if not p['matched']])
    # print({
    #     'datetime': datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"),
    #     'generation': generation,
    #     'neighbors': settings.detection['classifier_min_neighbors'],
    #     'window_size': settings.detection['classifier_min_size'],
    #     'candidates': candidates,
    #     'ground_truth': ground_truth_count,
    #     'hits': hits,
    #     'false_alerts': false_alerts,
    #     'misses': misses,
    #     'precision': float(hits) / (float(candidates)),
    #     'recall': float(hits) / float(ground_truth_count)
    # })

    return 0


def read_point_file(filename, delimiter):
    points = []
    with open(filename, 'rb') as f:
        rows = csv.DictReader(f, delimiter=delimiter)
        for row in rows:
            row['point'] = Point(float(row['x']), float(row['y']))
            row['buffer'] = row['point'].buffer(float(settings.evaluation['acceptance_radius']))
            row['matched'] = False
            points.append(row)
    return points

