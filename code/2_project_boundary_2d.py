"""Projects 3D boundary multipolygons into coordinate systems of 2D images.

Reads:
 - Camera calibration parameter file
 - offset for calibration parameters
 - 3D boundary file
Tasks:
 - interpret calibration parameters
 - For each image (camera), project 3D boundary into 2D with help of the
   calibration parameters (pmatrix with offset). This is done by looping through vertices and transforming each one.
Writes:
 - N 2D boundary multipolygons, where N is the number of cameras
Tools:
 - OGR to read and write polygons
 - GDAL ReadAsArray() or readRaster()

"""