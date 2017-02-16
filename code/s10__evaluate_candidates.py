"""
Args:
 - 3D detection results
Writes:
 -
   - location: [project home directory]/9_assess_reliability/
   - format: TO BE DEFINED
Tasks:
 - Compute an overall reliability of each cluster by assigning weights to
   - 2D cluster statistics (number of hits, density of cluster)
   - 3D cluster statistics (number of hits, density of cluster, number of missing votes)

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
    evaluated_clusters = []

    evaluated_results_file = os.path.join(settings.general['working_directory'], structure[9], '3dclusters_evaluated.csv')

    # Load ground truth
    ground_truth_file = settings.inputs['ground_truth']
    # read data and create buffers
    with open(ground_truth_file, 'rb') as f:
        reader = csv.DictReader(f, delimiter=settings.inputs['ground_truth_csv_delimiter'])
        for row in reader:
            point = Point(float(row['x']), float(row['y']))
            positives.append(point)
            # create buffer

            buffers.append(point.buffer(float(settings.evaluation['acceptance_radius'])))

    # Union all buffers
    buffers = cascaded_union(buffers)

    # Load clusters
    clusters_file = os.path.join(settings.general['working_directory'], structure[6], '3dclusters.csv')
    # read data and create buffers
    with open(clusters_file, 'rb') as f:
        reader = csv.DictReader(f, delimiter=' ')
        for row in reader:
            point = Point(float(row['x']), float(row['y']))
            row['is_match'] = 1 if point.within(buffers) else 0
            evaluated_clusters.append(row)

        # Write to file
        with open(evaluated_results_file, 'wb') as csv_file:
            result_writer = csv.DictWriter(csv_file, delimiter=' ', fieldnames=evaluated_clusters[0].keys(),
                                           quotechar='"', quoting=csv.QUOTE_MINIMAL)
            result_writer.writeheader()
            result_writer.writerows(evaluated_clusters)



