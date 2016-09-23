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
import os
import numpy as np

def cluster_3d(settings, structure, debug):

    # Where to get points from
    points_file = os.path.join(settings.values['Global']['working_directory'], structure[5], '3dpoints.csv')

    # Where to save clusters
    clusters_file = os.path.join(settings.values['Global']['working_directory'], structure[6], '3dclusters.csv')

    points = np.loadtxt(points_file)

    # Where to store cluster centroids
    centroids = np.zeros([1,4])


    # Compute clusters
    if debug:
        print 'scanning clusters...'
    point_clusters_dbs = skit.DBSCAN(eps=3, min_samples=5).fit_predict(points)
    # point_clusters_ms = skit.MeanShift(eps=3, min_samples=5).fit(points)

    points_with_clusters = np.append(points, np.transpose([point_clusters_dbs]), axis=1)

    for cluster_name in range(len(point_clusters_dbs)):
        cluster = np.array(filter(lambda p : p[3] == cluster_name, points_with_clusters))
        if len(cluster) > 0:
            centroid = np.mean(cluster, axis=0)
            centroids = np.append(centroids, [centroid], axis=0)

    np.savetxt(clusters_file, centroids)

