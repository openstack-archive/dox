#!/bin/bash -ex
# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

GROUP=docker
if [ $(id -gn) != ${GROUP} ]; then
  exec sg ${GROUP} "$0 $*"
fi

### Build image with docker
IMAGES="infra/centos7 infra/trusty"
for IMAGE in $IMAGES; do
    docker build dockerfiles/$IMAGE -t $IMAGE
done

docker images

# NOTE(pabelanger): Make sure we hash by ZUUL_COMMIT, so we know which tarball
# to download from secure worker.
DIST=$WORKSPACE/dist/$ZUUL_COMMIT
mkdir -p $DIST

### Save docker image for upload to tarballs.o.o
FILENAME=images.tar.gz
docker save $IMAGES | gzip -9 > $DIST/$FILENAME
shasum $DIST/$FILENAME > $DIST/$FILENAME.sha256
