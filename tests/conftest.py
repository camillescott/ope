#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2019
# File   : conftest.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 12.12.2019

import os
import shutil

import pytest

from .utils import hmmscan_cmd, run_shell_cmd


TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, 'test-data')

def get_data(name):
    return os.path.join(DATA_DIR, name)


@pytest.fixture
def datadir(tmpdir, request):
    '''
    Fixture responsible for locating the test data directory and copying it
    into a temporary directory.
    '''

    def getter(filename, as_str=True):
        filepath = tmpdir.join(filename)
        shutil.copyfile(os.path.join(DATA_DIR, filename),
                        filepath)
        if as_str:
            return str(filepath)
        return filepath

    return getter


@pytest.fixture(scope='session')
def pfam(tmpdir_factory):
    h3f = get_data('Pfam-A.hmm.h3f')
    h3i = get_data('Pfam-A.hmm.h3i')
    h3m = get_data('Pfam-A.hmm.h3m')
    h3p = get_data('Pfam-A.hmm.h3p')
    
    return h3f[:-4], (h3f, h3i, h3m, h3p)


@pytest.fixture(scope='session')
def query_x_pfam(pfam, tmpdir_factory):
    pfam, _ = pfam
    query = get_data('query.100.pep.fa')
    exp_output = tmpdir_factory.mktemp('query_x_pfam').join('exp.tbl')

    exp_cmd = hmmscan_cmd(query, pfam, exp_output)
    run_shell_cmd(' '.join(map(str, exp_cmd)))

    return exp_output
