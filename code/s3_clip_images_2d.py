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
    - location: [project home directory]/3_clip_images_2d/[image name]_clipped.tif
    - format: TIFF image
"""

import helpers
import os
import gdal
import rasterclipper


def clip_images_2d(settings, structure, debug):
    """Clips images with the projected road boundary information"""


    output_folder = os.path.join(settings.values['Global']['working_directory'], structure[2])

    # Loop through files of projected boundaries
    boundary_folder = os.path.join(settings.values['Global']['working_directory'], structure[1])

    for boundary_file in os.listdir(boundary_folder):
        image_file = os.path.join(settings.values['Inputs']['undistorted_image_folder'],boundary_file.split('.')[0]+'tif')
        try:
            with gdal.Open(image_file, gdal.GA_Readonly) as rast:
                array = rasterclipper.clip_raster(rast, os.path.join(boundary_folder, boundary_file))
        except:
            print 'error'

    pass