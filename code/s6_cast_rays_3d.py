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
import numpy as np
import helpers


def cast_rays_3d(settings, structure, debug):

    # Where to find the 2D clusters
    cluster_folder = os.path.join(settings.values['Global']['working_directory'], structure[3])

    # Where to store 3D points in memory
    points_3d = np.empty([1, 3])

    # Where to save 3D points
    output_file = os.path.join(settings.values['Global']['working_directory'], structure[5], '3dpoints.csv')

    # Get camera calibration information
    camera_params = helpers.read_camera_params(
        settings.values['Inputs']['camera_xyz_offset'],
        settings.values['Inputs']['camera_params'])

    # compute 3d points
    for cluster_list_file in os.listdir(cluster_folder):

        print cluster_list_file

        # read clusters
        cluster_list = np.loadtxt(os.path.join(cluster_folder, cluster_list_file), skiprows=1, delimiter=';')

        # fetch parameters for image
        this_cam_params = filter(lambda c: c['camera_name'].split('.')[0] == cluster_list_file.split('.')[0], camera_params)[0]

        KRt = np.dot(np.dot(this_cam_params['K'], this_cam_params['R']), this_cam_params['t'])
        KRinv = np.linalg.inv(np.dot(this_cam_params['K'], this_cam_params['R']))

        zval = 100

        # for each cluster
        for cluster in cluster_list:

            # Step 1: project to 3D space
            X2d = np.array([
                [cluster[0]*zval/float(settings.values['Inputs']['image_pixel_x'])],
                [cluster[1]*zval/float(settings.values['Inputs']['image_pixel_y'])],
                [zval]])
            X3d = np.dot(KRinv, (X2d + KRt))

            # Step 2: create 3D line between 3D point and camera location

            # Step 3: intersect line with surface and retain lowest


            points_3d = np.vstack([points_3d, [X3d[0, 0], X3d[1, 0], X3d[2, 0]]])

    # write to CSV
    np.savetxt(output_file, points_3d, delimiter=" ",)



