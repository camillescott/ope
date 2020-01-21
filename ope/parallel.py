#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2019
# File   : parallel.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 11.12.2019

import os
import subprocess

from .utils import which


MIN_VERSION = 20171222


def parallel_fasta(input_filename,
                   n_jobs, 
                   check_dep=True):

    '''Given an input FASTA source, target, shell command, and number of jobs,
    construct a gnu-parallel command to act on the sequences.

    Args:
        input_filename (str): The source FASTA.
        n_jobs (int): Number of cores or nodes to split to.
    Returns:
        str: The constructed shell command.
    '''
    
    exc = which('parallel') if not check_dep else check_parallel()

    cmd = [exc,
           '-a', input_filename,
           '--block', '-1',
           '--pipepart',
           '--recstart', '\'>\'',
           '--gnu',
           '-j', str(n_jobs)]

    return cmd


def parallel_fasta_pipe(n_jobs,
                        file_size_kb=10,
                        check_dep=True):

    exc = which('parallel') if not check_dep else check_parallel()
    block_size = file_size_kb // n_jobs
    
    cmd = [exc,
           '--block', f'{block_size}K',
           '--pipe',
           '--recstart', '\'>\'',
           '--gnu',
           '-j', str(n_jobs)]

    return cmd


def check_parallel():
    parallel = which('parallel')

    if parallel is None:
        raise RuntimeError('parallel not found.')
    else:
        try:
            version_string = subprocess.check_output(['parallel', '--version'])
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Error checking parallel '\
                                'version: [{e.returncode}] {e.output}')
        except OSError as e:
            raise RuntimeError(f'Error checking parallel version: '\
                                '[{e.errno}] {str(e)}')
        else:
            version = version_string.strip().split()[2]
            if int(version) < MIN_VERSION:
                raise RuntimeError(f'parallel version {version} < {MIN_VERSION}, '\
                                    'please update')
            return parallel
