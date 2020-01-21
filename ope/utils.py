#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2019
# File   : utils.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 11.12.2019

from functools import wraps
import os
import stat
import sys


def touch(filename):
    '''Perform the equivalent of bash's touch on the file.

    Args:
        filename (str): File path to touch.
    '''

    open(filename, 'a').close()


class Move(object):
    '''Context manager to change current working directory.
    '''

    def __init__(self, target, create=False, verbose=False):
        '''Move to specified directory.

        Args:
            target (str): Directory to change to.
            create (bool): If True, create the directory.
        '''

        self.verbose = verbose
        self.target = target
        self.create = create
   
    def __enter__(self):
        self.cwd = os.getcwd()
        if self.verbose:
            print('Move to `{0}` from cwd: `{1}`'.format(self.target, 
                                                         self.cwd, 
                                                         file=sys.stderr))
        if self.create:
            try:
                os.mkdir(self.target)
            except OSError:
                pass
        os.chdir(self.target)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.cwd)
        if exc_type:
            return False


def which(program):
    '''Checks whether the given program (or program path) is valid and
    executable.

    NOTE: Sometimes copypasta is okay! This function came from stackoverflow:

        http://stackoverflow.com/a/377028/5109965

    Args:
        program (str): Either a program name or full path to a program.

    Returns:
        Return the path to the executable or None if not found
    '''
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


