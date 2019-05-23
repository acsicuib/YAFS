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
import math
import warnings
import datetime
import datetime as dt
from datetime import datetime

# Third party modules
import geopy
import geopy.distance as geo_dist
import pandas as pd

TIME_FORMATS = ['%H:%M', '%H%M', '%I:%M%p', '%I%M%p', '%H:%M:%S', '%H%M%S', '%I:%M:%S%p', '%I%M%S%p']


class TrackException(Exception):
    """
    Generic exception for TrackAnimation
    """

    def __init__(self, msg, original_exception):
        super(TrackException, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception


def getBearing(start_point, end_point):
    """
    Calculates the bearing between two points.

    Parameters
    ----------
    start_point: geopy.Point
    end_point: geopy.Point

    Returns
    -------
    point: int
        Bearing in degrees between the start and end points.
    """
    warnings.warn("The getBearing function is deprecated and "
                  "will be removed in version 2.0.0. "
                  "Use the get_bearing function instead.",
                  FutureWarning,
                  stacklevel=8
                  )
    return get_bearing(start_point, end_point)


def get_bearing(start_point, end_point):
    """
    Calculates the bearing between two points.

    Parameters
    ----------
    start_point: geopy.Point
    end_point: geopy.Point

    Returns
    -------
    point: int
        Bearing in degrees between the start and end points.
    """
    start_lat = math.radians(start_point.latitude)
    start_lng = math.radians(start_point.longitude)
    end_lat = math.radians(end_point.latitude)
    end_lng = math.radians(end_point.longitude)

    d_lng = end_lng - start_lng
    if abs(d_lng) > math.pi:
        if d_lng > 0.0:
            d_lng = -(2.0 * math.pi - d_lng)
        else:
            d_lng = (2.0 * math.pi + d_lng)

    tan_start = math.tan(start_lat / 2.0 + math.pi / 4.0)
    tan_end = math.tan(end_lat / 2.0 + math.pi / 4.0)
    d_phi = math.log(tan_end / tan_start)
    bearing = (math.degrees(math.atan2(d_lng, d_phi)) + 360.0) % 360.0

    return bearing


def getCoordinates(start_point, end_point, distance_meters):
    """
    Calculates the new coordinates between two points depending
    of the specified distance and the calculated bearing.

    Parameters
    ----------
    start_point: geopy.Point
    end_point: geopy.Point
    distance_meters: float

    Returns
    -------
    point: geopy.Point
        A new point between the start and the end points.
    """
    warnings.warn("The getCoordinates function is deprecated and "
                  "will be removed in version 2.0.0. "
                  "Use the get_coordinates function instead.",
                  FutureWarning,
                  stacklevel=8
                  )
    return get_coordinates(start_point, end_point, distance_meters)


def get_coordinates(start_point, end_point, distance_meters):
    """
    Calculates the new coordinates between two points depending
    of the specified distance and the calculated bearing.

    Parameters
    ----------
    start_point: geopy.Point
    end_point: geopy.Point
    distance_meters: float

    Returns
    -------
    point: geopy.Point
        A new point between the start and the end points.
    """
    bearing = get_bearing(start_point, end_point)

    distance_km = distance_meters / 1000
    d = geo_dist.VincentyDistance(kilometers=distance_km)
    destination = d.destination(point=start_point, bearing=bearing)

    return geopy.Point(destination.latitude, destination.longitude)


def getPointInTheMiddle(start_point, end_point, time_diff, point_idx):
    """
    Calculates a new point between two points depending of the
    time difference between them and the point index.

    Parameters
    ----------
    start_point: DataFrame
    end_point: DataFrame
    time_diff: float
    point_idx: int
        Point index between the start and the end points

    Returns
    -------
    point: list
        A new point between the start and the end points.
    """
    warnings.warn("The getPointInTheMiddle function is deprecated and "
                  "will be removed in version 2.0.0. "
                  "Use the get_point_in_the_middle function instead.",
                  FutureWarning,
                  stacklevel=8
                  )
    return get_point_in_the_middle(start_point, end_point, time_diff, point_idx)


def get_point_in_the_middle(start_point, end_point, time_diff, point_idx):
    """
    Calculates a new point between two points depending of the
    time difference between them and the point index.

    Parameters
    ----------
    start_point: DataFrame
    end_point: DataFrame
    time_diff: float
    point_idx: int
        Point index between the start and the end points

    Returns
    -------
    point: list
        A new point between the start and the end points.
    """
    time_proportion = (time_diff * point_idx) / end_point['TimeDifference'].item()

    distance_proportion = end_point['Distance'].item() * time_proportion
    time_diff_proportion = end_point['TimeDifference'].item() * time_proportion
    speed = distance_proportion / time_diff_proportion
    distance = time_diff * speed
    cum_time_diff = int(start_point['CumTimeDiff'].item() + time_diff_proportion)
    # date = datetime.strptime(start_point['Date'].item(), '%Y-%m-%d %H:%M:%S') + dt.timedelta(seconds=int(
    # time_diff_proportion))
    date = pd.to_datetime(start_point['Date'].astype(str), format='%Y-%m-%d %H:%M:%S') + dt.timedelta(
        seconds=int(time_diff_proportion))
    altitude = (end_point['Altitude'].item() + start_point['Altitude'].item()) / 2
    name = start_point['CodeRoute'].item()

    geo_start = geopy.Point(start_point['Latitude'].item(), start_point['Longitude'].item())
    geo_end = geopy.Point(end_point['Latitude'].item(), end_point['Longitude'].item())
    middle_point = get_coordinates(geo_start, geo_end, distance_proportion)

    df_middle_point = ([[name, middle_point.latitude, middle_point.longitude, altitude,
                         date, speed, int(time_diff), distance, None, cum_time_diff]])

    return df_middle_point


def rgb(value, minimum, maximum):
    """
    Calculates an rgb color of a value depending of
    the minimum and maximum values.

    Parameters
    ----------
    value: float or int
    minimum: float or int
    maximum: float or int

    Returns
    -------
    rgb: tuple
    """
    value = float(value)
    minimum = float(minimum)
    maximum = float(maximum)

    if minimum == maximum:
        ratio = 0
    else:
        ratio = 2 * (value - minimum) / (maximum - minimum)

    b = int(max(0, 255 * (1 - ratio)))
    r = int(max(0, 255 * (ratio - 1)))
    g = 255 - b - r

    return r / 255.0, g / 255.0, b / 255.0


def calculateCumTimeDiff(df):
    """
    Calculates the cumulative of the time difference
    between points for each track of 'dfTrack'.
    """
    warnings.warn("The calculateCumTimeDiff function is deprecated and "
                  "will be removed in version 2.0.0. "
                  "Use the calculate_cum_time_diff function instead.",
                  FutureWarning,
                  stacklevel=8
                  )
    return calculate_cum_time_diff(df)


def calculate_cum_time_diff(df):
    """
    Calculates the cumulative of the time difference
    between points for each track of 'dfTrack'.
    """
    df = df.copy()

    df_cum = pd.DataFrame()
    grouped = df['CodeRoute'].unique()

    for name in grouped:
        df_slice = df[df['CodeRoute'] == name]
        df_slice = df_slice.reset_index(drop=True)
        df_slice['CumTimeDiff'] = df_slice['TimeDifference'].cumsum()
        df_cum = pd.concat([df_cum, df_slice])

    df_cum = df_cum.reset_index(drop=True)

    return df_cum


def isTimeFormat(time):
    """
    Check if 'time' variable has the format of one
    of the 'time_formats'
    """
    warnings.warn("The isTimeFormat function is deprecated and "
                  "will be removed in version 2.0.0. "
                  "Use the is_time_format function instead.",
                  FutureWarning,
                  stacklevel=8
                  )
    return is_time_format(time)


def is_time_format(time):
    """
    Check if 'time' variable has the format of one
    of the 'time_formats'
    """
    if time is None:
        return False

    for time_format in TIME_FORMATS:
        try:
            datetime.strptime(time, time_format)
            return True
        except ValueError:
            pass

    return False
