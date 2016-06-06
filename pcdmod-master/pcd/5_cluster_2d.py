"""
Reads:
 - 2D predictions
Writes:
 - 2D clusters containing
   - Reference to image
   - Coordinates
   - Number of hits
   - Standard deviation
Tasks:
 - For each image
   - Cluster predictions for that image into groups
   - Non-maxima suppression
Tools:
 - Sklearn.cluster.dbscan

"""