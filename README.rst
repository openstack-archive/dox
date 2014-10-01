===
dox
===

dox is a tool for using docker containers to run local tests, inspired by
tox and virtualenv for python. There are two elements to its configuration:

* What commands should be run?

* In what image should they be run?

If there is a dox.yml file, you're set. You want to specify what image to
use and what commands to run. You win::

  image: ubuntu:trusty
  commands: |
    pip install . -r test-requirements.txt
    python setup.py test

You might either not be willing to commit to dox as a way of life yet, or you
may want to use dox in a project that similarly has not done so.

What commands should be run
---------------------------

dox.yml wins.

If there is a tox.ini file, the commands specified in the base [testenv]
will be used.

If there is a .travis.yml file, the script section will be used.

If there are none of those things, dox will do its best to infer what
should be done. Examining the directory can often provide hints if you
haven't been too clever. For instance, if you have a Gruntfile, you probably
want to run grunt. If you have a Makefile, then make && make test is probably
your bag. If you have a Makefile.am, you probably want to run autotools first.
If you have a setup.py file, python setup.py test is a likely choice (although
in that case, you probably haven't done it right because setuptools support
for this is quite awful.)

After all of that, if we still can't figure out what you want - it's probably
easiest to just edit a file called dox.yml and put in a section telling us
what to do.

In what image should they be run
--------------------------------

Again, dox.yml wins, and thanks for making things easy!

If there is a tox.ini file, and it contains a [docker] section, the value in
"image" will be used::

  [docker]
  image=ubuntu:trusty

If there is not an image key in the docker section or an image key in the
dox.yml but there is a Dockerfile in the repo, an new image will be built
using the Dockerfile and the test commands will be run inside of the image.

If all of that fails, tests are going to run in a bare ubuntu image. Good luck!

Image Caching
-------------

Every run actually has two images associated with it: The `base` image and
the `test` image.

The image referenced above is the `base` image. When you execute `dox`,
it will search docker for the named image. If it exists, it will do nothing.
If it does not, it will either pull it, or, it will build it from the
Dockerfile. In the case of building from a Dockerfile, dox will make an image
named for the source directory. So if you're in ~/src/openstack/nova, it'll
make an image called "dox/nova/base".

The `test` image is an image made by dox for the test run. Similar to the
base run, it'll have a generated name, such as "dox/nova/test", and similar
to the base image, it will get generated once and then left alone.

If you want to regenerate the `test` image, you can run dox with the `-r`
option. If you want to regenerate/repull everything, you can run it with the
`--rebuild-all` option.

The reasoning behind this is that the base image should really be the
substrata which doesn't have a lot to do with the repo itself ... it shouldn't
really expect to change much based on day to day changes in the repo. The
test image on the other hand is built a bit more based on the repo itself.
So, for instance, in the base image you might want to do things like::

  apt-get install libxml-dev

and in the test image, you'd want things like::

  pip install -U requirements.txt

Neither change frequently, but the second it more likely to change day to day
than the first.

Additional information
----------------------

Regardless, dox will mount the current source dir as a volume at `/src` in
the container and will run commands in that context.

dox will attempt to reuse containers.  Since the source is bind-mounted into
the container, things that might be expensive like copying source dirs or
re-installing the source into the system can be minimized.

Boot2Docker support
-------------------

To get support for non Linux OSes that doesn't support natively docker
there is a tool called `boot2docker <http://boot2docker.io/>`_ which
allows you to run a remote docker server in a VirtualBox VM and the
client running on the non Linux desktop.

There is no support for mounted volumes by default with `boot2docker` which is needed by `dox`.
To get this feature you will need to follow these steps documented here :

https://medium.com/boot2docker-lightweight-linux-for-docker/boot2docker-together-with-virtualbox-guest-additions-da1e3ab2465c

When running dox you will need to specify the docker username from the boot2docker vm, commonly like this::

  dox --user-map=docker:1000:10

Advanced
--------
It is possible to specify multiple images to be used in a dox run.
Images can be provided on the command line, via the dox.yml file, or the
tox.ini file.

For the command line, images should be provided via the --images option,
in a comma-separated list.

The tox.ini file should also use a comma-separated list.

The dox.yml file should list images in an array.

The same prep and command instructions will be executed on each image sequentially.

dox does not currently allow for multiple images executing different tasks
at this time.  However, it is a goal to allow for such test scenarios in 
the future.
