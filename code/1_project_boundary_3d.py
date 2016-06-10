"""
This task projects 2D boundary into 3D with the elevation model, in order to then project into image space in the next step.

reads:
 - 2D boundary multipolygon
    - format: ESRI shapefile,
    - library for reading, storing, editing: OGR
 - raster elevation
    - format: geotiff
    - library: GDAL
writes:
 - 3D boundary multipolygon
    - format: GeoJSON
    - location: project home directory/1_project_boundary_3d
tasks:
 - Loop through vertices of boundary multipolygon and for each, fetch value of DEM and write to a 3D boundary multipolygon.
"""