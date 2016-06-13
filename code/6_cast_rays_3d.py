"""
Reads:
 - 2D prediction clusters from previous step
    - location: see output from previous step
    - format: see output from previous step
 - 3D mesh
    - location: defined in settings file
    - format: ply or STL
    - library: VTK
 - Camera calibration parameters
Tasks:
 - For each prediction cluster in each image
   - Compute ray in 3D
   - Intersect with mesh
   - Extract first intersection point (or maybe all intersection points?)
Writes:
 - 3D predictions
   - Coordinates
   - Standard deviation of cluster (assuming 2D normal distribution)
   - Reference to image
   - Number of hits
   ----------------
   - location: [project home directory]/6_cast_rays_3d/
   - format: TO BE DEFINED
Tools:
 - [Pycaster for casting rays onto mesh]
 - OR use the VTK library directly

"""