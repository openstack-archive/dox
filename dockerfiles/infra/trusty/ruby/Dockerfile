FROM ubuntu:trusty
MAINTAINER OpenStack <openstack-dev@lists.openstack.org>

RUN export PUPPET_GEM_VERSION='~> 3.4.0'
RUN mkdir .bundled_gems
RUN export GEM_HOME=`pwd`/.bundle
RUN bundle install
