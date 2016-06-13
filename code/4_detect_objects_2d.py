"""
Reads:
 - Clipped images
    - location: see output from previous step
    - format: see output from previous step
    - read with: opencv imread
 - Classifier definition (.xml)
    - location: defined by user in settings file
    - format: XML
    - read with: opencv CascadeClassifier
Writes:
 - For each image, a collection of 2D prediction points
    - format: TO BE DEFINED
    - location: [project home directory]/4_detect_objects_2d/
Tasks:
 - Read detection scale range from settings (at what pixel scale should objects be detected?)
 - For each image
   - [optional] determine optimal detection scale from image height
   - Run classifier
   - Convert prediction rectangles into points
   - Save prediction points for that image
Tools:
 - OpenCV CascadeClassifier.exe
 - Parallel? This processing step is arguably the most lengthy and the one that will be repeated many times.
"""