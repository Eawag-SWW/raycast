# -*- coding: utf-8 -*-

# Modules

from s01__project_boundary_3d import *
from s02__project_boundary_2d import *
from s03__clip_images_2d import *
from s04__extract_initial_samples import *
from s05__refresh_training_sets import *
from s05__create_folds import *
from s06__train_classifier import *
from s07__detect_objects_2d import *
from s08__cast_rays_3d import *
from s10__cluster_3d import *
from s11__evaluate_candidates import *
from s12__fit_classifiers import *
from s09__ortho_detect import *
from s13__ortho_cluster import ortho_cluster
from s14__ortho_evaluate_candidates import *
from s15__ortho_fit_classifiers import *
import default_settings
import csv
import collections

# Global variables
debug = False


def run_all(settings_custom={}):
    """Manages overall detection process, from beginning to end. This includes:
     - Read settings
     - Initialize processing
     - Error handling"""

    # read settings. No file passed implies default settings
    # print settings['general']['startingpoint']

    # update settings with custom settings
    if settings_custom == {}:
        settings_mod = default_settings.all
    else:
        settings_mod = update_settings(default_settings.all, settings_custom)

    # make sure basic directory structure is set up
    initialize_directories(settings_mod)
    # initialize preparatory tasks
    prep_config = initialize_prep(settings_mod)

    # do prep tasks
    if prep_config['do_preparation']:
        execute_steps(config=prep_config, structure=default_settings.all['general']['preparations_structure'], settings_mod=settings_mod)
        helpers.write_step_to_log(prep_config, 'preparations done.')

    # do training, detection, clustering, etc
    iter_config = initialize_iterations(settings_mod)
    execute_steps(config=iter_config, structure=default_settings.all['general']['iterations_structure'], settings_mod=settings_mod)
    helpers.write_step_to_log(iter_config, 'iteration done.')


def execute_steps(config, structure, settings_mod):
    step = config['step_position']
    # execute steps
    while step != 'iteration done.':
        helpers.write_step_to_log(config=config, line=step)
        print '### ' + step
        r = globals()[step.split('__')[1]](config, debug, settings_mod)
        if r == 1:
            print 'Error code raised'
            quit()
        elif r == 2:
            print 'Clustering settings invalid'
            if step == 's10__cluster_3d':
                step = 's13__ortho_cluster'
            else:
                step = 'iteration done.'
        else:
            step = get_next_step(step, structure)
        if not step:
            step = 'iteration done.'
    return 0


def get_next_step(current_step, structure):
    structure = structure.values()
    structure.sort()
    index = structure.index(current_step) + 1
    if index >= len(structure):
        return False
    else:
        return structure[structure.index(current_step) + 1]


def initialize_directories(settings):
    """Configures the processing by setting up necessary file structure."""

    # set up working directories
    working_directory = settings['general']['working_directory']
    prep_dir = os.path.join(working_directory, settings['general']['preparations_subdir'])

    # check if working directories exist and create otherwise
    check_directory_structure(working_directory,
                              [settings['general']['preparations_subdir'], settings['general']['iterations_subdir']])
    check_directory_structure(prep_dir, settings['general']['preparations_structure'].values())


def check_directory_structure(home_dir, structure):
    # tests and creates directory structure
    for directory in structure:
        if not os.path.exists(os.path.join(home_dir, directory)):
            os.makedirs(os.path.join(home_dir, directory))
            if debug:
                print "directory created: {directory}".format(directory=directory)
    pass


def initialize_prep(settings):
    prep_dir = os.path.join(settings['general']['working_directory'], settings['general']['preparations_subdir'])

    # check if the preparatory work has been done or not (clipping images)
    with open(os.path.join(prep_dir, 'log.txt'), 'a+') as log:  # a+ means append new text to file
        lines = log.readlines()
        # try to read the last line
        if len(lines) > 0:
            preparations_position = lines[-1]
        else:
            # If the file is empty, then set a default starting position
            preparations_position = settings['general']['preparations_structure']['proj_3d']
        pass

    # determine whether to start directly with the iteration or start with preparatory work
    do_preparation = not (preparations_position == 'preparations done.')
    return {"do_preparation": do_preparation,
            "step_position": preparations_position,
            "stage": "preparations"}


def initialize_detection(settings):
    check_directory_structure(settings['general']['working_directory'], [settings['general']['detection_subdir']])
    detection_dir = os.path.join(settings['general']['working_directory'], settings['general']['detection_subdir'])

    # make subdirs for each step of the detection
    check_directory_structure(detection_dir, settings['general']['iterations_structure'].values())

    config = {
        'stage': 'detection',
        'generation': 1,
        'iteration_directory': detection_dir
    }
    # append detection settings to config
    config.update(settings.detection)

    # check position in iteration from log file
    with open(os.path.join(detection_dir, 'log.txt'), 'a+') as log:  # a+ means append new text to file
        lines = log.readlines()
        # try to read the last line.
        if len(lines) > 0:
            config['step_position'] = lines[-1]
        else:
            # If the file is empty, then set a default starting position
            config['step_position'] = settings['general']['iterations_structure']['detect']

    # write iteration config settings to file
    with open(os.path.join(detection_dir, 'config.txt'), 'w') as f:
        result_writer = csv.DictWriter(f, delimiter=';', fieldnames=config.keys(),
                                       quotechar='"', quoting=csv.QUOTE_MINIMAL)

        result_writer.writeheader()
        result_writer.writerow(config)

    return config


def initialize_iterations(settings):
    # if we are supposed to start a new iteration,
    if settings['general']['start_new_iteration']:
        # create new iteration directory
        config = create_iteration_dir(settings)

    else:  # otherwise, find the last iteration process
        last_iteration_directory = latest_iteration_dir(settings)
        # check iteration config
        with open(os.path.join(last_iteration_directory, 'config.txt'), 'r') as f:
            config = next(csv.DictReader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL))

        if settings['general']['startingpoint'] == '':
            # check position in iteration from log file
            with open(os.path.join(last_iteration_directory, 'log.txt'), 'a+') as log:  # a+ means append new text to file
                lines = log.readlines()
                # try to read the last line.
                if len(lines) > 0:
                    config['step_position'] = lines[-1]
                else:
                    # If the file is empty, then set a default starting position
                    config['step_position'] = settings['general']['iterations_structure']['train']
        else:
            # use the starting point defined in the settings
            config['step_position'] = settings['general']['startingpoint']

        # if the last iteration was finished, start a new one if we haven't reached the limit
        if (config['step_position'] == 'iteration done.') & (int(config['generation']) <= int(settings['general']['folds'])):
            # start a new iteration
            config = create_iteration_dir(settings, is_first=False, previous_iteration_dir=last_iteration_directory)
            # reset the position
            config['step_position'] = settings['general']['iterations_structure']['train']

        elif config['step_position'] != 'iteration done.':
            print 'continuing iteration'
            # continue last iteration


        else:
            # stop the process. This baby is done!
            stop_iteration()

    # update settings
    return config


def latest_iteration_dir(settings):
    # find latest iteration
    iteration_dirs = os.listdir(
        os.path.join(settings['general']['working_directory'], settings['general']['iterations_subdir']))
    if len(iteration_dirs) > 0:
        return os.path.join(
            os.path.join(settings['general']['working_directory'], settings['general']['iterations_subdir']),
            sorted(iteration_dirs, reverse=True)[0])  # get latest iteration
    else:
        return create_iteration_dir(settings)['iteration_directory']


def create_iteration_dir(settings, is_first=True, previous_iteration_dir=''):
    iteration_dir = os.path.join(settings['general']['working_directory'],
                                 settings['general']['iterations_subdir'],
                                 datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
    os.makedirs(iteration_dir)
    # make subdirs for each step of the iteration
    check_directory_structure(iteration_dir, settings['general']['iterations_structure'].values())
    if not is_first:
        with open(os.path.join(previous_iteration_dir, 'config.txt'),
                  'a+') as f:  # a+ means append new text to file
            rows = csv.DictReader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # get the generation number and increment
            generation = next(rows)['generation']

        config = {
            'generation': generation,
            'step_position': settings['general']['iterations_structure']['train'],
            'stage': 'iterations',
            'neg_samples_initial_dir': os.path.join(previous_iteration_dir, settings['general']['iterations_structure']['refresh'],
                                                    'negatives', 'img'),
            'neg_samples_new_dir': os.path.join(previous_iteration_dir, settings['general']['iterations_structure']['extract'],
                                                'negatives', 'img'),
            'iteration_directory': iteration_dir
        }

    elif is_first:
        config = {
            'generation': 1,
            'step_position': settings['general']['iterations_structure']['train'],
            'stage': 'iterations',
            'neg_samples_initial_dir': os.path.join(settings['general']['working_directory'],
                                                    settings['general']['preparations_subdir'],
                                                    settings['general']['preparations_structure']['extract'],
                                                    'images', 'negatives', 'img'),
            'neg_samples_new_dir': '',
            'iteration_directory': iteration_dir
        }

    # write iteration config settings to file
    with open(os.path.join(iteration_dir, 'config.txt'), 'a+') as f:
        result_writer = csv.DictWriter(f, delimiter=';', fieldnames=config.keys(),
                                       quotechar='"', quoting=csv.QUOTE_MINIMAL)

        result_writer.writeheader()
        result_writer.writerow(config)

    return config


def stop_iteration():
    print '### ITERATIONS FINISHED'
    exit()


def update_settings(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            d[k] = update_settings(d.get(k, {}), v)
        else:
            d[k] = v
    return d

# run program
if __name__ == "__main__":
    run_all()
