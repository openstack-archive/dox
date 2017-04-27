#!/bin/bash -ex

GROUP=docker
if [ $(id -gn) != ${GROUP} ]; then
  sudo gpasswd -a ${USER} ${GROUP}
  sudo service docker restart
  exec sg ${GROUP} "$0 $*"
fi

docker run hello-world

mkdir -p $WORKSPACE/dist
docker save hello-world | gzip -9 > $WORKSPACE/dist/hello-world.tar.gz
