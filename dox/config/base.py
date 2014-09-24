# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class ConfigBase(object):
    """Configuration file reader base class."""

    @abc.abstractmethod
    def exists(self):
        """Check if the configuration file is present.

        :returns: True if the file is present.
        :returns: False if the file is not present.
        """

    @abc.abstractmethod
    def get_images(self):
        """Get list of docker source images used to build the test image.

        :returns: List of image names in <user>/<repo>[:<tag>] format.
        """

    @abc.abstractmethod
    def get_commands(self):
        """Get list of commands to execute with the final test image.

        These commands will be executed via the 'docker run' command
        with the final test image.

        :returns: List of executable commands.
        """

    @abc.abstractmethod
    def get_prep_commands(self):
        """Get list of commands to run while building the test image.

        These commands will be executed while building the test image,
        thus allowing for any software installation, configuration, etc.
        to be built into the test image.

        :returns: List of executable commands.
        """

    @abc.abstractmethod
    def get_add_files(self):
        """Get list of files to add to the test image.

        The named files will be placed in the working directory of the
        built test image.

        :returns: List of file names.
        """

    @abc.abstractmethod
    def source_name(self):
        """The source of the configuration.

        This identifies the source of the configuration values. E.g.,
        a file name, or other descriptive text.

        :returns: String describing the source.
        """
