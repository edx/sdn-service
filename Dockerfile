FROM ubuntu:focal as app
MAINTAINER sre@edx.org

# ENV variables for Python 3.12 support
ARG PYTHON_VERSION=3.12

# software-properties-common is needed to setup Python 3.12 env
RUN apt-get update && \
  apt-get install -y software-properties-common && \
  apt-add-repository -y ppa:deadsnakes/ppa

# System requirements.
RUN apt-get update
RUN apt-get install -qy \
	git-core \
	language-pack-en \
	build-essential \
	# libmysqlclient-dev header files needed to use native C implementation for MySQL-python for performance gains.
	libmysqlclient-dev \
	# mysqlclient wont install without libssl-dev
	libssl-dev \
	# mysqlclient>=2.2.0 requires pkg-config (https://github.com/PyMySQL/mysqlclient/issues/620)
	pkg-config \
	curl \
	python3-pip \
	python${PYTHON_VERSION} \
	python${PYTHON_VERSION}-dev

# need to use virtualenv pypi package with Python 3.12
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION}
RUN pip install virtualenv

# delete apt package lists because we do not need them inflating our image
RUN rm -rf /var/lib/apt/lists/*

# Python is Python3.
RUN ln -s /usr/bin/python3 /usr/bin/python

# Use UTF-8.
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV DJANGO_SETTINGS_MODULE sanctions.settings.production

EXPOSE 18770
EXPOSE 18771
RUN useradd -m --shell /bin/false app

ENV VIRTUAL_ENV_DIR=/edx/app/sanctions/venv
ENV PATH="$VIRTUAL_ENV_DIR/bin:$PATH"

RUN virtualenv -p python${PYTHON_VERSION} --always-copy ${VIRTUAL_ENV_DIR}

RUN pip install --upgrade pip setuptools

WORKDIR /edx/app/sanctions

# Copy the requirements explicitly even though we copy everything below
# this prevents the image cache from busting unless the dependencies have changed.
COPY requirements/production.txt /edx/app/sanctions/requirements/production.txt

RUN pip install -r requirements/production.txt

RUN mkdir -p /edx/var/log

# Code is owned by root so it cannot be modified by the application user.
# So we copy it before changing users.
USER app

# Gunicorn 19 does not log to stdout or stderr by default. Once we are past gunicorn 19, the logging to STDOUT need not be specified.
CMD gunicorn --workers=2 --name sanctions -c /edx/app/sanctions/sanctions/docker_gunicorn_configuration.py --log-file - --max-requests=1000 sanctions.wsgi:application

# This line is after the requirements so that changes to the code will not
# bust the image cache
COPY . /edx/app/sanctions

FROM app as devstack
USER root
COPY requirements/dev.txt /edx/app/sanctions/requirements/dev.txt
RUN pip install -r requirements/dev.txt
USER app
CMD gunicorn --workers=2 --name sanctions -c /edx/app/sanctions/sanctions/docker_gunicorn_configuration.py --log-file - --max-requests=1000 sanctions.wsgi:application
