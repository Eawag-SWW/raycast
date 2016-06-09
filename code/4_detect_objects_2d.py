"""
Reads:
 - Clipped images
 - Classifier definition (.xml)
Writes:
 - For each image, a collection of 2D prediction points
Tasks:
 - For each image
   - Run classifier
   - Save prediction coordinates
Tools:
 - OpenCV CascadeClassifier.exe
 - Parallelization? This processing step is arguably the most lengthy and the one that will be repeated many times.
"""