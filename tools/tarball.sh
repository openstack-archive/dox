#!/bin/bash -ex

GROUP=docker
if [ $(id -gn) != ${GROUP} ]; then
  sudo gpasswd -a ${USER} ${GROUP}
  sudo service docker restart
  exec sg ${GROUP} "$0 $*"
fi

### Build image with docker
IMAGES="infra/centos7 infra/trusty"
for IMAGE in $IMAGES; do
    docker build dockerfiles/$IMAGE -t $IMAGE
done

# NOTE(pabelanger): Make sure we hash by ZUUL_COMMIT, so we know which tarball
# to download from secure worker.
DIST=$WORKSPACE/dist/$ZUUL_COMMIT
mkdir -p $DIST

### Save docker image for upload to tarballs.o.o
FILENAME=images.tar.gz
docker save $IMAGES | gzip -9 > $DIST/$FILENAME
shasum $DIST/$FILENAME > $DIST/$FILENAME.sha256
