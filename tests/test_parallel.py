#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2019
# File   : test_parallel.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 12.12.2019

import pytest

from .utils import run_shell_cmd, hmmscan_cmd, compare_hmmscan


@pytest.mark.parametrize('n_threads', [1,2,4])
def test_parallel_pipepart(pfam, tmpdir, datadir, query_x_pfam, n_threads):
    pfam, _ = pfam
    query = datadir('query.100.pep.fa')
    par_output = 'parallel.tbl'

    with tmpdir.as_cwd():
        par_cmd = ['ope',
                   'parallel',
                   '-j',
                   n_threads,
                   query]
        par_cmd += hmmscan_cmd('/dev/stdin', pfam, par_output)
        run_shell_cmd(' '.join(map(str, par_cmd)))

        assert compare_hmmscan(query_x_pfam, par_output)
