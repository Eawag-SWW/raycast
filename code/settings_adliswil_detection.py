general = {
    "working_directory": "C:/temp/raycast/adliswil_more_training_data",
    "preparations_subdir": "preparations",
    "iterations_subdir": "iterations",
    "detection_subdir": "detection",
    "clf_training_subdir": "clf_training",
    "stats_subdir": "performance",
    "startingpoint": "s11__evaluate_candidates",
    "epsg": 21781,
    "gdalwarp": "C:/Program Files/QGIS Essen/bin/gdalwarp.exe",
    "opencv": "C:/opt/opencv/build/x64/vc14/bin",
    "start_new_iteration": False,
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
                             "ortho_detect": 's09__ortho_detect',
                             "cluster": 's10__cluster_3d',
                             "evaluate": 's11__evaluate_candidates',
                             "fit": 's12__fit_classifiers',
                             "ortho_cluster": 's13__ortho_cluster',
                             "ortho_evaluate": 's14__ortho_evaluate_candidates',
                             "ortho_fit": 's15__ortho_fit_classifiers'
                             },
    "max_generations": 1,
    "folds": 5,
    "do_folds": 5  # how many of the folds to process
}
inputs = {
    "boundary_file": "../demo_data/boundary/boundary2D.shp",
    "demfile": "../demo_data/dem/DEM.tif",
    "3dmesh": "../demo_data/mesh/adliswil_mesh_blender.stl",
    "3dmesh_offset": "../demo_data/mesh/mesh_offset.xyz",
    "classifier_default": "../demo_data/classifier/demo_classifier.xml",
    "binary_model_default": "../demo_data/classifier/binary_model.py",
    "undistorted_image_folder": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/training_adliswil/undistorted_images",
    "orthophoto": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/training_adliswil/orthoimage/adliswil_ortho_clipped.tif",
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
    "trained_cluster_classifier": "Q:/Messdaten/floodVisionData/side_2016_raycast/analysis/Logistic models/32px_update_170427/3N/s11__fit_binary_model/logistic_regression.pkl",
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
    "neighborhood_size": 0.25,
    "min_samples": 5
}
clustering_ortho = {
    "maximumdistance": 0.1,
    "neighborhood_size": 0.25,
    "min_samples": 5
}
evaluation = {
    "do_evaluation": True,
    "acceptance_radius": 0.5,
}
sample_preparations = {
    'width': 32,
    'height': 32,
    "locations_file": "../demo_data/seed_locations.csv",
    "csv_delimiter": ",",
    "augmentation_ratio_positives": 3,
    "augmentation_ratio_negatives": 2
}
training_images = {
    'width': 32,
    'height': 32,
    "positives_file": "../demo_data/training/positives.csv",
    "negatives_file": "../demo_data/training/negatives.csv",
    "csv_delimiter": ",",
    "negatives_rating_threshold": 0.001  # negative proposals are hard negatives and come with a score
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
    'w': 32,
    'h': 32
}
classifer_training = {
    # Use a fraction of positive samples - some will be discarded and need to be replaced by others
    'positive_sample_ratio': 0.8,
    # Ratio of negative to positive samples. Taking too many negative samples is not recommended
    'neg_pos_ratio': 2
}

classification = {
    'fitted_classifier_folder': 'C:/temp/raycastDetectionAdliswil/clf_training/s11__fit_classifiers'
}

precision_recall = {
    'steps': 40
}