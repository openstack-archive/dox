#!/bin/bash -ex

sudo gpasswd -a ${USER} docker
sudo service docker.io restart
newgrp docker

docker run hello-world
