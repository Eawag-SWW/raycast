'''
This function turns the image coordinates to geographic coordinates
'''

from osgeo import gdal, gdalconst
import sys
import os
from glob import glob
import default_settings as s
import pandas as pd
from s09__cluster_3d import cluster_dbscan

def ortho_cluster(config, debug):

    # Where to save clusters
    save_to_directory = os.path.join(config['iteration_directory'],
                                     s.general['iterations_structure']['ortho_cluster'])
    if not os.path.exists(save_to_directory):
        os.mkdir(save_to_directory)

    for fold_i in range(s.general['do_folds']):
        print('-- FOLD {} --'.format(fold_i))
        # Where to get points from
        points_dir = os.path.join(config['iteration_directory'],
                                   s.general['iterations_structure']['detect_ortho'],
                                   'fold_{}'.format(fold_i))
        points_file = os.path.join(
            points_dir,
            os.listdir(points_dir)[0]
        )
        clusters_file = os.path.join(save_to_directory, '3dclusters_{}.csv'.format(fold_i))

        points_df = pd.read_csv(points_file, sep=';')

        # do clustering
        clusters_df = cluster_dbscan(points_df,
                                     neighborhood_size=s.clustering_ortho["neighborhood_size"],
                                     min_samples=s.clustering_ortho["min_samples"])

        # save
        clusters_df.to_csv(clusters_file, index=False)

    return 0
