"""
Reads:
 - 3D clusters
    - location: see output from previous step
    - format: see output from previous step
 - 3D mesh
    - location: defined in settings file
    - format: ply or STL
    - library: VTK
 - Camera calibration parameters
Tasks:
 - For each cluster, estimate the number of cameras that should have seen it:
   - Compute 3D ray between cluster and camera
   - Test if ray is possible for camera. If so, continue.
   - Test if there are intersections of ray with 3D mesh. If so, the cluster is not visible.
     If not, the object should be visible in the image of the camera.
Writes:
 - 3D clusters, with added attribute: list of images in which the point should be visible.
   - location: [project home directory]/8_assess_visibility/
   - format: TO BE DEFINED
 Tools:
 - Pycaster / VTK

"""


def assess_visibility(settings, structure, debug):
    return 0
