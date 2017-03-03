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
from shapely.geometry import Point
from shapely.ops import cascaded_union
import default_settings as settings
import datetime

# Todo: only evaluate classifier results within the working area in which positives were identified

def evaluate_candidates(config, debug):
    if not settings.evaluation['do_evaluation']:
        return 0

    # 1. LOAD GROUND TRUTH

    ground_truth_file = settings.inputs['ground_truth']

    # 2. TEST WHETHER CANDIDATES FALL WITHIN BUFFERS OF GROUND TRUTH
    stats_file_points = os.path.join(settings.general['working_directory'], 'stats_points.txt')
    stats_file_clusters = os.path.join(settings.general['working_directory'], 'stats_clusters.txt')
    # a. point candidates
    points_in = os.path.join(config['iteration_directory'], settings.general['iterations_structure'][3], '3dpoints.csv')
    points_out = os.path.join(config['iteration_directory'], settings.general['iterations_structure'][5],
                              '3dpoints_evaluated.csv')
    points_out_truth = os.path.join(config['iteration_directory'], settings.general['iterations_structure'][5],
                                    '3dpoints_truth_evaluated.csv')
    # Do evaluation
    evaluate_file(points_in, ground_truth_file, points_out, points_out_truth, stats_file_points, config['generation'])

    # =====================================
    # b. clusters
    clus_in = os.path.join(config['iteration_directory'], settings.general['iterations_structure'][4], '3dclusters.csv')
    clus_out = os.path.join(config['iteration_directory'], settings.general['iterations_structure'][5],
                            '3dclusters_evaluated.csv')
    clus_out_truth = os.path.join(config['iteration_directory'], settings.general['iterations_structure'][5],
                                  '3dclusters_truth_evaluated.csv')

    # Do evaluation
    evaluate_file(clus_in, ground_truth_file, clus_out, clus_out_truth, stats_file_clusters, config['generation'])

    return 0


def evaluate_file(candidate_file, truth_file, file_out, file_out_truth, stats_file, generation):
    positives = []
    evaluated_clusters = []
    buffers_truth = []
    buffers_candidates = []

    # create buffers
    truth_pts, truth_bfrs = create_buffer(truth_file, delimiter=settings.inputs['ground_truth_csv_delimiter'])
    candidate_pts, candidate_bfrs = create_buffer(candidate_file, delimiter=' ')

    # Do evaluation
    candidate_hits, candidate_misses = evaluate_points(candidate_pts, truth_bfrs, file_out)
    truth_hits, truth_misses = evaluate_points(truth_pts, candidate_bfrs, file_out_truth)

    # Stats
    new_stats = {
        'datetime': datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"),
        'generation': generation,
        'accuracy': float(candidate_hits) / (float(candidate_hits) + float(candidate_misses)),
        'detection_rate': float(truth_hits) / (float(truth_hits) + float(truth_misses))
    }

    # Write to file
    write_header = False
    if not os.path.isfile(stats_file):
        write_header = True

    with open(stats_file, 'a+') as f:
        result_writer = csv.DictWriter(f, delimiter=';', fieldnames=new_stats.keys(),
                                       quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if write_header:
            result_writer.writeheader()
        result_writer.writerows([new_stats])

    return 0


def create_buffer(points_csv, delimiter):
    buffers = []
    points = []
    with open(points_csv, 'rb') as f:
        rows = csv.DictReader(f, delimiter=delimiter)
        for row in rows:
            point = Point(float(row['x']), float(row['y']))
            buffers.append(point.buffer(float(settings.evaluation['acceptance_radius'])))
            points.append(row)

    # Union all buffers into one multipolygon
    buffers = cascaded_union(buffers)

    return points, buffers


def evaluate_points(points, buffers, evaluated_pts_file):
    evaluated = []
    hits = 0
    misses = 0

    for row in points:
        # Test whether the candidate is close to ground truth
        point = Point(float(row['x']), float(row['y']))
        if point.within(buffers):
            row['is_match'] = 1
            hits += 1
        else:
            row['is_match'] = 0
            misses += 1
        evaluated.append(row)

    # Write evaluated candidates to file
    with open(evaluated_pts_file, 'wb') as csv_file:
        result_writer = csv.DictWriter(csv_file, delimiter=' ', fieldnames=evaluated[0].keys(),
                                       quotechar='"', quoting=csv.QUOTE_MINIMAL)
        result_writer.writeheader()
        result_writer.writerows(evaluated)

    # Compute statistics

    return hits, misses
