# -*- coding: utf-8 -*-

# Modules

from s1__project_boundary_3d import *
from s2__project_boundary_2d import *
from s3__clip_images_2d import *
from s4__extract_initial_samples import *
from s5__refresh_training_sets import *
from s6__retrain_classifier import *
from s7__detect_objects_2d import *
from s8__cast_rays_3d import *
from s9__cluster_3d import *
from s11__fit_binary_model import *
from s10__evaluate_candidates import *
from s12__extract_candidate_images import *
import default_settings as settings

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
    if prep_config['do_preparation'] == True:
        execute_steps(config=prep_config, structure=settings.general['preparations_structure'])
        helpers.write_step_to_log(prep_config, 'preparations done.')

    # do iteration until it is stopped from within
    while True:
        # initialize current iteration
        iter_config = initialize_iterations()
        execute_steps(config=iter_config, structure=settings.general['iterations_structure'])
        helpers.write_step_to_log(iter_config, 'iteration done.')


def execute_steps(config, structure):
    step = config['position']
    # execute steps
    while step != 'iteration done.':
        helpers.write_step_to_log(config=config, line=step)
        print '### ' + step
        r = globals()[step.split('__')[1]](config, debug)
        if r != 0:
            break
        step = get_next_step(step, structure)
        if not step:
            step = 'iteration done.'
    return 0


def get_next_step(current_step, structure):
    index = structure.index(current_step) + 1
    if index >= len(structure):
        return False
    else:
        return structure[structure.index(current_step) + 1]


def initialize_directories():
    """Configures the processing by setting up necessary file structure
    and determining the starting point of the processing. The starting point is determined either
    by reading the log file or can be imposed by the setting: Global>startingpoint."""

    # set up working directories
    working_directory = settings.general['working_directory']
    prep_dir = os.path.join(working_directory, settings.general['preparations_subdir'])

    # check if working directories exist and create otherwise
    check_directory_structure(working_directory,
                              [settings.general['preparations_subdir'], settings.general['iterations_subdir']])
    check_directory_structure(prep_dir, settings.general['preparations_structure'])


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
            preparations_position = settings.general['preparations_structure'][0]
        pass

    # determine whether to start directly with the iteration or start with preparatory work
    do_preparation = not (preparations_position == 'preparations done.')
    return {"do_preparation": do_preparation,
            "position": preparations_position,
            "stage": "preparations"}


def initialize_iterations():
    iteration_directory = ''
    iteration_position = ''
    # if we are supposed to start a new iteration,
    if settings.general['start_new_iteration']:
        # create new iteration directory
        (iteration_directory, generation, classifier_path, binary_model_path) = create_iteration_dir()

    else:  # otherwise, find the last iteration process
        last_iteration_directory = latest_iteration_dir()
        # check iteration config
        with open(os.path.join(last_iteration_directory, 'config.txt'), 'a+') as config:
            lines = config.readlines()
            # get the generation number
            generation = int(lines[0])
            # get the classifier and binary model info
            classifier_path = lines[1].rstrip('\n')
            binary_model_path = lines[2].rstrip('\n')

        # check position in iteration from log file
        with open(os.path.join(last_iteration_directory, 'log.txt'), 'a+') as log:  # a+ means append new text to file
            lines = log.readlines()
            # try to read the last line.
            if len(lines) > 0:
                iteration_position = lines[-1]
            else:
                # If the file is empty, then set a default starting position
                iteration_position = settings.general['iterations_structure'][0]

        # if the last iteration was finished, start a new one if we haven't reached the limit
        if (iteration_position == 'iteration done.') & (generation < settings.general['max_generations']):
            # start a new iteration
            (iteration_directory,
             generation,
             classifier_path,
             binary_model_path) = create_iteration_dir(is_first=False, previous_iteration_dir=last_iteration_directory)
            # reset the position
            iteration_position = settings.general['iterations_structure'][0]

        elif iteration_position != 'iteration done.':
            # continue last iteration
            iteration_directory = last_iteration_directory

        else:
            # stop the process. This baby is done!
            stop_iteration()

    # update settings
    return {"iteration_directory": iteration_directory,
            "position": iteration_position,
            "generation": generation,
            "classifier_path": classifier_path,
            "binary_model_path": binary_model_path,
            "stage": "iterations"}


def latest_iteration_dir():
    # find latest iteration
    iteration_dirs = os.listdir(
        os.path.join(settings.general['working_directory'], settings.general['iterations_subdir']))
    if len(iteration_dirs) > 0:
        return os.path.join(
            os.path.join(settings.general['working_directory'], settings.general['iterations_subdir']),
            sorted(iteration_dirs, reverse=True)[0])  # get latest iteration
    else:
        return create_iteration_dir()[0]


def create_iteration_dir(is_first=True, previous_iteration_dir=''):
    iteration_dir = os.path.join(settings.general['working_directory'],
                                 settings.general['iterations_subdir'],
                                 datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
    os.makedirs(iteration_dir)
    # make subdirs for each step of the iteration
    check_directory_structure(iteration_dir, settings.general['iterations_structure'])
    if not is_first:
        with open(os.path.join(previous_iteration_dir, 'config.txt'),
                  'a+') as config:  # a+ means append new text to file
            lines = config.readlines()
            # get the generation number and increment
            generation = int(lines[0]) + 1
        classifier_path = os.path.join(previous_iteration_dir, settings.general['iterations_structure'][5],
                                       'cascade.xml')
        binary_model_path = os.path.join(previous_iteration_dir, settings.general['iterations_structure'][6],
                                         'binary_model.py')
    elif is_first:
        generation = 1
        classifier_path = settings.inputs['classifier_default']
        binary_model_path = settings.inputs['binary_model_default']

    # write iteration config settings to file
    with open(os.path.join(iteration_dir, 'config.txt'), 'a+') as config:
        config.write(str(generation) + '\n')
        config.write(classifier_path + '\n')
        config.write(binary_model_path + '\n')
    return iteration_dir, generation, classifier_path, binary_model_path


def stop_iteration():
    print '### ITERATIONS FINISHED'
    exit()


# run program
main()
