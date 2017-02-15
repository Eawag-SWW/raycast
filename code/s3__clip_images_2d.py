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
from subprocess import call
import default_settings as settings


def clip_images_2d(structure, debug):
    """Clips images with the projected road boundary information"""
    # todo: read image resolution from tiff metadata

    output_folder = os.path.join(settings.general['working_directory'], structure[2])

    # Loop through files of projected boundaries
    boundary_folder = os.path.join(settings.general['working_directory'], structure[1])

    # Count files to work through:
    file_count = len([name for name in os.listdir('.') if os.path.isfile(name)])
    file_index = 1

    for boundary_file in os.listdir(boundary_folder):
        if debug:
            print 'clipping file ' + str(file_index) + ' of ' + str(file_count)
        file_index += 1
        image_file = os.path.join(settings.inputs['undistorted_image_folder'], boundary_file.split('.')[0]+'.tif')
        image_file_clipped = os.path.join(output_folder, boundary_file.split('.')[0]+'.tif')
        if os.path.isfile(image_file):
            call(
                ['gdalwarp.exe',
                 '-q',
                 '-cutline', os.path.join(boundary_folder, boundary_file),
                 '-tr', '1e-05', '1e-05',
                 '-of', 'GTIFF',
                 '-overwrite',
                 image_file,
                 image_file_clipped],
                executable=settings.general['gdalwarp'])

            # os.system(settings.general['gdalwarp'] + ' -q' + ' -cutline ' + os.path.join(boundary_folder, boundary_file) +
            #       ' -tr 1e-05 1e-05' + ' -of GTIFF' + ' ' + image_file + ' ' + image_file_clipped)


    return 0
    pass
