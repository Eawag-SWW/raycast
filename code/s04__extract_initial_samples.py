"""
Reads:
 - Positions of sample positive and negative points for classifier training
 - Digital elevation model
 - transformation matrix for each image
 - Clipped images from previous step
Writes:
 - clipped sample images
Tasks:
 - Read points and elevation model
 - apply elevation to points based on elevation model
 - For each image
   - Read transformation info
   - Transform all points into the image space
   - extract and save samples extracted from images
"""

import gdal
import csv
import pandas as pd
import helpers
import numpy as np
import os
import default_settings as s
from s14__extract_candidate_images import *


def extract_initial_samples(config, debug):
    output_file_points = os.path.join(s.general['working_directory'],
                               s.general['preparations_subdir'],
                               s.general['preparations_structure']['extract'],
                               'initial_samples.csv')
    image_sample_dir = os.path.join(s.general['working_directory'],
                             s.general['preparations_subdir'],
                             s.general['preparations_structure']['extract'],
                             'images')
    # read data from file
    dem_dataset = gdal.Open(s.inputs['demfile'])
    dem_rasterband = dem_dataset.GetRasterBand(1)
    dem_geotransform = dem_dataset.GetGeoTransform()

    # Get point data with elevation data applied
    positive3D = get_3d_points(dem_rasterband, dem_geotransform, s.training_images['positives_file'],
                               delimiter=s.training_images['csv_delimiter'])
    negative3D = get_3d_points(dem_rasterband, dem_geotransform, s.training_images['negatives_file'],
                               delimiter=s.training_images['csv_delimiter'])

    # Read image calibration parameters
    params = helpers.read_camera_params(s.inputs['camera_xyz_offset'], s.inputs['camera_params'])

    # Transform and save samples
    positive2D = get_2d(points3d=positive3D, params=params, is_match=1)
    negative2D = get_2d(points3d=negative3D, params=params, is_match=0)

    with open(output_file_points, 'w') as f:
        result_writer = csv.DictWriter(f, delimiter=' ', fieldnames=positive2D[0].keys(),
                                       quotechar='"', quoting=csv.QUOTE_MINIMAL)
        result_writer.writeheader()
        result_writer.writerows(positive2D + negative2D)

    # Clip samples
    extract_candidate_images(config, debug, image_sample_dir, output_file_points)

    # Todo: manually verify that the samples are correct.
    return 0


def get_2d(points3d, params, is_match):
    points2d = []
    # For each image, apply transformation and save the points
    for camera in params:
        # pMatrix = camera['camera_matrix']
        camera_name = camera['camera_name'].split('.')[0]
        KRt = np.dot(np.dot(camera['K'], camera['R']), camera['t'])

        for point in points3d:
            # Transform
            X = np.array([[float(point['X'])], [float(point['Y'])], [float(point['Z'])]])
            # ===================================================
            # project boundary to image coordinates vec = KRX-KRt
            [[img_x], [img_y], [img_z]] = np.dot(np.dot(camera['K'], camera['R']), X) - KRt
            # ===================================================

            u = float(s.inputs['image_pixel_x']) * img_x / img_z
            v = float(s.inputs['image_pixel_y']) * img_y / img_z

            upix = int(u * 100000)
            vpix = int(v * -100000)

            # check if point is within image
            if is_in_bbox(upix, vpix, s.training_images['width'],
                          s.inputs['image_width_px'] - s.training_images['width'],
                          s.training_images['height'], s.inputs['image_height_px'] - s.training_images['height']):
                # save point
                points2d.append({
                    "image": camera_name,
                    "img_x": int(upix),
                    "img_y": int(vpix),
                    "x": point['X'],
                    "y": point['Y'],
                    "z": point['Z'],
                    "is_match": is_match
                })

    return points2d


def get_3d_points(dem_rasterband, dem_geotransform, pointfile, delimiter):
    # read points and apply elevation
    points3d = []
    with open(pointfile, 'rb') as f:
        rows = csv.DictReader(f, delimiter=delimiter)
        for row in rows:
            x = float(row['X'])
            y = float(row['Y'])
            px = int((x - dem_geotransform[0]) / dem_geotransform[1])
            py = int((y - dem_geotransform[3]) / dem_geotransform[5])
            z = float(dem_rasterband.ReadAsArray(px, py, 1, 1)[0][0])
            row['Z'] = z
            points3d.append(row)

    return points3d


def is_in_bbox(x, y, xmin, xmax, ymin, ymax):
    return (x < xmax) & (x > xmin) & (y < ymax) & (y > ymin)
