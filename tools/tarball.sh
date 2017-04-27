#!/bin/bash -ex

sudo gpasswd -a ${USER} docker
sudo service docker restart
newgrp docker

docker run hello-world
