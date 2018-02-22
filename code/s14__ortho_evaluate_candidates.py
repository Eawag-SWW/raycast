from s11__evaluate_candidates import evaluate_clusters
import os


def ortho_evaluate_candidates(config, debug, settings):
    for fold_i in range(settings['general']['do_folds']):
        print('-- FOLD {} --'.format(fold_i))
        # input files
        ground_truth_file = settings['inputs']['ground_truth']
        clusters_file = os.path.join(config['iteration_directory'],
                                     settings['general']['iterations_structure']['ortho_cluster'],
                                     '3dclusters_{}.csv'.format(fold_i))
        train_list = os.path.join(settings['general']['working_directory'],
                                  settings['general']['preparations_subdir'],
                                  settings['general']['preparations_structure']['folds'],
                                  'gt_train_{}.csv'.format(fold_i))
        test_list = os.path.join(settings['general']['working_directory'],
                                 settings['general']['preparations_subdir'],
                                 settings['general']['preparations_structure']['folds'],
                                 'gt_test_{}.csv'.format(fold_i))
        # output files
        out_clusters_train_file = os.path.join(config['iteration_directory'],
                                               settings['general']['iterations_structure']['ortho_evaluate'],
                                               '3dclusters_train_{}.csv'.format(fold_i))
        out_clusters_test_file = os.path.join(config['iteration_directory'],
                                              settings['general']['iterations_structure']['ortho_evaluate'],
                                              '3dclusters_test_{}.csv'.format(fold_i))

        # check that directory exists
        if not os.path.exists(os.path.dirname(out_clusters_test_file)):
            os.mkdir(os.path.dirname(out_clusters_test_file))

        # Do evaluation
        evaluate_clusters(clusters_file, ground_truth_file, out_clusters_train_file, out_clusters_test_file, train_list,
                          test_list, settings)

    return 0
