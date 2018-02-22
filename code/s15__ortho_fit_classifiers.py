
from s12__fit_classifiers import do_fit_classifiers
import os


def ortho_fit_classifiers(config, debug, settings):
    results_folder_root = os.path.join(config['iteration_directory'],
                                       settings['general']['iterations_structure']['ortho_fit'])
    input_folder = os.path.join(config['iteration_directory'], settings['general']['iterations_structure']['ortho_evaluate'])

    do_fit_classifiers(
        config=config,
        results_folder_root=results_folder_root,
        input_folder=input_folder,
        settings=settings,
        view_mode='single-view'
    )

    return 0
