FROM ubuntu:trusty
MAINTAINER OpenStack <openstack-dev@lists.openstack.org>

RUN apt-get update
RUN apt-get install -y wget git python

RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py
RUN pip install -U setuptools
