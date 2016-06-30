"""
Clip each image with its corresponding projected boundary file

Reads:
 - 2D boundary multipolygon file for each camera
    - location: see output from previous step
    - format: see output from previous step
    - library: OGR
 - undistorted image for each camera
    - location: defined by user in settings file
    - format: TIFF image
    - library: GDAL
Tasks:
 - clip each image using the corresponding multipolygon
Tools:
 - rasterclipper.py
Writes:
 - N clipped images, where N is the number of cameras
    - location: [project home directory]/3_clip_images_2d/[image name]_clipped.tif
    - format: TIFF image
"""

import helpers
import os
import sys
import gdal
import gdalnumeric
import ogr
import operator
import osr
import Image
import ImageDraw
gdal.UseExceptions()


def clip_images_2d(settings, structure, debug):
    """Clips images with the projected road boundary information"""

    print 'I shouldn\'t print this.'

    output_folder = os.path.join(settings.values['Global']['working_directory'], structure[2])

    # Loop through files of projected boundaries
    boundary_folder = os.path.join(settings.values['Global']['working_directory'], structure[1])

    for boundary_file in os.listdir(boundary_folder):
        # input image name
        image_file_in = os.path.join(settings.values['Inputs']['undistorted_image_folder'], boundary_file.split('.')[0]+'.tif')
        # output image name
        image_file_out = os.path.join(output_folder, boundary_file.split('.')[0]+'.tif')
        # Check if file exists
        if os.path.isfile(image_file_in):

            print 'clipping', image_file_in,  ' to ', image_file_out

            #  clip file
            clip(os.path.join(boundary_folder, boundary_file),
                 image_file_in,
                 image_file_out)


# This function will convert the rasterized clipper shapefile
# to a mask for use within GDAL.
def imageToArray(i):
    """
    Converts a Python Imaging Library array to a
    gdalnumeric image.
    """
    a = gdalnumeric.fromstring(i.tostring(), 'b')
    a.shape = i.im.size[1], i.im.size[0]
    return a

def arrayToImage(a):
    """
    Converts a gdalnumeric array to a
    Python Imaging Library Image.
    """
    i = Image.fromstring('L', (a.shape[1], a.shape[0]),
                         (a.astype('b')).tostring())
    return i

def world2Pixel(geoMatrix, x, y):
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    """
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / xDist)
    return (pixel, line)

#
#  EDIT: this is basically an overloaded
#  version of the gdal_array.OpenArray passing in xoff, yoff explicitly
#  so we can pass these params off to CopyDatasetInfo
#
def OpenArray(array, prototype_ds=None, xoff=0, yoff=0):
    ds = gdal.Open(gdalnumeric.GetArrayFilename(array))

    if ds is not None and prototype_ds is not None:
        if type(prototype_ds).__name__ == 'str':
            prototype_ds = gdal.Open(prototype_ds)
        if prototype_ds is not None:
            gdalnumeric.CopyDatasetInfo(prototype_ds, ds, xoff=xoff, yoff=yoff)
    return ds

def histogram(a, bins=range(0, 256)):
    """
    Histogram function for multi-dimensional array.
    a = array
    bins = range of numbers to match
    """
    fa = a.flat
    n = gdalnumeric.searchsorted(gdalnumeric.sort(fa), bins)
    n = gdalnumeric.concatenate([n, [len(fa)]])
    hist = n[1:] - n[:-1]
    return hist

def stretch(a):
    """
    Performs a histogram stretch on a gdalnumeric array image.
    """
    hist = histogram(a)
    im = arrayToImage(a)
    lut = []
    for b in range(0, len(hist), 256):
        # step size
        step = reduce(operator.add, hist[b:b + 256]) / 255
        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + hist[i + b]
    im = im.point(lut)
    return imageToArray(im)

def clip(shapefile_path, raster_path, output_path):
    # Load the source data as a gdalnumeric array
    srcArray = gdalnumeric.LoadFile(raster_path)

    # Also load as a gdal image to get geotransform
    # (world file) info
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()

    # Create an OGR layer from a boundary shapefile
    shapef = ogr.Open(shapefile_path)
    lyr = shapef.GetLayer(os.path.split(os.path.splitext(shapefile_path)[0])[1])
    poly = lyr.GetNextFeature()

    # Convert the layer extent to image pixel coordinates
    minX, maxX, minY, maxY = lyr.GetExtent()
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)

    # Calculate the pixel size of the new image
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)

    clip = srcArray[:, ulY:lrY, ulX:lrX]

    #
    # EDIT: create pixel offset to pass to new image Projection info
    #
    xoffset = ulX
    yoffset = ulY
    print "Xoffset, Yoffset = ( %f, %f )" % (xoffset, yoffset)

    # Create a new geomatrix for the image
    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY

    # Map points to pixels for drawing the
    # boundary on a blank 8-bit,
    # black and white, mask image.
    points = []
    pixels = []
    geom = poly.GetGeometryRef()
    pts = geom.GetGeometryRef(0)
    for p in range(pts.GetPointCount()):
        points.append((pts.GetX(p), pts.GetY(p)))
    for p in points:
        pixels.append(world2Pixel(geoTrans, p[0], p[1]))
    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = imageToArray(rasterPoly)

    # Clip the image using the mask
    clip = gdalnumeric.choose(mask,
                              (clip, 0)).astype(gdalnumeric.uint8)

    # This image has 3 bands so we stretch each one to make them
    # visually brighter
    # for i in range(3):
    #     clip[i, :, :] = stretch(clip[i, :, :])

    # Save new tiff
    #
    gtiffDriver = gdal.GetDriverByName('GTiff')
    if gtiffDriver is None:
        raise ValueError("Can't find GeoTiff Driver")
    gtiffDriver.CreateCopy(output_path,
                           OpenArray(clip, prototype_ds=raster_path, xoff=xoffset, yoff=yoffset)
                           )


    gdal.ErrorReset()