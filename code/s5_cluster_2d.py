"""
Reads:
 - 2D predictions
    - location: see output from previous step
    - format: see output from previous step
    - read with: TO BE DEFINED
Tasks:
 - For each image
   - Cluster predictions for that image into groups
   - Non-maxima suppression or average to retain only one point per cluster
Tools:
 - Sklearn.cluster.dbscan
Writes:
 - 2D clusters containing
   - Reference to image
   - Coordinates
   - Number of hits
   - [Standard deviation]
   -----------------------
   - location: [project home directory]/5_cluster_2d/
   - format: TO BE DEFINED

"""