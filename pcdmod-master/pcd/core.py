# -*- coding: utf-8 -*-

# Modules
import SettingReader
import os
import gdal
import ogr
import osr
import sys
import numpy as np

debug = True
structure = ['1_project_boundary_3d', '2_project_boundary_2d', '3_clip_images_2d', '4_detect_objects_2d',
             '5_cluster_2d', '6_cast_rays_3d', '7_cluster_3d', '8_assess_visibility', '9_assess_reliability']


def main(settingsfile=None):
    """Manages overall detection process, from beginning to end. This includes:
		o	Read boundary, DEM, 3D mesh files into memory, check validity of coordinates
		o	Read settings
		o	Check the existence of intermediate files (3D boundaries, clipped images) and read them if possible
		o	Filter out cameras that have inacceptable calibration accuracy
		o	Orchestrate tasks
		o	Error handling
		o	Write intermediate results to files"""

    # read settings
    settings = SettingReader.SettingReader(None)
    # print settings.values['Global']['startingpoint']

    # initialize processing
    initialize(settings)

    start(settings)

    return 0


def start(settings):
    functionname = settings.values['Global']['startingpoint'][2:]
    globals()[functionname](settings)
    pass


def initialize(settings):
    """Configures the processing by setting up necessary file structure and assessing starting point"""

    # set up working directory
    working_directory = settings.values['Global']['workingdirectory']

    # check if directory exists and create otherwise
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)
        if debug: print "processing directory created."

    # check if log file exists
    with open(os.path.join(working_directory, 'log.txt'), 'a+') as log:  # a+ means add to file
        lines = log.readlines()
        if len(lines) > 0:
            position = lines[-1]
        else:
            position = structure[0]
            # directory structure
            checkdirectorystructure(working_directory)
        pass

    if debug: print 'position is {currentPos}'.format(currentPos=position)

    # update settings
    settings.values['Global']['startingpoint'] = position

    return 0


def checkdirectorystructure(home):
    # tests and creates directory structure
    for directory in structure:
        if not os.path.exists(os.path.join(home, directory)):
            os.makedirs(os.path.join(home, directory))
            if debug: print  "directory created: {directory}".format(directory=directory)
    pass


def project_boundary_3d(settings):
    # log position
    write_to_log(settings, structure[0])

    # read data from file
    boundary2D = LoadShape(settings.values['Inputs']['boundaryfile'])
    dem_dataset = gdal.Open(settings.values['Inputs']['demfile'])
    dem_rasterband = dem_dataset.GetRasterBand(1)
    dem_geotransform = dem_dataset.GetGeoTransform()

    # process data
    # 3D shapefile
    # Register driver
    driver = ogr.GetDriverByName('GeoJSON')

    # create the spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(settings.values['Global']['epsg']))

    # Create new file
    # Create new, even if the last already exists, because otherwise there are problems
    filename = os.path.join(settings.values['Global']['workingdirectory'], structure[0], 'boundary3D.json')
    if os.path.exists(filename):
        driver.DeleteDataSource(filename)
    dataSource = driver.CreateDataSource(filename)
    if dataSource is None:
        print 'Could not create ' + filename
        return 1
    # sys.exit(1)

    # Create a new layer
    outlayer = dataSource.CreateLayer('boundaries', srs, geom_type=ogr.wkbMultiPolygon)
    featureDefn = outlayer.GetLayerDefn()

    for feature in boundary2D.GetLayer():
        # create feature
        outfeature = ogr.Feature(featureDefn)

        # extract geometry
        # for g in xrange(feature.getNumGeometries()):

        # Create output polygon
        outgeom = ogr.Geometry(ogr.wkbMultiPolygon)
        # read polygon
        ingeom = feature.GetGeometryRef()

        print 'geometry count: ', ingeom.GetGeometryCount()
        print 'geometry name: ', ingeom.GetGeometryName()
        for inpoly in ingeom:
            outpoly = ogr.Geometry(ogr.wkbPolygon)
            # print 'polygon found'
            for ring in inpoly:
                outring = ogr.Geometry(ogr.wkbLinearRing)
                points = ring.GetPointCount()
                # print 'ring with points: ', points
                for p in xrange(points):
                    x, y, z = ring.GetPoint(p)
                    px = int((x - dem_geotransform[0]) / dem_geotransform[1])
                    py = int((y - dem_geotransform[3]) / dem_geotransform[5])
                    # px = min(max(px,0),int(dem_geotransform[1])
                    # py = min(max(py,0),dem_geotransform[5])
                    z = float(dem_rasterband.ReadAsArray(px, py, 1, 1)[0][0])
                    # print z
                    # add point to polygon
                    outring.AddPoint(x, y, z)

                # add ring to polygon
                outpoly.AddGeometry(outring)
                # destroy ring
                outring.Destroy()

            outgeom.AddGeometry(outpoly)
            outpoly.Destroy()

        # add multipolygon to feature
        outfeature.SetGeometry(outgeom)
        # destroy polygon
        outgeom.Destroy()

        # add feature to layer
        outlayer.CreateFeature(outfeature)
        # destroy feature
        outfeature.Destroy()

    # destroy data source
    dataSource.Destroy()

    # close dem file
    dem_dataset = None

    # call next function
    project_boundary_2d(settings)

    pass


def project_boundary_2d(settings):
    '''Projects 3D boundary onto 2D images and clips them.'''

    # log position
    write_to_log(settings, structure[1])

    # Read image calibration parameters
    params = readPmatrix(settings.values['Inputs']['calibrations'])

    # Loop through images, project, clip, save
    for camera in params[1:3]:
        pMatrix = camera['camera_matrix']
        camera_name = camera['camera_name']
        output_file = os.path.join(settings.values['Global']['workingdirectory'], structure[1],
                                   camera_name + '_boundary2D.json')
        # clip
        project2D(settings, output_file, pMatrix)
        # save

        pass

    # call next function

    pass


def project2D(settings, output_file, pMatrix):
    if (debug): print 'working on ', output_file

    print_calc = True

    # Load 3D boundary
    boundary3D = LoadShape(os.path.join(
        settings.values['Global']['workingdirectory'],
        structure[0],
        'boundary3D.json'), 'GeoJSON')

    # Register driver
    driver = ogr.GetDriverByName('GeoJSON')

    # create the spatial reference
    # srs = osr.SpatialReference()
    # srs.ImportFromEPSG(int(settings.values['Global']['epsg']))

    # Create new file
    # Create new, even if the last already exists, because otherwise there are problems
    filename = os.path.join(output_file)
    if os.path.exists(filename):
        driver.DeleteDataSource(filename)
    data_source = driver.CreateDataSource(filename)
    if data_source is None:
        print 'Could not create ' + filename
        return 1
    # sys.exit(1)

    # Create a new layer
    outlayer = data_source.CreateLayer('boundaries', None, geom_type=ogr.wkbMultiPolygon)
    featureDefn = outlayer.GetLayerDefn()

    for feature in boundary3D.GetLayer():
        # create feature
        outfeature = ogr.Feature(featureDefn)
        # Create output polygon
        outgeom = ogr.Geometry(ogr.wkbMultiPolygon)

        # read polygon
        ingeom = feature.GetGeometryRef()

        for inpoly in ingeom:
            outpoly = ogr.Geometry(ogr.wkbPolygon)
            for ring in inpoly:
                outring = ogr.Geometry(ogr.wkbLinearRing)
                points = ring.GetPointCount()
                for p in xrange(points):
                    x, y, z = ring.GetPoint(p)
                    point3D = np.array([[x], [y], [z], [1]])
                    # project boundary to image coordinates
                    vec = np.dot(pMatrix, point3D)

                    u = vec[0, 0] / vec[2, 0]
                    v = vec[1, 0] / vec[2, 0]
                    outring.AddPoint(u, v)

                    if print_calc:
                        print '3D point:', point3D
                        print 'pMatrix:', pMatrix
                        print 'camera coords:', vec
                        print 'u: ', u
                        print 'v: ', v
                        print_calc = False
                        pass

                # add ring to polygon
                outpoly.AddGeometry(outring)
                # destroy ring
                outring.Destroy()

            outgeom.AddGeometry(outpoly)
            outpoly.Destroy()

        # add multipolygon to feature
        outfeature.SetGeometry(outgeom)
        # destroy polygon
        outgeom.Destroy()

        # add feature to layer
        outlayer.CreateFeature(outfeature)
        # destroy feature
        outfeature.Destroy()

    # destroy data source
    data_source.Destroy()

    # close file
    boundary3D = None

    pass


def readPmatrix(filename):
    # make a list of dictionaries
    params = []
    # Open the file for reading.
    with open(filename, 'r') as infile:
        data = infile.readlines()  # Read the contents of the file into memory.

    # Divide into sections
    for line in data:
        dic = {}
        splitted = line.split()
        dic['camera_name'] = splitted[0]
        dic['camera_matrix'] = np.reshape(map(float, splitted[1:]), (3, 4))
        params.append(dic)

    return params


def LoadShape(filename, driver='ESRI Shapefile'):
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
    with open(os.path.join(settings.values['Global']['workingdirectory'], 'log.txt'),
              'a+') as log:  # a+ means add to file
        log.write('\n' + line)
    pass


# run program
main()
