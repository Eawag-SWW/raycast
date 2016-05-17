#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      moydevma
#
# Created:     18.03.2014
# Copyright:   (c) moydevma 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from evaluation import *

def detectSewers(MODE = 0, params =0, dstShapeFile='TEMP/inlets.shp',imfile ='S:/Master Thesis Data/08_Case Studies/Koeniz/Clipped orthophotos/road_cadaster_50_100.tif',epsg=21781, assessTrue=99, ground_truth=''):

    import cv2, sys, time



    # -----------VARIABLES-----------
    ##imfile =  'E:/Users/moydevma/Thesis Data/Image Identification/Testing images/l1_clipped_rgb.tif'
    
    # image block dimensions
    blockDim = 4000 # pixels
    blockBuffer = 13 # pixels
    # Check if function was called from another
    if __name__ == '__main__':ISMAIN = True
    else: ISMAIN = False

    # -----------SELECT MODE--------------
    if MODE == 0:
        MODE = int(input('Thresholding (1) or Viola Jones (2)?'))

    # ----------- LOAD SPECIFIC PARAMETERS IF AVALABLE--------


    # -----------LOAD VJ CLASSIFIER IF NECESSARY-----------
    if MODE ==2: #VIOLA JONES
        if params <> 0:
            try:
                classifierFolder, neighbors = params
                print 'folder with classifier: ', classifierFolder
                print 'number of neighbors: ', neighbors
            except:
                print 'wrong parameters passed'
                sys.exit()
        else:
            message = 'Select folder with cascade classifier'
            classifierFolder =getFolder("Classifier Training/",message)
            neighbors = int(input('How many neighbors re needed for an inlet to count?'))


        gutter_cascade = cv2.CascadeClassifier(classifierFolder+'/cascade.xml')
        if gutter_cascade.empty():
            print 'classifier not loaded - stopping script'
            sys.exit()
    elif MODE == 1: #BLOB
        if params <> 0:
            try:
                p_thresh,p_area,p_aspect,p_blur = params
            except:
                print 'wrong parameters passed'
                sys.exit()
        else:
            print 'no parameters for thresholding...stopping script'
            sys.exit()
    else:
        sys.exit()

    startTime = time.time()

    # -----------LOAD IMAGE-----------
    # Verify
    ##if ISMAIN:
        ##message = 'Select an image file'
        ##imfile = getPath(('GeoTIFF Files','*.tif'),'E:/Users/moydevma/Thesis Data/Image Identification/Testing images/', message)
    geoImage,Origin,CellSize,dimensions = readGeoTiff(imfile)


    # -----------PARTITION IMAGE-----------
    stepsW = int(dimensions[0]/blockDim+1)
    stepsH = int(dimensions[1]/blockDim+1)
    print 'number of blocks: ', stepsH*stepsW

    # -----------PROCESS BLOCKS-----------

    blockCount = 1
    gutters = []
    for j in range(stepsH):
        for i in range(stepsW):
            # Get array from dataset
            print 'block ', blockCount,':',
            extent = getExtent(i,j,blockBuffer, blockDim, dimensions)
            gray = getArray(geoImage, extent)

            # -----------DETECT OBJECTS-----------
            print 'scanning...',
            if MODE == 2:
                localGutters = gutter_cascade.detectMultiScale(gray, scaleFactor = 1000000, minNeighbors=neighbors)
            if MODE == 1:
                localGutters = thresholding(gray,p_thresh,p_area,p_aspect,p_blur)

            print len(localGutters), ' sewer inlet(s)'
            blockCount +=1

            # -----------DRAW RECTANGLES-----------
            #if ISMAIN:
            #    drawRecs(localGutters,gray)

            # ----------SAVE WORK------------
            shapeShift(localGutters,extent)
            gutters.extend(localGutters)

    classifTime = time.time()
    print 'Elapsed time: ', classifTime-startTime

    # -----------WRITE SHAPEFILE-----------

    writeRecs2Shapefile(gutters,Origin,CellSize,dstShapeFile,epsg)

    # -----------ASSESS RESULTS----------
    if assessTrue == 99:
        assessTrue = input('Assess results? [1=yes]')
    if assessTrue== 1:
        confusionMatrix(truthfile=ground_truth, predfile=dstShapeFile)

    print 'Finished.'


def drawRecs(localGutters,img):
    import matplotlib.pyplot as plt
    for (x,y,w,h) in localGutters:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),1)
    # Display image
    plt.imshow(img)
    plt.show()


def readGeoTiff(imfile):
    'Returns grayscale image as a numpy array!'
    from osgeo import gdal, gdalconst
    import sys

    # Register driver
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()

    # Load image
    geoimg = gdal.Open(imfile, gdalconst.GA_ReadOnly) # Format is id, Xpos, Ypos
    if geoimg == None:
        print ("Image file load FAILED")
        sys.exit(1)
    else:
        print "Image file loaded successfully."

    #Read image geoinfo
    try:
        geotrf = geoimg.GetGeoTransform()
    except:
        print 'Cannot read GeoInfo...stopping'
        sys.exit()
    origin = (geotrf[0],geotrf[3])
    cellSize = (geotrf[1],geotrf[5])
    dimensions = (geoimg.RasterXSize,geoimg.RasterYSize)

    # Return everything
    return(geoimg,origin,cellSize,dimensions)

def getExtent(i,j,blockBuffer, blockDim, dimensions):
    x =i*blockDim
    y =j*blockDim
    w =min(blockDim+blockBuffer,dimensions[0]-x)
    h =min(blockDim+blockBuffer,dimensions[1]-y)

    return (x,y,w,h)

def shapeShift(rectangles, extent):
    for i in xrange(len(rectangles)):
        (x,y,w,h) = rectangles[i]
        x += extent[0]
        y += extent[1]
        rectangles[i] = (x,y,w,h)

def getArray(geoImage, extent):
    import  gdal, cv2
    # Define bands
    bands = [None]*3
    for j in range(3):
        bands[j] = geoImage.GetRasterBand(j+1).ReadAsArray(extent[0],extent[1],extent[2],extent[3]) # 1-based index

    # Merge bands
    img = cv2.merge((bands[0],bands[1],bands[2]))

    # Turn into grayscale
    return cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)



def writeRecs2Shapefile(gutters,Origin,CellSize,filename, epsg=21781):
    '''Writes shapefile from a list of rectangle objects. WGS84 32N is not assumed!!!'''
    from osgeo import ogr, osr
    import sys, os

    #Register driver
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # create the spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)

    # Create new file
    if os.path.exists(filename):
        driver.DeleteDataSource(filename)
    dataSource = driver.CreateDataSource(filename)
    if dataSource is None:
        print 'Could not create ' + filename
        return 1
        sys.exit(1)

    # Create a new layer
    layer = dataSource.CreateLayer('gutters', srs, geom_type=ogr.wkbPoint)

    featureDefn = layer.GetLayerDefn()

    for i in range(len(gutters)):
        (x,y,w,h)=gutters[i]
        feature = ogr.Feature(featureDefn)
        # Create point feature
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint((x+w/2)*CellSize[0]+Origin[0],(y+h/2)*CellSize[1]+Origin[1])
        feature.SetGeometry(point)
        feature.SetFID(i)
        layer.CreateFeature(feature)

        # destroy feature
        feature.Destroy()

    dataSource.Destroy()
    print 'shapefile written to ', filename

def thresholding(img,p_thresh,p_maxArea,p_aspect,p_blur):
    'takes a grayscale array and finds gutter-like shapes using a thresholding approach'
    import cv2, time
    import numpy as np


    # Blur using a median filter
    cv2.medianBlur(img,p_blur,img)

    # Close the mask
    ##kernel = np.ones((5,5),np.uint8)
    ##th_hue=cv2.morphologyEx(th_hue,cv2.MORPH_CLOSE,kernel)

    # Thresholding on Grey: should be below p_thresh
    #ret,mask = cv2.threshold(img,p_thresh,255,cv2.THRESH_BINARY_INV)

    #Adaptive thresholding
    mask = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,15,p_thresh)

    # Find Contours
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)

    # Trace Rectangles and only keep good ones
    gutters = []
    areas = []
    aspects = []
    for cnt in contours:
        ((x,y),(w, h),angle) = cv2.minAreaRect(cnt)
        area=h*w
        # AREA
        if area >80 and area < p_maxArea:
            # ASPECT
            aspect =max(w/h,h/w)
            if aspect < p_aspect:
                gutters.append((int(x-w/2),int(y-h/2),int(w),int(h)))

    return gutters

def getPath(filetype, directory, msg):
    import  Tkinter, tkFileDialog

    root = Tkinter.Tk()
    root.withdraw()

    file_path = tkFileDialog.askopenfilename(filetypes=[filetype], initialdir=directory, title=msg)
    return file_path

def getFolder(directory, msg):
    import  Tkinter, tkFileDialog

    root = Tkinter.Tk()
    root.withdraw()

    folder_path = tkFileDialog.askdirectory( initialdir=directory, title=msg)
    return folder_path


if __name__ == '__main__':
    detectSewers(MODE=2)
