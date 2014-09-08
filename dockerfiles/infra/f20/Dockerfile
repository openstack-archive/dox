FROM fedora:20
MAINTAINER OpenStack <openstack-dev@lists.openstack.org>

RUN yum -y update
RUN yum -y groupinstall 'Development Tools'
RUN yum -y install wget git python

RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py
RUN pip install -U setuptools
