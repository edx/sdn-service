sanctions
#############################

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

Backend Django IDA for checking users against Specially Designated Nationals (SDN) - Treasury Department and Nonproliferation Sanctions (ISN) - State Department, as well as managing these sanctions hit records.
This service also maintains a fallback copy that saves data from the Consolidated Screening List provided by the ITA, which is only utilized when our primary approach by calling the government's SDN API is not an option, due to an API outage/timeout.

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

  # Install/update the dev requirements
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

How to use this service
------------------------------------------------

The sanctions endpoint will check users against the SDN API and return a hit count - if there is a match found, a record in the sanctions database (SanctionsCheckFailure) will be created.

Example of making a POST request to the `api/v1/sdn-check/` endpoint:

.. code-block::

  response = self.client.post(
      'https://sanctions.edx.org/api/v1/sdn-check/',
      timeout=settings.SANCTIONS_CLIENT_TIMEOUT,
      json={
          'lms_user_id': user.lms_user_id, # optional
          'username': user.username, # optional
          'full_name': full_name,
          'city': city,
          'country': country,
          'metadata': { # optional
              'order_identifer': 'EDX-123456',
              'purchase_type': 'program',
              'order_total': '989.00'
          },
          'system_identifier': 'commerce-coordinator', # optional
          'sdn_api_list': 'ISN,SDN', # optional, default is 'ISN,SDN'
      },
  )

Please reach out to someone on the Purchase Squad if you have questions.

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

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

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
