"""
Reads:
 - 2D prediction clusters from previous step
 - 3D mesh
 - Camera calibration values
Writes:
 - 3D predictions
   - Coordinates
   - Standard deviation of cluster (assuming 2D normal distribution)
   - Reference to image
   - Number of hits
Tasks:
 - For each prediction cluster in each image
   - Compute ray in 3D
   - Intersect with mesh
   - Extract first intersection point (or maybe all intersection points?)
Tools:
 - Pycaster for casting rays onto mesh (uses the VTK library)

"""