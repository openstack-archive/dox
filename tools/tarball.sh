#!/bin/bash -ex

GROUP=docker
if [ $(id -gn) != ${GROUP} ]; then
  sudo gpasswd -a ${USER} ${GROUP}
  sudo service docker restart
  exec sg ${GROUP} "$0 $*"
fi

docker run hello-world

DIST=$WORKSPACE/dist
mkdir -p $DIST
IMAGE=hello-world
docker save $IMAGE | gzip -9 > $DIST/$IMAGE.tar.gz
shasum $DIST/$IMAGE.tar.gz > $DIST/$IMAGE.tar.gz.sha256
