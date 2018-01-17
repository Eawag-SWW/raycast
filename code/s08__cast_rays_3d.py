"""
Reads:
 - 2D prediction clusters from previous step
    - location: see output from previous step
    - format: see output from previous step
 - 3D mesh
    - location: defined in settings file
    - format: ply or STL
    - library: VTK
 - Camera calibration parameters
Tasks:
 - For each prediction cluster in each image
   - Compute ray in 3D
   - Intersect with mesh
   - Extract first intersection point (or maybe all intersection points?)
Writes:
 - 3D predictions
   - Coordinates
   - Standard deviation of cluster (assuming 2D normal distribution)
   - Reference to image
   - Number of hits
   ----------------
   - location: [project home directory]/6_cast_rays_3d/
   - format: TO BE DEFINED
Tools:
 - [Pycaster for casting rays onto mesh]
 - OR use the VTK library directly
"""

import os
import vtk
import numpy as np
import helpers
import csv
import default_settings as settings


def cast_rays_3d(config, debug):
    # Where to find the 2D clusters
    cluster_folder = os.path.join(config['iteration_directory'],
                                  settings.general['iterations_structure']['detect'])

    # Where to store 3D points in memory
    # points_3d = np.empty([1, 5])

    # Where to save 3D points
    output_file = os.path.join(config['iteration_directory'],
                               settings.general['iterations_structure']['cast'], '3dpoints.csv')

    # Start saving data
    with open(output_file, 'wb') as csv_file:

        point_writer = csv.writer(csv_file, delimiter=',',
                                  quotechar='"', quoting=csv.QUOTE_MINIMAL)
        point_writer.writerow(['x', 'y', 'z', 'score', 'id', 'image', 'img_x', 'img_y'])

        # Get camera calibration information
        camera_params = helpers.read_camera_params(
            settings.inputs['camera_xyz_offset'],
            settings.inputs['camera_params'])

        # Load 3D mesh
        print 'Loading 3D mesh...'
        mesh = loadSTL(settings.inputs['3dmesh'])

        # Load mesh offset
        with open(settings.inputs['3dmesh_offset'], 'r') as offsetfile:
            mesh_offset = np.array(map(float, offsetfile.readlines()[0].split()))

        # build OBB tree for fast intersection search
        print 'Building OBB tree...'
        obbTree = vtk.vtkOBBTree()
        obbTree.SetDataSet(mesh)
        obbTree.BuildLocator()

        image_index = 0

        # compute 3d points
        for cluster_list_file in os.listdir(cluster_folder):

            # if cluster_list_file != 'IMG_1105.csv': continue

            # print cluster_list_file

            # get image number
            image_index += 1

            # read clusters
            cluster_list = np.loadtxt(os.path.join(cluster_folder, cluster_list_file), skiprows=1, delimiter=';',
                                      ndmin=2)

            # fetch parameters for image
            this_cam_params = \
            filter(lambda c: c['camera_name'].split('.')[0] == cluster_list_file.split('.')[0], camera_params)[0]

            # compute camera transforms
            KRt = np.dot(np.dot(this_cam_params['K'], this_cam_params['R']), this_cam_params['t'])
            KRinv = np.linalg.inv(np.dot(this_cam_params['K'], this_cam_params['R']))
            # the zval is like an estimated elevation difference between camera and point
            zval = 200

            # intersection source (camera)
            intersection_source = np.transpose(this_cam_params['t'])[0] - mesh_offset

            # for each cluster
            for cluster in cluster_list:

                # Step 1: project to 3D space
                X2d = np.array([
                    [cluster[0] * zval / float(settings.inputs['image_pixel_x'])],
                    [cluster[1] * zval / float(settings.inputs['image_pixel_y'])],
                    [zval]])
                X3d = np.dot(KRinv, (X2d + KRt))

                #  target (3D point) and intersections
                intersection_target = np.transpose(X3d)[0] - mesh_offset
                pointsVTKintersection = vtk.vtkPoints()

                # Step 2: intersect line with surface and retain lowest
                code = obbTree.IntersectWithLine(intersection_source, intersection_target, pointsVTKintersection, None)
                if code == 1:
                    pointsVTKIntersectionData = pointsVTKintersection.GetData()
                    noPointsVTKIntersection = pointsVTKIntersectionData.GetNumberOfTuples()
                    (x, y, z) = pointsVTKIntersectionData.GetTuple3(0)
                    point_writer.writerow([
                        x + mesh_offset[0],
                        y + mesh_offset[1],
                        z + mesh_offset[2],
                        cluster[2],  # the score of the cluster
                        int(cluster[3]),  # the id of the cluster
                        cluster_list_file.split('.')[0],  # the image in which the cluster was detected
                        int(X2d[0][0] / zval),  # image coordinates
                        int(X2d[1][0] / zval)])
                    # points_3d = np.append(points_3d, new_point_3d, axis=0)
                    # point_writer.writerow(new_point_3d)

    return 0


def loadSTL(filenameSTL):
    readerSTL = vtk.vtkSTLReader()
    readerSTL.SetFileName(filenameSTL)
    # 'update' the reader i.e. read the .stl file
    readerSTL.Update()

    polydata = readerSTL.GetOutput()

    # If there are no points in 'vtkPolyData' something went wrong
    if polydata.GetNumberOfPoints() == 0:
        raise ValueError(
            "No point data could be loaded from '" + filenameSTL)

    return polydata
