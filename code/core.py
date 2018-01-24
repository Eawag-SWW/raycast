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
from s09__cluster_3d import *
from s10__evaluate_candidates import *
from s11__fit_classifiers import *
from s12__classify_clusters import *
from s13__precision_recall import  *
from s14__extract_candidate_images import *
import default_settings as settings
import csv

# Global variables
debug = True


def main():
    """Manages overall detection process, from beginning to end. This includes:
     - Read settings
     - Initialize processing
     - Error handling"""

    # read settings. No file passed implies default settings
    # print settings.general['startingpoint']

    # make sure basic directory structure is set up
    initialize_directories()
    # initialize preparatory tasks
    prep_config = initialize_prep()
    # do prep tasks
    if prep_config['do_preparation']:
        execute_steps(config=prep_config, structure=settings.general['preparations_structure'])
        helpers.write_step_to_log(prep_config, 'preparations done.')

    # do training, detection, clustering, etc
    iter_config = initialize_iterations()
    execute_steps(config=iter_config, structure=settings.general['iterations_structure'])
    helpers.write_step_to_log(iter_config, 'iteration done.')



def execute_steps(config, structure):
    step = config['step_position']
    # execute steps
    while step != 'iteration done.':
        helpers.write_step_to_log(config=config, line=step)
        print '### ' + step
        r = globals()[step.split('__')[1]](config, debug)
        if r != 0:
            print 'Error code raised'
            quit()

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


def initialize_directories():
    """Configures the processing by setting up necessary file structure."""

    # set up working directories
    working_directory = settings.general['working_directory']
    prep_dir = os.path.join(working_directory, settings.general['preparations_subdir'])

    # check if working directories exist and create otherwise
    check_directory_structure(working_directory,
                              [settings.general['preparations_subdir'], settings.general['iterations_subdir']])
    check_directory_structure(prep_dir, settings.general['preparations_structure'].values())


def check_directory_structure(home_dir, structure):
    # tests and creates directory structure
    for directory in structure:
        if not os.path.exists(os.path.join(home_dir, directory)):
            os.makedirs(os.path.join(home_dir, directory))
            if debug: print "directory created: {directory}".format(directory=directory)
    pass


def initialize_prep():
    prep_dir = os.path.join(settings.general['working_directory'], settings.general['preparations_subdir'])

    # check if the preparatory work has been done or not (clipping images)
    with open(os.path.join(prep_dir, 'log.txt'), 'a+') as log:  # a+ means append new text to file
        lines = log.readlines()
        # try to read the last line
        if len(lines) > 0:
            preparations_position = lines[-1]
        else:
            # If the file is empty, then set a default starting position
            preparations_position = settings.general['preparations_structure']['proj_3d']
        pass

    # determine whether to start directly with the iteration or start with preparatory work
    do_preparation = not (preparations_position == 'preparations done.')
    return {"do_preparation": do_preparation,
            "step_position": preparations_position,
            "stage": "preparations"}


def initialize_detection():
    check_directory_structure(settings.general['working_directory'], [settings.general['detection_subdir']])
    detection_dir = os.path.join(settings.general['working_directory'], settings.general['detection_subdir'])

    # make subdirs for each step of the detection
    check_directory_structure(detection_dir, settings.general['iterations_structure'].values())

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
            config['step_position'] = settings.general['iterations_structure']['detect']

    # write iteration config settings to file
    with open(os.path.join(detection_dir, 'config.txt'), 'w') as f:
        result_writer = csv.DictWriter(f, delimiter=';', fieldnames=config.keys(),
                                       quotechar='"', quoting=csv.QUOTE_MINIMAL)

        result_writer.writeheader()
        result_writer.writerow(config)

    return config


def initialize_iterations():
    # if we are supposed to start a new iteration,
    if settings.general['start_new_iteration']:
        # create new iteration directory
        config = create_iteration_dir()

    else:  # otherwise, find the last iteration process
        last_iteration_directory = latest_iteration_dir()
        # check iteration config
        with open(os.path.join(last_iteration_directory, 'config.txt'), 'r') as f:
            config = next(csv.DictReader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL))

        # check position in iteration from log file
        with open(os.path.join(last_iteration_directory, 'log.txt'), 'a+') as log:  # a+ means append new text to file
            lines = log.readlines()
            # try to read the last line.
            if len(lines) > 0:
                config['step_position'] = lines[-1]
            else:
                # If the file is empty, then set a default starting position
                config['step_position'] = settings.general['iterations_structure']['train']

        # if the last iteration was finished, start a new one if we haven't reached the limit
        if (config['step_position'] == 'iteration done.') & (int(config['generation']) <= int(settings.general['folds'])):
            # start a new iteration
            config = create_iteration_dir(is_first=False, previous_iteration_dir=last_iteration_directory)
            # reset the position
            config['step_position'] = settings.general['iterations_structure']['train']

        elif config['step_position'] != 'iteration done.':
            print 'continuing iteration'
            # continue last iteration


        else:
            # stop the process. This baby is done!
            stop_iteration()

    # update settings
    return config


def latest_iteration_dir():
    # find latest iteration
    iteration_dirs = os.listdir(
        os.path.join(settings.general['working_directory'], settings.general['iterations_subdir']))
    if len(iteration_dirs) > 0:
        return os.path.join(
            os.path.join(settings.general['working_directory'], settings.general['iterations_subdir']),
            sorted(iteration_dirs, reverse=True)[0])  # get latest iteration
    else:
        return create_iteration_dir()['iteration_directory']


def create_iteration_dir(is_first=True, previous_iteration_dir=''):
    iteration_dir = os.path.join(settings.general['working_directory'],
                                 settings.general['iterations_subdir'],
                                 datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
    os.makedirs(iteration_dir)
    # make subdirs for each step of the iteration
    check_directory_structure(iteration_dir, settings.general['iterations_structure'].values())
    if not is_first:
        with open(os.path.join(previous_iteration_dir, 'config.txt'),
                  'a+') as f:  # a+ means append new text to file
            rows = csv.DictReader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # get the generation number and increment
            generation = next(rows)['generation']

        config = {
            'generation': generation,
            'step_position': settings.general['iterations_structure']['train'],
            'stage': 'iterations',
            'neg_samples_initial_dir': os.path.join(previous_iteration_dir, settings.general['iterations_structure']['refresh'],
                                                    'negatives', 'img'),
            'neg_samples_new_dir': os.path.join(previous_iteration_dir, settings.general['iterations_structure']['extract'],
                                                'negatives', 'img'),
            'iteration_directory': iteration_dir
        }

    elif is_first:
        config = {
            'generation': 1,
            'step_position': settings.general['iterations_structure']['train'],
            'stage': 'iterations',
            'neg_samples_initial_dir': os.path.join(settings.general['working_directory'],
                                                    settings.general['preparations_subdir'],
                                                    settings.general['preparations_structure']['extract'],
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


# run program
main()
