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
import random
import pandas as pd
import helpers
import numpy as np
import os
import sys
from scipy import ndimage
from scipy import misc
from tkMessageBox import *


REDO_PROJ = False


def extract_initial_samples(config, debug, settings):
    random.seed(12345)
    output_file_points = os.path.join(settings['general']['working_directory'],
                                      settings['general']['preparations_subdir'],
                                      settings['general']['preparations_structure']['extract'],
                                      'initial_samples.csv')
    image_sample_dir = os.path.join(settings['general']['working_directory'],
                                    settings['general']['preparations_subdir'],
                                    settings['general']['preparations_structure']['extract'],
                                    'images')
    # read data from file
    dem_dataset = gdal.Open(settings['inputs']['demfile'])
    dem_rasterband = dem_dataset.GetRasterBand(1)
    dem_geotransform = dem_dataset.GetGeoTransform()
    points = pd.read_csv(settings['inputs']['ground_truth']).append(pd.read_csv(settings['inputs']['negatives']))

    # Only reproject points if required
    if os.path.exists(output_file_points) & (not REDO_PROJ):
        print('loading image coordinates for each sample')
        valid_2d = pd.read_csv(output_file_points)
    else:
        # Get point data with elevation data applied
        print ('fetching elevation coordinates')
        points_3d = get_3d_points(dem_rasterband, dem_geotransform, points)

        # Read image calibration parameters
        params = helpers.read_camera_params(settings['inputs']['camera_xyz_offset'], settings['inputs']['camera_params'])

        # Transform and save samples
        print ('extracting image coordinates for each sample')
        valid_2d = get_2d(points3d=points_3d,
                          params=params,
                          output_file=output_file_points,
                          rating_threshold=settings['training_images']['negatives_rating_threshold'],
                          settings=settings)

    # Clip samples
    print ('clipping samples')
    extract_candidate_images(image_sample_dir, valid_2d, debug, settings)

    # Todo: manually verify that the samples are correct.
    return 0


def get_2d(points3d, params, output_file, settings, rating_threshold=0.01):
    points2d = pd.DataFrame()
    # For each image, apply transformation and save the points
    for camera in params:
        # pMatrix = camera['camera_matrix']
        camera_name = camera['camera_name'].split('.')[0]
        KRt = np.dot(np.dot(camera['K'], camera['R']), camera['t'])

        for i, point in points3d.iterrows():
            # make a copy
            # point = pd.DataFrame(point)
            # Transform
            X = np.array([[float(point.x)], [float(point.y)], [float(point.z)]])
            # ===================================================
            # project boundary to image coordinates vec = KRX-KRt
            [[img_x], [img_y], [img_z]] = np.dot(np.dot(camera['K'], camera['R']), X) - KRt
            # ===================================================

            u = float(settings['inputs']['image_pixel_x']) * img_x / img_z
            v = float(settings['inputs']['image_pixel_y']) * img_y / img_z

            upix = int(u * 100000)
            vpix = int(v * -100000)

            # check if point is within image
            is_in_img = is_in_bbox(upix, vpix, settings['training_images']['width'],
                                   settings['inputs']['image_width_px'] - settings['training_images']['width'],
                                   settings['training_images']['height'],
                                   settings['inputs']['image_height_px'] - settings['training_images']['height'])
            if is_in_img & ((point.rating >= rating_threshold) | point.matched):
                # save point
                points2d = points2d.append(pd.DataFrame({
                    'id': [point.id],
                    'img_x': [upix],
                    'img_y': [vpix],
                    'image': [camera_name],
                    'x': [point.x],
                    'y': [point.y],
                    'z': [point.z],
                    'rating': [point.rating],
                    'matched': [point.matched]
                }))

    points2d.to_csv(output_file, index=False)

    return points2d


def get_3d_points(dem_rasterband, dem_geotransform, points):
    # read points and apply elevation
    points3d = pd.DataFrame(points)
    points3d['z'] = points3d.apply(lambda pt: get_elevation(pt, dem_geotransform, dem_rasterband), axis=1)

    return points3d


def get_elevation(point, dem_geotransform, dem_rasterband):
    return float(dem_rasterband.ReadAsArray(
        int((point.x - dem_geotransform[0]) / dem_geotransform[1]),
        int((point.y - dem_geotransform[3]) / dem_geotransform[5]), 1, 1)[0][0])


def is_in_bbox(x, y, xmin, xmax, ymin, ymax, buffer=200):
    return (x < (xmax - buffer)) & (x > (xmin + buffer)) & (y < (ymax - buffer)) & (y > (ymin + buffer))


def extract_candidate_images(training_image_dir, points, debug, settings):
    # Sample extraction

    # Check that directories exist and delete any content
    for directory in ['positives/img', 'negatives/img']:
        d = os.path.join(training_image_dir, directory)
        if not os.path.exists(d):
            os.makedirs(d)
            if debug:
                print "directory created: {directory}".format(directory=d)
        delete_all_files(d)
    pass

    # PROCESS POINTS
    # load points
    candidates = points

    # load blacklist
    blacklist = pd.read_csv(settings['inputs']['ground_truth_blacklist'])

    # Make a list of already seen negatives
    already_seen_negatives = []
    # for each image, extract samples from that image.
    for image_name in list(candidates.image.unique()):
        sys.stdout.write('.')
        # Load image
        image_file = os.path.join(settings['inputs']['undistorted_image_folder'],
                                  image_name + '.' + settings['inputs']['image_extension'])
        # image_file = os.path.join("Q:/Messdaten/floodVisionData/side_2016_raycast/data/training_adliswil/original_images",
        #                           image_name + '.jpg') #  '+settingsettings['inputs']['image_extension'])
        if not os.path.isfile(image_file):
            continue

        image = ndimage.imread(image_file,
                               flatten=True)
        # Process candidates from that image
        filtered_cd = candidates[candidates['image'] == image_name]
        # Get blacklist for image
        filtered_blacklist = blacklist[blacklist['img'] == image_name]

        # Go through all candidates
        for index, cd in filtered_cd.iterrows():
            # if is ground truth and not in blacklist
            if cd.matched and (cd['id'] not in list(filtered_blacklist.id)):
                # Clip image
                make_samples(
                    point=cd,
                    image=image,
                    is_positive=cd['matched'],
                    save_dir=training_image_dir,
                    settings=settings
                )
            elif (not cd.matched) and (cd.id not in already_seen_negatives):
                already_seen_negatives.append(cd.id)
                # Clip image
                make_samples(point=cd,
                             image=image,
                             is_positive=cd['matched'],
                             save_dir=training_image_dir,
                             settings=settings
                             )

    print 'done clipping. Writing dat files'
    showwarning(title='Verify samples', message='Please verify that the sample images in %s are correct.' %
                                                training_image_dir)

    # save list of file names for negatives (positives done in next step)
    img_list = os.listdir(os.path.join(training_image_dir, 'negatives', 'img'))
    with open(os.path.join(training_image_dir, 'negatives', "bg.txt"), "w+") as list_file:
        # first shuffle list
        random.shuffle(img_list)
        for path in img_list:
            list_file.writelines(os.path.join(training_image_dir, 'negatives', 'img', "{}\n".format(path)))
        list_file.close()

    return 0


def make_samples(point, image, is_positive, save_dir, settings):
    # How much to augment the data
    if is_positive:
        num_variations = settings['sample_preparations']['augmentation_ratio_positives']
    else:
        num_variations = settings['sample_preparations']['augmentation_ratio_negatives']

    # Make box that is 1.5 times the final sample size
    w = int(settings['training_images']['width'] * 1.5)
    h = int(settings['training_images']['height'] * 1.5)
    box_left = point.img_x - w / 2
    box_upper = point.img_y - h / 2
    box_right = point.img_x + w / 2
    box_lower = point.img_y + h / 2
    # crop it
    crop1 = image[box_upper:box_lower, box_left:box_right]
    for i in range(num_variations):
        transformed = np.copy(crop1)
        # select transformations randomly
        do_hflip = (random.randint(0, 1) == 1)
        do_vflip = (random.randint(0, 1) == 1)
        rotation = random.choice([random.uniform(0, 360), 0, 90])

        # do transformations
        transformed = ndimage.rotate(transformed, rotation, reshape=False)
        if do_hflip:
            transformed = np.fliplr(transformed)
        if do_vflip:
            transformed = np.flipud(transformed)

        # recrop to final size
        w_big = int(transformed.shape[0])  # width of transformed image
        start = int((w_big - settings['training_images']['width'])/2)
        end = int((w_big + settings['training_images']['width'])/2)

        crop2 = transformed[start:end, start:end]

        # Based on whether it is a hit or miss, save it in the right place
        subdir = 'positives/img' if is_positive else 'negatives/img'
        # Save image and write filename
        filename = '{}_{}_({:1.3f})-{}.jpg'.format(point['id'], point['image'], point['rating'], i)
        misc.imsave(os.path.join(save_dir, subdir, filename), crop2)


def delete_all_files(folder):
    files = os.listdir(folder)
    if len(files) > 0:
        print('deleting files in {}'.format(folder))
    for the_file in files:
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
