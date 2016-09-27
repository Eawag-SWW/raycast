# -*- coding: utf-8 -*-

# Modules
import SettingReader
import os

import helpers

from s1_project_boundary_3d import *
from s2_project_boundary_2d import *
from s3_clip_images_2d import *
from s4_detect_objects_2d import *
from s5_cluster_2d import *
from s6_cast_rays_3d import *
from s7_cluster_3d import *
from s8_assess_visibility import *
from s9_assess_reliability import *


# Global variables
debug = True
structure = ['s1_project_boundary_3d', 's2_project_boundary_2d', 's3_clip_images_2d', 's4_detect_objects_2d',
             's5_cluster_2d', 's6_cast_rays_3d', 's7_cluster_3d', 's8_assess_visibility', 's9_assess_reliability']
current_position = structure[0]


def main():
    """Manages overall detection process, from beginning to end. This includes:
 - Read settings
 - Initialize processing
 - Error handling"""

    # read settings. No file passed implies default settings
    settings = SettingReader.SettingReader(None)
    # print settings.values['Global']['startingpoint']

    # initialize processing
    current_position = initialize(settings)

    # deduce steps that will have to be executed
    steps_to_execute = structure[structure.index(current_position):]

    # execute steps
    for step in steps_to_execute:
        helpers.write_to_log(settings=settings, line=step)
        print '### ' + step
        r = globals()[step[3:]](settings, structure, debug)
        if r != 0:
            break


    return 0


def initialize(settings):
    """Configures the processing by setting up necessary file structure
    and determining the starting point of the processing. The starting point is determined either
    by reading the log file or can be imposed by the setting: Global>startingpoint."""

    # Todo: implement setting interpretation for overriding starting point

    # set up working directory
    working_directory = settings.values['Global']['working_directory']

    # check if working directory exists and create otherwise
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)
        if debug:
            print "processing directory created."

    if settings.values['Global']['startingpoint'] == 'Auto':
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
        position = structure[int(settings.values['Global']['startingpoint'])-1]
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
