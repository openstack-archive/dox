#!/bin/bash -ex

sudo gpasswd -a ${USER} docker
newgrp docker

docker run hello-world
