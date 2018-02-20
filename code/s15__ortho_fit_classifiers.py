
from s12__fit_classifiers import do_fit_classifiers
import default_settings as s
import os


def ortho_fit_classifiers(config, debug):
    results_folder_root = os.path.join(config['iteration_directory'],
                                       s.general['iterations_structure']['ortho_fit'])
    input_folder = os.path.join(config['iteration_directory'], s.general['iterations_structure']['ortho_evaluate'])

    do_fit_classifiers(config=config, results_folder_root=results_folder_root, input_folder=input_folder)

    return 0