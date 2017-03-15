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
import default_settings as settings


def project_boundary_2d(config, debug):
    """Projects 3D boundary into coordinate systems of 2D images."""

    # Read image calibration parameters
    params = helpers.read_camera_params(settings.inputs['camera_xyz_offset'], settings.inputs['camera_params'])

    # Loop through images, project, clip, save
    for camera in params:
        # pMatrix = camera['camera_matrix']
        camera_name = camera['camera_name'].split('.')[0]
        # check if the image actually exists in the project
        if os.path.isfile(os.path.join(settings.inputs['undistorted_image_folder'], camera_name+'.tif')):
            output_file = os.path.join(settings.general['working_directory'],
                                       settings.general['preparations_subdir'],
                                       settings.general['preparations_structure']['proj_2d'],
                                       camera_name + '__boundary2D.json')
            # project and save
            project2d(output_file, camera, debug=debug)

        pass

    # call next function
    return 0
    pass


def project2d(output_file, camera, debug=False):
    if debug:
        print 'working on ', output_file

    print_calc = debug

    # calculate fixed offset for projection
    KRt = np.dot(np.dot(camera['K'], camera['R']), camera['t'])

    # create bounding box for clipping
    xmin = float(camera['t'][0][0]) - int(settings.image_clipping['image_ground_size'])
    xmax = float(camera['t'][0][0]) + int(settings.image_clipping['image_ground_size'])
    ymin = float(camera['t'][1][0]) - int(settings.image_clipping['image_ground_size'])
    ymax = float(camera['t'][1][0]) + int(settings.image_clipping['image_ground_size'])

    # Load 3D boundary
    # Todo: I tried externalizing the loading of the shape so that it didn't have to be done for each image. However,
    # only the projection for the first image would work - the other were returned empty.
    boundary3D = helpers.load_shape(os.path.join(
        settings.general['working_directory'],
        settings.general['preparations_subdir'],
        settings.general['preparations_structure']['proj_3d'],
        'boundary3D.json'), driver='GeoJSON', debug=debug)

    # Register driver
    driver = ogr.GetDriverByName('GeoJSON')

    # create the spatial reference
    # srs = osr.SpatialReference()
    # srs.ImportFromEPSG(int(settings.general['epsg']))

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

                    # Check if point is in bbox
                    if is_in_bbox(x, y, xmin, xmax, ymin, ymax):
                        X = np.array([[x], [y], [z]])

                        # ===================================================
                        # project boundary to image coordinates vec = KRX-KRt
                        vec = np.dot(np.dot(camera['K'], camera['R']), X) - KRt
                        # ===================================================

                        u = float(settings.inputs['image_pixel_x']) * vec[0, 0] / vec[2, 0]
                        v = float(settings.inputs['image_pixel_y']) * vec[1, 0] / vec[2, 0]

                        # limit point coordinates to keep it from becoming outrageous
                        u = min(max(u, -.5), .5)
                        v = min(max(v, -.5), .5)
                        outring.AddPoint(u, v)

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


def is_in_bbox(x, y, xmin, xmax, ymin, ymax):
    return (x < xmax) & (x > xmin) & (y < ymax) & (y > ymin)
