"""
Reads:
 - 3D predictions
    - location: see output from previous step
    - format: see output from previous step
    - read with: TO BE DEFINED
Tasks:
 - Cluster predictions
Writes:
 - 3D prediction clusters
   - Coordinates
   - Standard deviation (assuming 3D normal distribution)
   - List of 2D Clusters involved
   ----------------
   - location: [project home directory]/7_cluster_3d/
   - format: TO BE DEFINED
Tools:
 - Sklearn.cluster.dbscan

"""

import sklearn.cluster as skit
import sklearn.neighbors as neighbors
import os
import numpy as np
import pickle
from sklearn import linear_model as sklim
from shapely.geometry import Point
from shapely.ops import cascaded_union
import csv
import sys
import default_settings as settings

buffer_dist = 0.2


def cluster_3d(config, debug):
    # Where to get points from
    points_file = os.path.join(config['iteration_directory'],
                               settings.general['iterations_structure']['cast'], '3dpoints.csv')

    # Where to save clusters
    save_to_directory = os.path.join(config['iteration_directory'],
                                     settings.general['iterations_structure']['cluster'])
    clusters_file = os.path.join(save_to_directory, '3dclusters.csv')

    # points = np.loadtxt(points_file)

    points = []
    buffers = []
    clusters = []

    # read data into a list of shapely points
    with open(points_file, 'rb') as f:
        reader = csv.DictReader(f, delimiter=' ')
        for row in reader:
            point = Point(float(row['x']), float(row['y']), float(row['z']))
            points.append({
                'geom': point,
                'score': row['score'],
                'image': row['image']
            })
            # create buffer
            buffer = point.buffer(buffer_dist)
            buffers.append(buffer)

    # do union
    dissolved = cascaded_union(buffers)

    # count clusters
    cluster_count = len(dissolved)
    if debug:
        print str(cluster_count) + ' clusters found'

    # load cluster classifier
    # Classify clusters
    if settings.general['mode'] == 'detection':
        cluster_classifier = pickle.load(open(settings.detection['trained_cluster_classifier'], 'rb'))

    # describe clusters
    # Loop through clusters and analyze
    for area in dissolved:

        cluster = {
            'count': 0,
            'avg_score': 1,
            'max_score': 0,
            'area': area.area,
            'x': area.centroid.x,
            'y': area.centroid.y,
            'density': 0
        }
        # Add points to clusters
        for point in points:
            if area.contains(point['geom']):
                cluster['avg_score'] = (cluster['avg_score'] * cluster['count'] + float(point['score'])) / (
                    cluster['count'] + 1)
                cluster['max_score'] = max(cluster['max_score'], float(point['score']))
                cluster['count'] += 1
                # cluster['points'].append(point)

        # compute density
        cluster['density'] = cluster['count'] / cluster['area']
        # clusters.append(cluster)
        clusters.append(cluster)

        # Classify clusters
        if settings.general['mode'] == 'detection':
            cluster['is_obj'] = cluster_classifier.predict(np.array([(cluster['count'],
                                                                        cluster['area'],
                                                                        cluster['density'],
                                                                        cluster['avg_score'],
                                                                        cluster['max_score'])]))[0]

    with open(clusters_file, 'wb') as csv_file:
        cluster_writer = csv.DictWriter(csv_file, delimiter=' ', fieldnames=clusters[0].keys(),
                                        quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Write header
        cluster_writer.writeheader()

        # Write clusters
        cluster_writer.writerows(clusters)

    return 0


















    # # Clean data from outliers
    # if debug:
    #     print 'removing outliers...'
    # threshold = 2
    # n_neighbors = 5
    # distances, indexes = np.array(neighbors.NearestNeighbors(radius=0.4, n_neighbors=n_neighbors).fit(points).kneighbors(points))
    # # print weight_graph
    # outliers = np.array(map(lambda point : point[1] > threshold, distances))
    # # outliers = [row[1] for row in distances] > threshold
    # print outliers
    # # points_with_label = np.append(points, np.transpose([outliers]), axis=1)
    # # filtered_points = filter(lambda p: p[3] is not True, points_with_label)
    # filtered_points = points[not outliers]
    #
    # np.savetxt(os.path.join(save_to_directory, '3dfiltered.csv'), filtered_points)
    #
    # return 1
    #
    # # Compute clusters
    # if debug:
    #     print 'scanning clusters...'
    #
    # # MEANSHIFT
    # bandwidth = skit.estimate_bandwidth(points, quantile=0.001, n_samples=None)
    # centroids_ms = skit.MeanShift(bandwidth=bandwidth, bin_seeding=True).fit(points).cluster_centers_
    #
    # # DBSCAN
    # point_clusters_dbs = skit.DBSCAN(eps=3, min_samples=5).fit_predict(points)
    # points_with_clusters = np.append(points, np.transpose([point_clusters_dbs]), axis=1)
    # centroids_dbscan = np.zeros([1,4])
    #
    # for cluster_name in range(len(point_clusters_dbs)):
    #     cluster = np.array(filter(lambda p : p[3] == cluster_name, points_with_clusters))
    #     if len(cluster) > 0:
    #         centroid = np.mean(cluster, axis=0)
    #         centroids_dbscan = np.append(centroids_dbscan, [centroid], axis=0)
    #
    # np.savetxt(os.path.join(save_to_directory, 'weight_matrix.csv'), weight_graph)
    # np.savetxt(os.path.join(save_to_directory, '3dclusters_meanshift.csv'), centroids_ms)
    # np.savetxt(os.path.join(save_to_directory, '3dclusters_dbscan.csv'), centroids_dbscan)
