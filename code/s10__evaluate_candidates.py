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


def evaluate_candidates(structure, debug):
    if not settings.evaluation['do_evaluation']:
        return 0

    positives = []
    buffers = []

    # evaluated_results_file = os.path.join(settings.general['working_directory'], structure[9], '3dclusters_evaluated.csv')

    # 1. LOAD GROUND TRUTH

    ground_truth_file = settings.inputs['ground_truth']
    # read data and create buffers
    with open(ground_truth_file, 'rb') as f:
        reader = csv.DictReader(f, delimiter=settings.inputs['ground_truth_csv_delimiter'])
        for row in reader:
            point = Point(float(row['x']), float(row['y']))
            positives.append(point)
            # create buffer

            buffers.append(point.buffer(float(settings.evaluation['acceptance_radius'])))

    # Union all buffers into one multipolygon
    buffers = cascaded_union(buffers)

    # 2. TEST WHETHER CANDIDATES FALL WITHIN BUFFERS OF GROUND TRUTH
    # a. point candidates
    evaluate_file(os.path.join(settings.general['working_directory'], structure[5], '3dpoints.csv'),
                  buffers,
                  os.path.join(settings.general['working_directory'], structure[9], '3dpoints_evaluated.csv'))
    # b. clusters
    evaluate_file(os.path.join(settings.general['working_directory'], structure[6], '3dclusters.csv'),
                  buffers,
                  os.path.join(settings.general['working_directory'], structure[9], '3dclusters_evaluated.csv'))

    return 0


def evaluate_file(candidate_file, buffered_truth, file_out):
    evaluated_clusters = []
    # Load candidates
    with open(candidate_file, 'rb') as f:
        reader = csv.DictReader(f, delimiter=' ')
        for row in reader:
            # Test whether the candidate is close to ground truth
            point = Point(float(row['x']), float(row['y']))
            row['is_match'] = 1 if point.within(buffered_truth) else 0
            evaluated_clusters.append(row)

        # Write evaluated candidates to file
        with open(file_out, 'wb') as csv_file:
            result_writer = csv.DictWriter(csv_file, delimiter=' ', fieldnames=evaluated_clusters[0].keys(),
                                           quotechar='"', quoting=csv.QUOTE_MINIMAL)
            result_writer.writeheader()
            result_writer.writerows(evaluated_clusters)

    return 0
