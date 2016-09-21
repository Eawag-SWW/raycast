"""Projects 3D boundary multipolygons into coordinate systems of 2D images.

Reads:
 - Camera calibration parameter file
    - location: defined by user in settings file
    - Pix4D name: [prject name]_calibrated_camera_parameters.txt
    - read with: the calibrated camera parameter matrices are saved as numpy arrays in a dictionary
 - offset for calibration parameters
    - location: defined by user in settings file
    - Pix4D name: [project name]_offset.xyz
    - read with: saved as a list
 - 3D boundary file:
    - location: see output from previous step
    - format: see output from previous step
    - library: OGR
Tasks:
 - read calibration parameters to dictionary
 - For each image (camera), project 3D boundary into 2D with help of the
   calibration parameters (pmatrix with offset). This is done by looping through vertices and transforming each one.
 - WARNING: because the transformation function is only valid around the center of focus of the camera,
   we have to delete some of the vertices.
Writes:
 - N 2D boundary multipolygons, where N is the number of cameras
    - format: GeoJSON
    - location: [project home directory]/2_project_boundary_2d/[image name]_boundary2D.json
Tools:
 - OGR to read and write polygons

"""


import ogr
import helpers
import os
import numpy as np


def project_boundary_2d(settings, structure, debug):
    """Projects 3D boundary into coordinate systems of 2D images."""

    # Read image calibration parameters
    params = helpers.read_camera_params(settings.values['Inputs']['camera_xyz_offset'], settings.values['Inputs']['camera_params'])

    # Loop through images, project, clip, save
    for camera in params[100:110]:
        # pMatrix = camera['camera_matrix']
        camera_name = camera['camera_name']
        output_file = os.path.join(settings.values['Global']['working_directory'], structure[1],
                                   camera_name + '_boundary2D.json')
        # project and save
        project2d(settings, output_file, camera, structure, debug=debug)

        pass

    # call next function
    return 0
    pass


def project2d(settings, output_file, camera, structure, debug=False):
    if debug:
        print 'working on ', output_file

    print_calc = debug

    # calculate fixed offset for projection
    KRt = np.dot(np.dot(camera['K'], camera['R']), camera['t'])
    # Load 3D boundary
    # Todo: I tried externalizing the loading of the shape so that it didn't have to be done for each image. However,
    # only the projection for the first image would work - the other were returned empty.
    boundary3D = helpers.load_shape(os.path.join(
        settings.values['Global']['working_directory'],
        structure[0],
        'boundary3D.json'), driver='GeoJSON', debug=debug)

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
                    X = np.array([[x], [y], [z]])

                    # ===================================================
                    # project boundary to image coordinates vec = KRX-KRt
                    vec = np.dot(np.dot(camera['K'], camera['R']), X) - KRt
                    # ===================================================

                    u = float(settings.values['Inputs']['image_pixel_x'])*vec[0, 0] / vec[2, 0]
                    v = float(settings.values['Inputs']['image_pixel_y'])*vec[1, 0] / vec[2, 0]
                    outring.AddPoint(u, v)

                    if print_calc:
                        print '3D point: ', X
                        print 'camera pos: ', camera['t']
                        print 'rotation: ', camera['R']
                        print 'matrix: ', camera['K']
                        print '3D point:', X
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
