"""
This task projects 2D boundary into 3D with the elevation model, in order to then project into image space in the next step.

reads:
 - 2D boundary multipolygon
    - location: defined in settings file
    - format: ESRI shapefile
    - library for reading, storing, editing: OGR
 - raster elevation
    - location: defined in settings file
    - format: geotiff
    - library: GDAL
writes:
 - 3D boundary multipolygon
    - format: GeoJSON
    - location: [project home directory]/1_project_boundary_3d/boundary3D.json
tasks:
 - Loop through vertices of boundary multipolygon and for each, fetch value of DEM and write to a 3D boundary multipolygon.
"""