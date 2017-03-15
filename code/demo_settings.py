general = {
    "working_directory": "C:/temp/pcdTest",
    "preparations_subdir": "preparations",
    "iterations_subdir": "iterations",
    "stats_subdir": "performance",
    "startingpoint": "Auto",
    "epsg": 21781,
    "gdalwarp": "C:/Program Files/QGIS Essen/bin/gdalwarp.exe",
    "opencv": "C:/opt/opencv/build/x64/vc14/bin",
    "start_new_iteration": False,
    "preparations_structure": ['s1__project_boundary_3d', 's2__project_boundary_2d', 's3__clip_images_2d',
                               's4__extract_initial_samples'],
    "iterations_structure": ['s5__refresh_training_sets', 's6__retrain_classifier', 's7__detect_objects_2d',
                             's8__cast_rays_3d', 's9__cluster_3d', 's10__evaluate_candidates', 's11__fit_binary_model',
                             's12__extract_candidate_images'],
    "max_generations": 5
}
inputs = {
    "boundary_file": "../demo_data/boundary/boundary2D.shp",
    "demfile": "../demo_data/dem/DEM.tif",
    "3dmesh": "../demo_data/mesh/adliswil_mesh_blender.stl",
    "3dmesh_offset": "../demo_data/mesh/mesh_offset.xyz",
    "classifier_default": "../demo_data/classifier/demo_classifier.xml",
    "binary_model_default": "../demo_data/classifier/binary_model.py",
    "undistorted_image_folder": "Q:/Abteilungsprojekte/eng/SWWData/Matthew/PhD_DATA/side_2016_raycast/data/undistorted_images",
    # "undistorted_image_folder": "../demo_data/images",
    "camera_params": "../demo_data/image_params/l1_calibrated_camera_parameters.txt",
    "camera_xyz_offset": "../demo_data/image_params/l1_offset.xyz",
    "image_pixel_x": 0.00001,
    "image_pixel_y": -0.00001,
    "image_width_px": 4608,
    "image_height_px": 3456,
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
training_images = {
    'width': 24,
    'height': 24,
    "positives_file": "../demo_data/training/positives.csv",
    "negatives_file": "../demo_data/training/negatives.csv",
    "csv_delimiter": ","
}
haarClassiferArgs = {
    'numStages': 15,
    'precalcValBufSize': 4048,
    'precalcIdxBufSize': 4048,
    'featureType': 'Haar',
    'minHitRate': 0.99,
    'maxFalseAlarmRate': 0.4,
    'weightTrimRate': 0.95,
    'maxDepth': 1,
    'maxWeakCount': 20,
    'bt': 'GAB',
    'mode': 'ALL'
}
classifer_training = {
    # Not all positive samples should be used because some will be discarded during training
    'positive_sample_ratio': 0.7,
    # Taking too many negative samples is not recommended
    'neg_pos_ratio': 100
}
