#!/bin/bash -ex

GROUP=docker
if [ $(id -gn) != ${GROUP} ]; then
  sudo gpasswd -a ${USER} ${GROUP}
  sudo service docker restart
  exec sg ${GROUP} "$0 $*"
fi

### Build image with docker
IMAGE=infra/trusty
docker build dockerfiles/$IMAGE -t $IMAGE

DIST=$WORKSPACE/dist
mkdir -p $DIST

### Save docker image for upload to tarballs.o.o
TRIMMED_IMAGE=${IMAGE/\//_}
docker save $IMAGE | gzip -9 > $DIST/$TRIMMED_IMAGE.tar.gz
shasum $DIST/$TRIMMED_IMAGE.tar.gz > $DIST/$TRIMMED_IMAGE.tar.gz.sha256
