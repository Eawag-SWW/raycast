#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      moydevma
#
# Created:     01.04.2014
# Copyright:   (c) moydevma 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def writeCSV(list,notes, file_path):
    import csv
    with open(file_path, 'a') as outcsv:
        #configure writer to write standart csv file
        writer = csv.writer(outcsv, delimiter=';', lineterminator='\n') #  quotechar='|', quoting=csv.QUOTE_MINIMAL
        writer.writerow(['NEW ENTRY'])
        writer.writerow([notes])
        writer.writerow(['number of neighbors', 'Matched Grd Truths', 'Matched Predictions', 'Misses', 'False Alerts'])

        #Write item to outcsv
        writer.writerows(list)


# ###############################################

from evaluation import *
from sewerDetector import *
import time

notes= 'Cascade classification: 3+ Boosting with different  # of neighbors'
param_thresh = [0,1,2,3,4,5,6,7]
result = []
start_time = time.time()

for n in param_thresh:
    shapefile = 'Output/TEMP/VJ3-Neighbors.shp'
    detectSewers(MODE = 2,params=("Classifier Training/140520-Haar45-HNM3-B1/",n),dstShapeFile=shapefile)
    mgt,mp,m,fa = confusionMatrix(truthfile='Training Data Generation/positives.shp', predfile=shapefile, sewerType = 99)
    result.append([n,mgt,mp,m,fa])

print '###################'
print 'Calculation time: ', time.time()-start_time
print result
writeCSV(result,notes,'Evaluation/'+'thresholding.csv')