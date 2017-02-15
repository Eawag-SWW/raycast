# -*- coding: utf-8 -*-

# Modules

from s1__project_boundary_3d import *
from s2__project_boundary_2d import *
from s3__clip_images_2d import *
from s4__detect_objects_2d import *
from s5__cluster_2d import *
from s6__cast_rays_3d import *
from s7__cluster_3d import *
from s8__assess_visibility import *
from s9__assess_reliability import *
from s10__evaluate_detection import *

import default_settings as settings

# Global variables
debug = True
structure = ['s1__project_boundary_3d', 's2__project_boundary_2d', 's3__clip_images_2d', 's4__detect_objects_2d',
             's5__cluster_2d', 's6__cast_rays_3d', 's7__cluster_3d', 's8__assess_visibility', 's9__assess_reliability', 's10__evaluate_detection']
current_position = structure[0]


def main():
    """Manages overall detection process, from beginning to end. This includes:
 - Read settings
 - Initialize processing
 - Error handling"""

    # read settings. No file passed implies default settings
    # print settings.general['startingpoint']

    # initialize processing
    current_position = initialize()

    # deduce steps that will have to be executed
    steps_to_execute = structure[structure.index(current_position):]

    # execute steps
    for step in steps_to_execute:
        helpers.write_to_log(settings=settings, line=step)
        print '### ' + step
        r = globals()[step.split('__')[1]](structure, debug)
        if r != 0:
            break

    return 0


def initialize():
    """Configures the processing by setting up necessary file structure
    and determining the starting point of the processing. The starting point is determined either
    by reading the log file or can be imposed by the setting: Global>startingpoint."""

    # Todo: implement setting interpretation for overriding starting point

    # set up working directory
    working_directory = settings.general['working_directory']

    # check if working directory exists and create otherwise
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)
        if debug:
            print "processing directory created."

    if settings.general['startingpoint'] == 'Auto':
        # check position from log file
        with open(os.path.join(working_directory, 'log.txt'), 'a+') as log:  # a+ means append new text to file
            lines = log.readlines()
            # try to read the last line
            if len(lines) > 0:
                position = lines[-1]
                log_append = ' from log file.'
            else:
                # If the file is empty, then set a default starting position
                position = structure[0]
                log_append = ', chosen as default'
            pass
    else:
        position = structure[int(settings.general['startingpoint'])-1]
        log_append = ', as defined in settings (use "Auto" to restart processing where left off)'
    # Set up directory structure
    checkdirectorystructure(working_directory)

    if debug:
        print 'position is {currentPos}'.format(currentPos=position) + log_append

    # update settings

    return position


def checkdirectorystructure(home):
    # tests and creates directory structure
    for directory in structure:
        if not os.path.exists(os.path.join(home, directory)):
            os.makedirs(os.path.join(home, directory))
            if debug: print  "directory created: {directory}".format(directory=directory)
    pass



# run program
main()
