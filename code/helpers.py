"""
Functions of general purpose
"""


def load_shape(filename, driver='ESRI Shapefile', debug=True):
    """
    Load a geometry supported by OGR
    :param filename: filename of geometry
    :param driver: format of file, such as 'GeoJSON' or 'ESRI Shapefile'
    :param debug: print out debug information?
    :return: datasource
    """
    import ogr
    import sys

    # Load points as a numpy array, in order to be evaluated

    driver_shp = ogr.GetDriverByName(driver)
    driver_shp.Register()
    datasource = driver_shp.Open(filename, 0)

    if datasource is None:
        print "Shapefile load FAILED"
        sys.exit(1)
    else:
        if debug: print "Shapefile loaded successfully: ", filename
    # TO DO: Test that it is a point file

    return datasource


def write_to_log(settings, line):
    """
    Writes a string to the log file
    :param settings: contains path to project root
    :param line: string to write to file
    :return: none
    """
    import os
    import datetime

    with open(os.path.join(settings.values['Global']['working_directory'], 'log.txt'),
              'a+') as log:  # a+ means add to file
        log.write('\n' + str(datetime.datetime.now()))
        log.write('\n' + line)
    pass


def read_camera_params(filename_offset, filename_params):
    """
    Read camera calibration parameters
    :param filename_offset: file path for offset information
    :param filename_params: file path for other calibration information
    :return: a list of dictionaries containing calibration parameters for each image
    """
    import numpy as np

    # make a list of dictionaries
    params = []

    # Read XYZ offset
    with open(filename_offset, 'r') as offsetfile:
        offset = map(float, offsetfile.readlines()[0].split())

    # Open the file for reading.
    with open(filename_params, 'r') as infile:
        data = infile.readlines()  # Read the contents of the file into memory.
        imagecount = (len(data)-8)/10
        print imagecount, ' images'
    # Divide into sections
    for m in range(imagecount):
        linebase = 8+m*10
        dic = {}
        splitted = data[linebase].split()
        dic['camera_name'] = splitted[0]
        dic['camera_w'] = int(splitted[1])
        dic['camera_h'] = int(splitted[2])

        # CAMERA MATRIX K
        linebase = linebase +1
        splitted = []
        for i in range(3):
            splitted.append(map(float, data[linebase+i].split()))
        dic['K'] = np.array(splitted)

        # CAMERA POSITION t
        linebase = linebase +5 # Jump to camera position
        splitted = np.array(map(float, data[linebase].split())) + offset
        dic['t'] = np.reshape(splitted,(3,1))

        # CAMERA ROTATION R
        linebase = linebase +1
        splitted = []
        for i in range(3):
            splitted.append(map(float, data[linebase+i].split()))
        dic['R'] = np.array(splitted)

        # Save camera
        params.append(dic)

    return params


def readGeoTiff(imfile):
    'Returns grayscale image as a numpy array!'
    from osgeo import gdal, gdalconst
    import cv2
    import sys

    # Register driver
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()

    # Load image
    geoimg = gdal.Open(imfile, gdalconst.GA_ReadOnly)  # Format is id, Xpos, Ypos
    if geoimg is None:
        print ("Image file load FAILED")
        sys.exit(1)
    else:
        print "Image file loaded successfully."
        # write image to numpy array
        img = cv2.merge((
            geoimg.GetRasterBand(1).ReadAsArray(),
            geoimg.GetRasterBand(2).ReadAsArray(),
            geoimg.GetRasterBand(3).ReadAsArray()
        ))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Read image geoinfo
    try:
        geotrf = geoimg.GetGeoTransform()
    except:
        print 'Cannot read GeoInfo...stopping'
        sys.exit()
    origin = (geotrf[0], geotrf[3])
    cell_size = (geotrf[1], geotrf[5])
    dimensions = (geoimg.RasterXSize, geoimg.RasterYSize)

    # Return everything
    return gray, origin, cell_size, dimensions