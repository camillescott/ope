"""Console script for ope."""

import subprocess
import sys

import click

from .parallel import parallel_fasta, parallel_fasta_pipe


@click.group()
def main(args=None):
    pass


@main.command(name='parallel',
              context_settings=dict(
                  ignore_unknown_options=True,
              ))
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--n_jobs', '-j', default=0)
@click.argument('cmd_args', nargs=-1, type=click.UNPROCESSED)
def run_parallel(input_file, n_jobs, cmd_args):
    if input_file in ('/dev/stdin', '-'):
        pcmd = parallel_fasta_pipe(n_jobs)
    else:
        pcmd = parallel_fasta(input_file, n_jobs)

    cmd = ' '.join(pcmd + list(cmd_args))
    print(cmd, file=sys.stderr)
    subprocess.run(cmd, shell=True)

