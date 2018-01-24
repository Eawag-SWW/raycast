general = {
    "working_directory": "C:/temp/raycast_koeniz_original_images",
    "preparations_subdir": "preparations",
    "iterations_subdir": "iterations",
    "detection_subdir": "detection",
    "clf_training_subdir": "clf_training",
    "stats_subdir": "performance",
    "startingpoint": "Auto",
    "epsg": 21781,
    "gdalwarp": "C:/Program Files/QGIS Essen/bin/gdalwarp.exe",
    "opencv": "C:/opt/opencv/build/x64/vc14/bin",
    "start_new_iteration": False,
    "preparations_structure": {
        "proj_3d": 's01__project_boundary_3d',
        "proj_2d": 's02__project_boundary_2d',
        "clip": 's03__clip_images_2d',
        # "extract": 's04__extract_initial_samples'
    },
    "iterations_structure": {"refresh": 's05__refresh_training_sets',
                             "retrain": 's06__retrain_classifier',
                             "detect": 's07__detect_objects_2d',
                             "cast": 's08__cast_rays_3d',
                             "cluster": 's09__cluster_3d',
                             "evaluate": 's10__evaluate_candidates',
                             "fit": 's11__fit_classifiers',
                             "classify": 's12__classify_clusters',
                             "prc": 's13__precision_recall',
                             "extract": 's14__extract_candidate_images'},
    "max_generations": 1,
    "mode": "detection"
}
inputs = {
    "boundary_file": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/Geodata/roadsides.shp",
    "demfile": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/Geodata/dem.tif",
    "3dmesh": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/Mesh/koeniz.stl",
    "3dmesh_offset": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/pix4DOffset.txt",
    "classifier_default": "../demo_data/classifier/demo_classifier.xml",
    "binary_model_default": "../demo_data/classifier/binary_model.py",
    # "undistorted_image_folder": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/Pix4D/koeniz/1_initial/images/undistorted_images",
    # "undistorted_image_folder": "../demo_data/images",
    "undistorted_image_folder": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/Pix4D/img",
    "image_extension": "jpg",
    "camera_params": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/Pix4D/koeniz/1_initial/params/koeniz_calibrated_camera_parameters.txt",
    "camera_xyz_offset": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/pix4DOffset.txt",
    "image_pixel_x": 0.00001,
    "image_pixel_y": -0.00001,
    "image_width_px": 4608,
    "image_height_px": 3456,
    "calibrationformat": "pix4D",
    "ground_truth": "Q:/Messdaten/floodVisionData/side_2016_raycast/data/validation_koeniz/Geodata/ground_truth.csv",
    "ground_truth_csv_delimiter": ","
}

detection = {
    "trained_img_classifier": "../demo_data/classifier/demo_classifier.xml",
    "trained_cluster_classifier": "Q:/Messdaten/floodVisionData/side_2016_raycast/analysis/Logistic models/32px_update_170427/3N/s11__fit_binary_model\logistic_regression.pkl",
    "classifier_min_size": 36,
    "classifier_max_size": 36,
    "classifier_scale_factor": 999,
    "classifier_min_neighbors": 0
}
image_clipping = {
    "image_ground_size": 200,
}
clustering_3d = {
    "maximumdistance": 0.1,
    "neighborhood_size": 0.2,
    "min_samples": 6
}
evaluation = {
    "do_evaluation": True,
    "acceptance_radius": 0.5,
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

classification = {
    'fitted_classifier_folder': 'C:/temp/raycastDetectionAdliswil/clf_training/s11__fit_classifiers'
}

precision_recall = {
    'steps': 40
}