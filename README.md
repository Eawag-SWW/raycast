Raycast: Object detection framework for UAV photo clouds
========================
## Objective

This code is a framework for detecting objects in calibrated UAV images. It is designed to work with window-based classifiers like opencv cascadeclassifier, and streamlines the training process of such classifiers.

## Prerequisites

1. It assumes that the images were processed in Pix4D, since specific Pix4D processing files are required for the framework to run. Namely, the undistorted images and camera calibration parameter files are required.
2. GDAL binaries for the gdalwarp function are required (this function is not available from the gdal python wrapper. A working solution is to install the latest QGIS and change the path at the setting "general>>gdalwarp" 

## Python setup and packages to install

Make sure you have installed pip for managing packages. The Anaconda distribution of Python comes with pip as well as other useful packages. 
Most modules needed for raycast can be installed with pip, but the following need an appropriate wheel file to be downloaded.

 - gdal: http://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal (geospatial functions)
 - shapely: http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely (geospatial functions)
 - vtk: http://www.lfd.uci.edu/~gohlke/pythonlibs/#vtk (ray casting functions)

This tutorial for gdal shows how it's done for gdal: https://pythongisandstuff.wordpress.com/2016/04/13/installing-gdal-ogr-for-python-on-windows/

OpenCV needs to be installed separately:
https://sourceforge.net/projects/opencvlibrary/files/
http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html#install-opencv-python-in-windows


## Method
![Framework diagram](docs/images/diagram.png?raw=true "Method of framework")
