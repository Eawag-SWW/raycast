#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      moydevma
#
# Created:     31.03.2014
# Copyright:   (c) moydevma 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from sewerDetector import *

def confusionMatrix(truthfile = '', predfile = '', sewerType = 0, MARGIN = 0.4,writeNegs=99,epsg=32632):
    '''    Returns:
    Matched Ground Truths:  tms
    Matched Predictions: pms
    Misses: misses
    False Alerts:  fas'''
    import time, math, ogr, numpy as np


    # ----------VARIABLES----------
    # Sewer type
    if sewerType == 0:
        sewerType = float(input('What sewer input type are you comparing? (Type 99 for all)'))
        print 'Comparing to sewer inlets of type ',sewerType
    # Ground truth
    if truthfile == '':
        truthfile = getPath(('ESRI Shapefile','.shp'),'Training Data Generation/','Open Ground Truth')
    truth = LoadShape(truthfile,sewerType)
    truths = len(truth)
    # Predictions
    if predfile == '':
        predfile =getPath(('ESRI Shapefile','.shp'),'../08 - Case Study/Koeniz/Classification Results','Open Classified Sewer Inlets')
    pred = LoadShape(predfile)
    preds = len(pred)


    distances = np.empty([truths,preds])


    start = time.time()
    # Calculate Distances
    print 'Time for Distance calculation: ',
    it = np.nditer(distances, flags=['multi_index'], op_flags=['writeonly'])
    while not it.finished:
            it[0]= math.sqrt((truth[it.multi_index[0],1] -pred[it.multi_index[1],1])**2+ (truth[it.multi_index[0],2]-pred[it.multi_index[1],2])**2)
            it.iternext()
    print time.time()-start

    # Compare distances with margin to create "matches" array
    matches = distances<MARGIN

    # Calculate Error Rates
    truthMatches = np.any(matches,axis=1) # array describing for which ground truth there was a matching prediction
    predMatches =  np.any(matches,axis=0) # array describing for which predictions there was a matching ground truth
    tms =np.sum(truthMatches)
    pms =np.sum(predMatches)
    misses = truths-tms
    fas = preds-pms
    print 'Matched Ground Truths: ',  tms
    print 'Matched Predictions: ',  pms
    print 'Misses: ', misses
    print 'False Alerts: ', fas
    print 'Detection rate: ', round(100*float(tms)/truths,1),'%'
    print 'Correctness: ', round(100*float(tms)/preds,1),'%'

    if writeNegs == 99:
        writeNegs = input('Write hard negatives to shapefile? [1=yes]')

    if writeNegs == 1:
        writeNegatives(truth,pred,truthMatches,predMatches,epsg)
    else:
        print 'Hard negatives not saved'

    print 'Evaluation finished.'
    return (tms,pms, misses, fas)

def LoadShape(filename , PointType=99):
    # Load points as a numpy array, in order to be evaluated
    import ogr, sys, numpy as np
    driver_shp = ogr.GetDriverByName('ESRI Shapefile')
    driver_shp.Register()
    datasource = driver_shp.Open(filename, 0)

    if datasource is None:
        print "Shapefile load FAILED"
        sys.exit(1)
    else:
        print "Shapefile loaded successfully: " , filename
        # TO DO: Test that it is a point file

    Layer = datasource.GetLayer()
    pointsnumber = Layer.GetFeatureCount()

    points = []
    sewerType = 99
    for feature in Layer:
        if PointType <> 99:
            try:
                sewerType = feature.GetFieldAsDouble('sewerType')
            except:
                print 'error: no field of name sewerType'
        if sewerType == PointType:
            geometry = feature.GetGeometryRef()
            sewerX = geometry.GetX()
            sewerY = geometry.GetY()
            points.append( [sewerType, sewerX, sewerY])

    NPpoints = np.array(points)

    print 'Number of objects (selected/total): ', len(points), '/',pointsnumber
    return NPpoints

def writeNegatives(truth,pred,truthMatches,predMatches,epsg):
    '''writes false alerts and misses to to shapefiles, in order to be reused in training:
        truth: array of ground truth coordinates
        pred: " for predictions
        truthMatches: 1D array describing matched ground truths: 'truth[0]=0 --> the first ground truth point was not matched correctly
        predMatches: " for predictions
        '''
    from sewerDetector import *

    # Select folder for saving files:
    dstFolder=getFolder('../08 - Case Study/Koeniz/Classification Results','Select folder for saving files')

    # False Alerts:create list of false alerts
    falseAlerts=[]
    for i in range(len(pred)): #for each prediction
        if predMatches[i] == 0: #if prediction was not matched
            falseAlerts.append((pred[i][1],pred[i][2])) #add to list of false alerts

    # Write false alerts to shapefile
    writeShapefile(falseAlerts,dstFolder+'/false_alerts.shp',epsg)

    # Misses: create list of misses
    misses=[]
    for i in range(len(truth)): #for each grd truth
        if truthMatches[i]==0: #if not found
            misses.append((truth[i][1],truth[i][2])) #add to list of misses
    # Write misses to shapefile
    writeShapefile(misses,dstFolder+'/misses.shp',epsg)


def writeShapefile(objects,filename, epsg=21781):
    '''Writes shapefile of points from a list of coordinates. WGS84 32N is assumed if not defined!!!'''
    from osgeo import ogr, osr
    import sys, os

    #Register driver
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # create the spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)

    # Create new file
    # Create new, even if the las already exists, because otherwise there are problems
    if os.path.exists(filename):
        driver.DeleteDataSource(filename)
    dataSource = driver.CreateDataSource(filename)
    if dataSource is None:
        print 'Could not create ' + filename
        return 1
        #sys.exit(1)

    # Create a new layer
    layer = dataSource.CreateLayer('objects', srs, geom_type=ogr.wkbPoint)

    featureDefn = layer.GetLayerDefn()

    for i in range(len(objects)):
        (x,y)=objects[i]
        feature = ogr.Feature(featureDefn)
        # Create point feature
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x,y)
        feature.SetGeometry(point)
        feature.SetFID(i)
        layer.CreateFeature(feature)

        # destroy point
        point.Destroy()
        # destroy feature
        feature.Destroy()

    dataSource.Destroy()
    print 'shapefile written to ', filename



if __name__ == '__main__':
    confusionMatrix(writeNegs=1, MARGIN = 0.4, sewerType=99,epsg=32632 )