"""
Reads:
 - 3D predictions
Writes:
 - 3D prediction clusters
   - Coordinates
   - Standard deviation (assuming 3D normal distribution)
   - List of 2D Clusters involved
Tasks:
 - Cluster predictions
Tools:
 - Sklearn.cluster.dbscan

"""