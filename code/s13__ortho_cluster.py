'''
This function turns the image coordinates to geographic coordinates
'''


import os
import pandas as pd
from s10__cluster_3d import cluster_dbscan


def ortho_cluster(config, debug, settings):

    # Where to save clusters
    save_to_directory = os.path.join(config['iteration_directory'],
                                     settings['general']['iterations_structure']['ortho_cluster'])
    if not os.path.exists(save_to_directory):
        os.mkdir(save_to_directory)

    for fold_i in range(settings['general']['do_folds']):
        print('-- FOLD {} --'.format(fold_i))
        # Where to get points from
        points_dir = os.path.join(config['iteration_directory'],
                                   settings['general']['iterations_structure']['ortho_detect'],
                                   'fold_{}'.format(fold_i))
        points_file = os.path.join(
            points_dir,
            os.listdir(points_dir)[0]
        )
        clusters_file = os.path.join(save_to_directory, '3dclusters_{}.csv'.format(fold_i))

        points_df = pd.read_csv(points_file, sep=';')

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
