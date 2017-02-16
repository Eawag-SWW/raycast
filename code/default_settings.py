general = {
    "working_directory": "C:/temp/pcdTest",
    "startingpoint": "Auto",
    "epsg": 21781,
    "gdalwarp": "C:/Program Files/QGIS Essen/bin/gdalwarp.exe",
}
inputs = {
    "boundary_file": "../demo_data/boundary/boundary2D.shp",
    "demfile": "../demo_data/dem/DEM.tif",
    "3dmesh": "../demo_data/mesh/adliswil_mesh_blender.stl",
    "3dmesh_offset": "../demo_data/mesh/mesh_offset.xyz",
    "classifier_default": "../demo_data/classifier/demo_classifier.xml",
    # "undistorted_image_folder": "Q:/Abteilungsprojekte/eng/SWWData/Matthew/PhD_DATA/side_2016_raycast/data/undistorted_images",
    "undistorted_image_folder": "../demo_data/images",
    "camera_params": "../demo_data/image_params/l1_calibrated_camera_parameters.txt",
    "camera_xyz_offset": "../demo_data/image_params/l1_offset.xyz",
    "image_pixel_x": 0.00001,
    "image_pixel_y": -0.00001,
    "calibrationformat": "pix4D",
    "ground_truth": "../demo_data/validation/positives.csv",
    "ground_truth_csv_delimiter": ","
}
image_clipping = {
    "image_ground_size": 200,
}
clustering_2d = {
    "maximumdistance": 0.4,
}
clustering_3d = {
    "maximumdistance": 0.4,
}
evaluation = {
    "do_evaluation": True,
    "acceptance_radius": 0.4,
}