"""
Reads:
 - 3D predictions
    - location: see output from previous step
    - format: see output from previous step
    - read with: TO BE DEFINED
Tasks:
 - Cluster predictions
Writes:
 - 3D prediction clusters
   - Coordinates
   - Standard deviation (assuming 3D normal distribution)
   - List of 2D Clusters involved
   ----------------
   - location: [project home directory]/7_cluster_3d/
   - format: TO BE DEFINED
Tools:
 - Sklearn.cluster.dbscan

"""