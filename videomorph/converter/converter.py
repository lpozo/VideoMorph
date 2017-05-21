# -*- coding: utf-8 -*-
#
# File name: converter.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2015-2016 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides the definition of the Converter class."""

from PyQt5.QtCore import QProcess

from .utils import which
from .utils import spawn_process
from videomorph import CONV_LIB
from videomorph import PROBER


def get_conversion_lib():
    """Return the name of the conversion library installed on the system."""
    if which(CONV_LIB.ffmpeg):
        return CONV_LIB.ffmpeg  # Default library
    elif which(CONV_LIB.avconv):
        return CONV_LIB.avconv  # Alternative library
    return None  # Not available library


class ConversionLib:
    """Conversion Library class."""
    def __init__(self):
        self._name = get_conversion_lib()
        self.player = Player(conversion_lib_name=self.name)
        self.converter = Converter(conversion_lib_name=self.name)

    @property
    def name(self):
        """Return the name of the conversion library."""
        return self._name

    @name.setter
    def name(self, library_name):
        """Set the library_name of the conversion library."""
        self._name = library_name

    @property
    def prober(self):
        """Return the probe of the conversion library."""
        if self._name == CONV_LIB.ffmpeg:
            return PROBER.ffprobe
        elif self._name == CONV_LIB.avconv:
            return PROBER.avprobe
        else:
            return None

    def setup_converter(self, reader, finisher, process_channel):
        """Setup converter."""
        self.converter.setup(reader, finisher, process_channel)


class Converter:
    """Converter class to provide conversion functionality."""

    def __init__(self, conversion_lib_name):
        """Class initializer."""
        self.conversion_lib = conversion_lib_name

        self.process = QProcess()

    def setup(self, reader, finisher, process_channel):
        """Set up the QProcess object."""
        self.process.setProcessChannelMode(process_channel)
        self.process.readyRead.connect(reader)
        self.process.finished.connect(finisher)

    def start(self, cmd):
        """Start the encoding process."""
        self.process.start(which(self.conversion_lib), cmd)

    def stop(self):
        """Terminate encoding process."""
        self.process.terminate()
        if self.is_running:
            self.process.kill()

    def finished_disconnect(self, connected):
        """Disconnect the QProcess.finished method."""
        self.process.finished.disconnect(connected)

    def finished(self):
        """Calling QProcess.finished method."""
        self.process.finished()

    def close(self):
        """Calling QProcess.close method."""
        self.process.close()

    def kill(self):
        """Calling QProcess.kill method."""
        self.process.kill()

    def state(self):
        """Calling QProcess.state method."""
        return self.process.state()

    def exit_status(self):
        """Calling QProcess.exit_status method."""
        return self.process.exitStatus()

    @property
    def is_running(self):
        """Return the individual file encoding process state."""
        return self.process.state() == QProcess.Running

    @staticmethod
    def encoding_done(media_list):
        """Return True if media list is done."""
        return media_list.position + 1 >= media_list.length

    def read_all(self):
        """Calling QProcess.readAll method"""
        return self.process.readAll()


class Player:
    """Player class to provide a video player using ffplay."""

    def __init__(self, conversion_lib_name):
        if conversion_lib_name == CONV_LIB.ffmpeg:
            self.name = 'ffplay'
        else:
            self.name = None

    def play(self, file_path):
        """Play a video file with ffplay."""
        if self.name is not None:
            spawn_process([which(self.name), file_path])
        else:
            raise AttributeError('Payer not available')
