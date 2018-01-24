"""
Clip each image with its corresponding projected boundary file

Reads:
 - 2D boundary multipolygon file for each camera
    - location: see output from previous step
    - format: see output from previous step
    - library: OGR
 - undistorted image for each camera
    - location: defined by user in settings file
    - format: TIFF image
    - library: GDAL
Tasks:
 - clip each image using the corresponding multipolygon
Tools:
 - rasterclipper.py
Writes:
 - N clipped images, where N is the number of cameras
    - location: [project home directory]/3_clip_images_2d/[image name].tif
    - format: TIFF image
"""

import os
from glob import glob
from subprocess import call
import default_settings as settings


def clip_images_2d(config, debug):
    """Clips images with the projected road boundary information"""
    # todo: read image resolution from tiff metadata

    output_folder = os.path.join(settings.general['working_directory'],
                                 settings.general['preparations_subdir'],
                                 settings.general['preparations_structure']['clip'])

    # Loop through files of projected boundaries
    boundary_folder = os.path.join(settings.general['working_directory'],
                                   settings.general['preparations_subdir'],
                                   settings.general['preparations_structure']['proj_2d'])

    # Count files to work through:
    boundary_files = glob(os.path.join(boundary_folder, '*.json'))
    file_count = len(boundary_files)
    print('{x} images found'.format(x=file_count))
    if file_count == 0:
        raise NameError('no boundary files found.')
    file_index = 1
    processed = 0
    for boundary_file in boundary_files:
        if debug:
            print 'clipping file ' + str(file_index) + ' of ' + str(file_count)
        file_index += 1
        image_file = os.path.join(settings.inputs['undistorted_image_folder'], os.path.basename(boundary_file).split('__')[0] + '.'+settings.inputs['image_extension'])
        image_file_clipped = os.path.join(output_folder, os.path.basename(boundary_file).split('__')[0] + '.'+settings.inputs['image_extension'])
        if os.path.isfile(image_file):
            try:
                call(
                    ['gdalwarp.exe',
                     '-q',
                     '-cutline', boundary_file,
                     '-tr', '1e-05', '1e-05',
                     '-of', 'GTIFF',
                     '-overwrite',
                     image_file,
                     image_file_clipped],
                    executable=settings.general['gdalwarp'])
            except:
                raise NameError('Error with reprojection')
            processed += 1
    if processed == 0:
        raise NameError('no images processed')

    return 0
    pass
