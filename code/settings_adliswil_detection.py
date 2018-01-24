general = {
    "working_directory": "C:/temp/raycast/adliswil_new",
    "preparations_subdir": "preparations",
    "iterations_subdir": "iterations",
    "detection_subdir": "detection",
    "clf_training_subdir": "clf_training",
    "stats_subdir": "performance",
    "startingpoint": "Auto",
    "epsg": 21781,
    "gdalwarp": "C:/Program Files/QGIS Essen/bin/gdalwarp.exe",
    "opencv": "C:/opt/opencv/build/x64/vc14/bin",
    "start_new_iteration": True,
    "preparations_structure": {
        "proj_3d": 's01__project_boundary_3d',
        "proj_2d": 's02__project_boundary_2d',
        "clip": 's03__clip_images_2d',
        "extract": 's04__extract_initial_samples',
        "folds": 's05__create_folds'
    },
    "iterations_structure": {"train": 's06__train_classifier',
                             "detect": 's07__detect_objects_2d',
                             "cast": 's08__cast_rays_3d',
                             "cluster": 's09__cluster_3d',
                             "evaluate": 's10__evaluate_candidates',
                             "fit": 's11__fit_classifiers',
                             "classify": 's12__classify_clusters',
                             "prc": 's13__precision_recall',
                             "extract": 's14__extract_candidate_images'},
    "max_generations": 1,
    "folds": 5
}
inputs = {
    "boundary_file": "../demo_data/boundary/boundary2D.shp",
    "demfile": "../demo_data/dem/DEM.tif",
    "3dmesh": "../demo_data/mesh/adliswil_mesh_blender.stl",
    "3dmesh_offset": "../demo_data/mesh/mesh_offset.xyz",
    "classifier_default": "../demo_data/classifier/demo_classifier.xml",
    "binary_model_default": "../demo_data/classifier/binary_model.py",
    "undistorted_image_folder": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/training_adliswil/undistorted_images",
    # "undistorted_image_folder": "../demo_data/images",
    "image_extension": "tif",
    "camera_params": "../demo_data/image_params/l1_calibrated_camera_parameters.txt",
    "camera_xyz_offset": "../demo_data/image_params/l1_offset.xyz",
    "image_pixel_x": 0.00001,
    "image_pixel_y": -0.00001,
    "image_width_px": 4608,
    "image_height_px": 3456,
    "calibrationformat": "pix4D",
    "ground_truth": "../demo_data/ground_truth.csv",
    "ground_truth_blacklist": "../demo_data/ground_truth_blacklist.csv",
    "negatives": "../demo_data/negative_locations.csv",
    "ground_truth_csv_delimiter": ","
}

detection = {
    "trained_img_classifier": "../demo_data/classifier/demo_classifier.xml",
    "trained_cluster_classifier": "Q:/Messdaten/floodVisionData/side_2016_raycast/analysis/Logistic models/32px_update_170427/3N/s11__fit_binary_model\logistic_regression.pkl",
    "classifier_min_size": 28,
    "classifier_max_size": 28,
    "classifier_scale_factor": 999,
    "classifier_min_neighbors": 0
}
image_clipping = {
    "image_ground_size": 200,
}
clustering_3d = {
    "maximumdistance": 0.1,
    "neighborhood_size": 0.2,
    "min_samples": 4
}
evaluation = {
    "do_evaluation": True,
    "acceptance_radius": 0.5,
}
sample_preparations = {
    'width': 40,
    'height': 40,
    "locations_file": "../demo_data/seed_locations.csv",
    "csv_delimiter": ",",
    "augmentation_ratio_positives": 5,
    "augmentation_ratio_negatives": 1
}
training_images = {
    'width': 40,
    'height': 40,
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
    'mode': 'ALL',
    'w': 40,
    'h': 40
}
classifer_training = {
    # Use a fraction of samples in each training stage
    'positive_sample_ratio': 1.0/haarClassiferArgs['numStages'],
    # Ratio of negative to positive samples. Taking too many negative samples is not recommended
    'neg_pos_ratio': 0.9
}

classification = {
    'fitted_classifier_folder': 'C:/temp/raycastDetectionAdliswil/clf_training/s11__fit_classifiers'
}

precision_recall = {
    'steps': 40
}