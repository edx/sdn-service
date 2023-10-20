FROM ubuntu:focal as app
MAINTAINER sre@edx.org


# Packages installed:

# language-pack-en locales; ubuntu locale support so that system utilities have a consistent
# language and time zone.

# python; ubuntu doesnt ship with python, so this is the python we will use to run the application

# python3-pip; install pip to install application requirements.txt files

# libmysqlclient-dev; to install header files needed to use native C implementation for
# MySQL-python for performance gains.

# libssl-dev; # mysqlclient wont install without this.

# python3-dev; to install header files for python extensions; much wheel-building depends on this

# gcc; for compiling python extensions distributed with python packages like mysql-client


# set timezone to prevent geographic location from hanging see https://dev.to/grigorkh/fix-tzdata-hangs-during-docker-image-build-4o9m
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo


# If you add a package here please include a comment above describing what it is used for
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -qy install --no-install-recommends \
 language-pack-en \
 locales \
 python3.9 \
 python3.9-dev \
 python3-pip \
 pkg-config \
 libmysqlclient-dev \
 libssl-dev \
 gcc \
 build-essential \
 git \
 wget \
 curl

# Create a symbolic link between python3 and python3.9
RUN ln -s /usr/bin/python3.9 /usr/bin/python

# Need to overwrite python3 with python3.9 as well, because
# helm template invokes `python3` directly in migrations init container
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3

# Install pip for Python 3.9
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Create a symbolic link between pip and pip3.9
RUN ln -sf /usr/bin/pip3 /usr/bin/pip

RUN pip install --upgrade pip setuptools

# delete apt package lists because we do not need them inflating our image
RUN rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV DJANGO_SETTINGS_MODULE sanctions.settings.production

EXPOSE 18770
EXPOSE 18771
RUN useradd -m --shell /bin/false app

WORKDIR /edx/app/sanctions

# Copy the requirements explicitly even though we copy everything below
# this prevents the image cache from busting unless the dependencies have changed.
COPY requirements/production.txt /edx/app/sanctions/requirements/production.txt

# Dependencies are installed as root so they cannot be modified by the application user.
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
