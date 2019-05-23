# -*- coding: utf-8 -*-

# Copyright 2017 Juan José Martín Miralles
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Python modules
import os
import warnings

# Own modules
from trackanimation.tracking import ReadTrack
from trackanimation.tracking import TrackException


def readTrack(directory_or_file, files_to_read=None):
    warnings.warn("The readTrack function is deprecated and "
                  "will be removed in version 2.0.0. "
                  "Use the read_track function instead.",
                  FutureWarning,
                  stacklevel=8
                  )
    return read_track(directory_or_file, files_to_read)


def read_track(directory_or_file, files_to_read=None):
    read_track = ReadTrack(directory_or_file)

    if directory_or_file.lower().endswith(('.csv')):
        return read_track.read_csv()
    elif directory_or_file.lower().endswith(('.gpx')) or os.path.isdir(directory_or_file):
        return read_track.read_gpx(files_to_read)
    else:
        raise TrackException('Must specify a valid file name', directory_or_file)
