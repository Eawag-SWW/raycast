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
import gdal
import ogr
import osr
import helpers
import os
import default_settings as settings


def project_boundary_3d(config, debug):
    # read data from file
    boundary2D = helpers.load_shape(settings.inputs['boundary_file'], debug=debug)
    dem_dataset = gdal.Open(settings.inputs['demfile'])
    dem_rasterband = dem_dataset.GetRasterBand(1)
    dem_geotransform = dem_dataset.GetGeoTransform()

    # Create output 3D polygon as geojson

    # Register driver
    driver = ogr.GetDriverByName('GeoJSON')

    # create the spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(settings.general['epsg']))

    # Create new file
    # Create new, even if the last already exists, because otherwise there are problems
    filename = os.path.join(settings.general['working_directory'],
                            settings.general['preparations_subdir'],
                            settings.general['preparations_structure']['proj_3d'], 'boundary3D.json')
    if os.path.exists(filename):
        driver.DeleteDataSource(filename)
    dataSource = driver.CreateDataSource(filename)
    if dataSource is None:
        print 'Could not create ' + filename
        return 1

    outlayer = dataSource.CreateLayer('boundaries', srs, geom_type=ogr.wkbMultiPolygon)
    featureDefn = outlayer.GetLayerDefn()

    # The following structure mirrors the input polygon, while assigning elevation to each vertex
    for feature in boundary2D.GetLayer():
        # create feature
        outfeature = ogr.Feature(featureDefn)

        # extract geometry
        # for g in xrange(feature.getNumGeometries()):

        # Create output polygon
        outgeom = ogr.Geometry(ogr.wkbMultiPolygon)
        # read polygon
        ingeom = feature.GetGeometryRef()

        print 'geometry count: ', ingeom.GetGeometryCount()
        print 'geometry name: ', ingeom.GetGeometryName()
        for inpoly in ingeom:
            outpoly = ogr.Geometry(ogr.wkbPolygon)
            # print 'polygon found'
            for ring in inpoly:
                outring = ogr.Geometry(ogr.wkbLinearRing)
                points = ring.GetPointCount()
                # print 'ring with points: ', points
                for p in xrange(points):
                    x, y, z = ring.GetPoint(p)
                    px = int((x - dem_geotransform[0]) / dem_geotransform[1])
                    py = int((y - dem_geotransform[3]) / dem_geotransform[5])
                    # px = min(max(px,0),int(dem_geotransform[1])
                    # py = min(max(py,0),dem_geotransform[5])
                    z = float(dem_rasterband.ReadAsArray(px, py, 1, 1)[0][0])
                    # print z
                    # add point to polygon
                    outring.AddPoint(x, y, z)

                # add ring to polygon
                outpoly.AddGeometry(outring)
                # destroy ring
                outring.Destroy()

            outgeom.AddGeometry(outpoly)
            outpoly.Destroy()

        # add multipolygon to feature
        outfeature.SetGeometry(outgeom)
        # destroy polygon
        outgeom.Destroy()

        # add feature to layer
        outlayer.CreateFeature(outfeature)
        # destroy feature
        outfeature.Destroy()

    # destroy data source
    dataSource.Destroy()

    # close dem file
    dem_dataset = None

    return 0

    pass
