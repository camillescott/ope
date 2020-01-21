#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Camille Scott, 2019
# File   : utils.py
# License: MIT
# Author : Camille Scott <camille.scott.w@gmail.com>
# Date   : 11.12.2019

import os
import subprocess

from ope.io.hmmer import HMMerParser


def hmmscan_cmd(input_filename, database_filename, output_filename):
    cmd = ['hmmscan',
           '--cpu', 
           '1',
           '--domtblout', '/dev/stdout',
           '-E', '1e-05',
           '-o', '/dev/null',
           database_filename,
           input_filename,
           '>',
           output_filename]

    return cmd


def compare_hmmscan(filename_a, filename_b):
    df_a = HMMerParser(filename_a).read().sort_values('target_name').reset_index(drop=True)
    df_b = HMMerParser(filename_b).read().sort_values('target_name').reset_index(drop=True)
    print('First DF:', df_a, '\n', '=' * 40)
    print('Second DF:', df_b, '\n', '=' * 40)
    return df_a.equals(df_b)


def run_shell_cmd(cmd, fail_ok=False, in_directory=None):
    cwd = os.getcwd()
    if in_directory:
        os.chdir(in_directory)

    print('running: ', cmd)
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        (out, err) = p.communicate()

        out = out.decode('utf-8')
        err = err.decode('utf-8')

        if p.returncode != 0 and not fail_ok:
            print('out:', out)
            print('err:', err)
            raise AssertionError("exit code is non zero: %d" % p.returncode)

        return (p.returncode, out, err)
    finally:
        os.chdir(cwd)
