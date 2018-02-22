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
import pandas as pd


def cluster_3d(config, debug, settings):
    # Where to save clusters
    save_to_directory = os.path.join(config['iteration_directory'],
                                     settings['general']['iterations_structure']['cluster'])

    for fold_i in range(settings['general']['do_folds']):
        print('-- FOLD {} --'.format(fold_i))
        # Where to get points from
        points_file = os.path.join(config['iteration_directory'],
                                   settings['general']['iterations_structure']['cast'], '3dpoints_{}.csv'.format(fold_i))
        clusters_file = os.path.join(save_to_directory, '3dclusters_{}.csv'.format(fold_i))

        points_df = pd.read_csv(points_file)

        # do clustering
        clusters_df = cluster_dbscan(points_df,
                                     neighborhood_size=settings['clustering_3d']["neighborhood_size"],
                                     min_samples=settings['clustering_3d']["min_samples"])

        # save
        clusters_df.to_csv(clusters_file, index=False)

        # check number of clusters is sufficient
        if len(clusters_df) < 70:
            return 2

    return 0


def cluster_dbscan(points, neighborhood_size, min_samples):
    '''
    Args:
        point_coords: DataFrame of points
        neighborhood_size: size of cluster
        min_samples:

    Returns:
        clusters as df
    '''

    clusters = pd.DataFrame()

    # If no z dim exists, create it
    if 'z' not in points.columns:
        points['z'] = 0

    # If no image name exists, create it
    if 'image' not in points.columns:
        points['image'] = 'ortho'

    # If no score col exists, rename n col
    if 'score' not in points.columns:
        if 'n' in points.columns:
            points = points.rename(index=str, columns={'n': 'score'})


    # Do clustering
    point_coords = points.as_matrix(['x', 'y', 'z'])
    cluster_labels = skit.DBSCAN(eps=neighborhood_size, min_samples=min_samples).fit_predict(point_coords)
    points['cluster_label'] = cluster_labels

    # compute cluster stats
    grouped = points.groupby('cluster_label')

    print('{n} clusters found'.format(n=len(grouped)))
    for name, group in grouped:
        if name >= 0:  # The first group contains unclustered points
            # compute numDetection stats
            img_grouped = group.groupby('image').aggregate(len)
            ns = range(0, 50, 2)
            neighbor_hist = list(pd.cut(np.array(img_grouped.cluster_label), ns, right=True).value_counts())

            # Find max number of neighbors
            n_max = 0
            for idx, item in enumerate(neighbor_hist):
                if item != 0:
                    n_max = ns[idx]
            # Find avg number of neighbors
            n_avg = float(np.dot(neighbor_hist, ns[1:]))/np.sum(neighbor_hist)

            # Area
            area = (max(group.x) - min(group.x) + neighborhood_size) * (
                max(group.y) - min(group.y) + neighborhood_size)
            cluster = {
                'count': [len(group)],
                'image_count': [len(group.image.unique())],
                'total_score': [sum(group.score)],
                'avg_score': [float(sum(group.score))/len(group)],
                'max_score': [max(group.score)],
                'area': [area],  # area of cluster bbox
                'x': [float(sum(group.x))/len(group)],
                'y': [float(sum(group.y))/len(group)],
                'z': [float(sum(group.z))/len(group)],
                'density': [len(group)/area],
                'N_max': n_max,
                'N_avg': n_avg
            }
            for i in range(len(neighbor_hist)):
                cluster['n'+str(ns[i])] = [neighbor_hist[i]]

            # append to main dataframe
            clusters = clusters.append(pd.DataFrame(cluster))

    return clusters
