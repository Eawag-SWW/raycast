"""
This task projects 2D boundary into 3D with the elevation model, in order to then project into image space in the next step.

reads:
 - 2D boundary multipolygon
 - raster elevation file
writes:
 - 3D boundary multipolygon
tasks:
 - Loop through vertices of boundary multipolygon and for each, fetch value of DEM and write to a 3D boundary multipolygon.
"""