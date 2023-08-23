sanctions
#############################


|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

Backend Django IDA for checking users against Specially Designated Nationals (SDN) - Treasury Department and Nonproliferation Sanctions (ISN) - State Department, as well as managing these sanctions hit records.

.. TODO: The ``README.rst`` file should start with a brief description of the repository and its purpose.
.. It should be described in the context of other repositories under the ``openedx``
.. organization. It should make clear where this fits in to the overall Open edX
.. codebase and should be oriented towards people who are new to the Open edX
.. project.

Getting Started
***************

Developing
==========

One Time Setup
--------------
.. code-block::

  # Clone the repository
  git clone git@github.com:edx/sanctions.git
  cd sanctions

  # Set up a virtual environment with the same name as the repo
  # Here's how you might do that if you have virtualenvwrapper setup
  mkvirtualenv -p python3.8 sanctions
  # Or using virtualenv setup
  python3 -m venv <venv>

  # Activate the virtual environment
  source <venv>/bin/activate

  # Install/update the dev requirements inside the virtual environment
  make requirements

  # Start redis in devstack from your local devstack directory
  make dev.up.redis

  # Start this app, worker, and db containers
  make dev.up

  # Return to sanctions repo directory and provision your service
  bash provision-sanctions.sh

  # Run sanctions locally inside the virtual envioment
  python manage.py runserver localhost:18770 --settings=sanctions.settings.local 

Every time you develop something in this repo
---------------------------------------------
.. code-block::

  # Activate the virtualenv
  # Here's how you might do that if you're using virtualenvwrapper.
  workon sanctions

  # Grab the latest code
  git checkout main
  git pull

  # Install/update the dev requirements inside the virtual environment
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make validate

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<ticket_number>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim ...

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the tests and quality checks
  make validate

  # Commit all your changes
  git commit ...
  git push

  # Open a PR and ask for review.

Deploying
=========

Deployment is done via our internal GoCD service: gocd.tools.edx.org. If you need to deploy, please notify the Purchase Squad before doing so.

Getting Help
************

Documentation
=============

This is a new service, and is a work in progress (as most things are)! There is no official home for this app's technical docs just yet, but there could be soon. Please reach out to someone on the Purchase Squad if you have questions.

(TODO: `Set up documentation <https://openedx.atlassian.net/wiki/spaces/DOC/pages/21627535/Publish+Documentation+on+Read+the+Docs>`_)

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/sanctions.svg
    :target: https://pypi.python.org/pypi/sanctions/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/edx/sanctions/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/edx/sanctions/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/edx/sanctions/coverage.svg?branch=main
    :target: https://codecov.io/github/edx/sanctions?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/sanctions/badge/?version=latest
    :target: https://docs.openedx.org/projects/sanctions
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/sanctions.svg
    :target: https://pypi.python.org/pypi/sanctions/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/sanctions.svg
    :target: https://github.com/edx/sanctions/blob/main/LICENSE.txt
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
