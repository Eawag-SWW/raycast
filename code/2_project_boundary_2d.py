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