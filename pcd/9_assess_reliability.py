"""
Args:
 - 3D clusters
Writes:
 - 3D clusters, with reliability score attribute
Tasks:
 - Compute an overall reliability of each cluster by assigning weights to
   - 2D cluster statistics (number of hits, density of cluster)
   - 3D cluster statistics (number of hits, density of cluster, number of missing votes)

"""