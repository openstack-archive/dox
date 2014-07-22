===
dox
===

dox is a tool for using docker containers to run local tests, inspired by
tox and virtualenv for python. There are two elements to its configuration:

* What commands should be run?

* In what image should they be run?

If there is a dox.yml file, you're set. You want a docker section to specify
what image to use and a testenv section to specify the commands to run. You
win.

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

If there is not an image key in the docker section but there is a Dockerfile
in the repo, an image will be built using the Dockerfile and the test
commands will be run inside of the image.

Additional information
----------------------

Regardless, dox will mount the current source dir as a volume at `/src` in
the container and will run commands in that context.

dox will attempt to reuse containers.  Since the source is bind-mounted into
the container, things that might be expensive like copying source dirs or
re-installing the source into the system can be minimized.

Advanced
--------
The dox.yml file can reference multiple images, such as if your test suite
needs things like a MySQL server. At least, that's the theory. This is not
yet implemented.
