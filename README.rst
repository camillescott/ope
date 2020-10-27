=========
ope
=========

.. image:: https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat
        :target: http://bioconda.github.io/recipes/ope/README.html

.. image:: https://img.shields.io/pypi/v/ope.svg
        :target: https://pypi.python.org/pypi/ope

.. image:: https://img.shields.io/travis/camillescott/ope.svg
        :target: https://travis-ci.org/camillescott/ope

.. image:: https://readthedocs.org/projects/ope/badge/?version=latest
        :target: https://ope.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Abstracts away running `gnu-parallel` on tools with FASTA input and provides parsers for some common
formats produced by said tools.

Example usage::

   ope parallel -j 4 [query.pep.fa] hmmscan --domtblout [results.tbl] -E 1e-05 -o /dev/null /store/biodb/Pfam-A.hmm /dev/stdin

Hence, the only `gnu-parallel` flag one needs to worry about is `-j` for the number of cores to use.
Note that you also need to set the input in the actual tool invocation as `/dev/stdin`.

* Free software: MIT license
* Documentation: https://ope.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
