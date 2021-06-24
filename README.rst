========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - |
        |
    * - package
      - | |commits-since|

.. |commits-since| image:: https://img.shields.io/github/commits-since/mengsha-sun/experiment-utils/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/mengsha-sun/experiment-utils/compare/v0.0.0...master



.. end-badges

Utils for experiment design and analysis.

Installation
============

::

    pip install -e git+https://github.com/mengsha-sun/experiment-utils.git#egg=experiment_utils

You can also install a specific version or branch with::

    pip install git+https://github.com/mengsha-sun/experiment-utils.git@v1.0.0#egg=experiment_utils
    pip install git+https://github.com/mengsha-sun/experiment-utils.git@master#egg=experiment_utils


Documentation
=============


To use the project:

.. code-block:: python

    import experiment_utils
    experiment_utils.longest()


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
