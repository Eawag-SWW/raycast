Raycast: Object detection framework for UAV photo clouds
========================
## Objective

This code is a framework for detecting objects in calibrated UAV images. It is designed to work with window-based classifiers like opencv cascadeclassifier, and streamlines the training process of such classifiers.

## Prerequisites

It assumes that the images were processed in Pix4D, since specific Pix4D processing files are required for the framework to run. Namely, the undistorted images and camera calibration parameter files are required.

## Method
![Framework diagram](docs/images/diagram.png?raw=true "Method of framework")
