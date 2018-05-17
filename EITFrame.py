import numpy as np
import matplotlib.pyplot as plt
import struct
import datetime
from collections import OrderedDict
from enum import Enum

__version__ = "0.1"
__author__ = "Brett Hannigan"
__email__ = "hanniganbrett@gmail.com"
__date__ = "2018-04-26"

class BreathPhaseMarker(Enum):
    END_EXP = -1
    NONE = 0
    END_INSP = 1
    TIDAL = 2

class EITFrame:
    """A frame of electrical impedance tomography data.

    See Appendix Ib, "Instruction Manual Drager EIT Data Analysis Tool" (2011) for details.

    Attributes:
        time_stamp: A double to indicate the time the frame was acquired.
        dummy: A float indicating an analog value.
        image: A 32*32 float numpy array containing the image data in row major form, beginning from the upper-left corner.
        min_max_flag: An integer indicating the minimum (-1), maximum (+1), or none (0) of the series.
        event_marker: A non-negative integer indicating an event.
        event_text: A string describing the event.
        timing_error: A non-negative integer indicating a timing error has occurred.
        medibus: A float array of MEDIBUS values.
    """

    block_sizes = OrderedDict([('time_stamp',8), ('dummy',4), ('image',4096), 
        ('min_max_flag',4), ('event_marker',4), ('event_text',30), ('timing_error',4),
        ('medibus',208)])

    block_types = OrderedDict([('time_stamp','d'), ('dummy','f'), ('image','1024f'), 
        ('min_max_flag','i'), ('event_marker','i'), ('event_text','30s'), ('timing_error','i'),
        ('medibus','52f')])

    def __init__(self, time_stamp=None, dummy=None, image=None, min_max_flag=None, 
        event_marker=None, event_text=None, timing_error=None, medibus=None):
        self.__time_stamp = time_stamp
        self.__dummy = dummy
        if image is None:
            self.__image = np.zeros((32, 32), np.float32)
        else:
            self.__image = image
        if min_max_flag is None:
            self.__min_max_flag = BreathPhaseMarker.NONE
        else:
            self.__min_max_flag = min_max_flag
        if event_marker is None:
            self.__event_marker = 0
        else:
            self.__event_marker = event_marker
        if event_text is None:
            self.__event_text = ""
        else:
            self.__event_text = event_text
        if timing_error is None:
            self.__timing_error = 0
        else:
            self.__timing_error = timing_error
        if medibus is None:
            self.__medibus = []
        else:
            self.__medibus = medibus

    def __sub__(self, other):
        """
        Overloads the subtraction operator (-) for EITFrame objects.

        :param other EITFrame: subtrahend value.
        :return: self - other.
        :rtype: EITFrame
        """
        difference = EITFrame(other.__time_stamp,
            self.__dummy - other.__dummy,
            np.subtract(self.__image, other.__image),
            BreathPhaseMarker.TIDAL,
            None,
            None,
            self.__timing_error + other.__timing_error,
            [])
        return difference

    @property
    def time_stamp(self):
        return self.__time_stamp

    @time_stamp.setter
    def time_stamp(self, value):
        if isinstance(value, tuple):
            self.__time_stamp = EITFrame.__float_to_time(EITFrame.__tuple_to_scalar(value))
        elif isinstance(value, datetime.time):
            self.__time_stamp = value

    @property
    def dummy(self):
        return self.__dummy

    @dummy.setter
    def dummy(self, value):
        if isinstance(value, tuple):
            self.__dummy = EITFrame.__tuple_to_scalar(value)
        elif isinstance(value, float):
            self.__dummy = value

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value):
        if isinstance(value, tuple):
            self.__image = np.asarray(value, dtype=np.float32).reshape((32, 32))
        elif isinstance(value, np.ndarray):
            self.__image = value

    @property
    def min_max_flag(self):
        return self.__min_max_flag

    @min_max_flag.setter
    def min_max_flag(self, value):
        if isinstance(value, tuple):
            self.__min_max_flag = BreathPhaseMarker(EITFrame.__tuple_to_scalar(value))
        elif isinstance(value, BreathPhaseMarker):
            self.__min_max_flag = value
        else:
            self.__min_max_flag = BreathPhaseMarker(value)

    @property
    def event_marker(self):
        return self.__event_marker

    @event_marker.setter
    def event_marker(self, value):
        if isinstance(value, tuple):
            self.__event_marker = EITFrame.__tuple_to_scalar(value)
        elif isinstance(value, int):
            self.__event_marker = value
        else:
            self.__event_marker = int(value)

    @property
    def event_text(self):
        return self.__event_text

    @event_text.setter
    def event_text(self, value):
        if isinstance(value, tuple):
            self.__event_text = EITFrame.__tuple_to_scalar(value).decode("utf-8")
        elif isinstance(value, str):
            self.__event_text = value

    @property
    def timing_error(self):
        return self.__timing_error

    @timing_error.setter
    def timing_error(self, value):
        if isinstance(value, tuple):
            self.__timing_error = EITFrame.__tuple_to_scalar(value)
        elif isinstance(value, int):
            self.__timing_error = value
        else:
            self.__timing_error = int(value)

    def unpack_frame(self, frame_bytes):
        """
        Unpacks a binary frame of data into an EITFrame object.

        :param frame_bytes bytes: a frame of data as described in Appendix Ib of "Instruction Manual: Drager EIT Data Analysis Tool".
        """
        byte_index = 0
        for i in iter(EITFrame.block_sizes.keys()):
            setattr(self, i, struct.unpack(EITFrame.block_types[i], frame_bytes[byte_index:(byte_index+EITFrame.block_sizes[i])]))
            byte_index = byte_index + EITFrame.block_sizes[i]

    def image_median(self, mask=np.ones((32, 32), dtype=bool)):
        """
        Calculates the median pixel value of the impedance image.

        :param mask ndarray: (optional) array to mask off part of the image where mask is False.
        :return: median intensity of pixels where mask is True.
        :rtype: float
        """
        return np.median(self.__image[mask])

    def global_inhomogeneity(self, mask=np.ones((32, 32), dtype=bool)):
        """
        Calculates the global inhomogeneity (GI) index.

        :param mask ndarray: (optional) array to mask off part of the image where mask is False.
        :return: GI index, as defined in [Zhao2009] (https://doi.org/10.1007/s00134-009-1589-y).
        :rtype: float
        """
        return np.sum(np.absolute(self.__image[mask] - self.image_median(mask)))/np.sum(self.__image[mask])

    def show_image(self, mask=np.ones((32, 32), dtype=bool)):
        """
        Presents the impedance image as a matplotlib plot.

        :param mask ndarray: (optional) array to mask off part of the image where mask is False.
        """
        image = np.copy(self.__image)
        image[~mask] = 0
        plt.imshow(image, aspect="auto")
        plt.show()

    def save_image(self, mask=np.ones((32, 32), dtype=bool)):
        image = np.copy(self.__image)
        image[~mask] = 0
        plt.imsave('image.png', image)

    @staticmethod
    def __tuple_to_scalar(tuple_value):
        """
        Helper method for Tuple to scalar conversion.

        :param tuple_value tuple: object to be converted, the output of a struct.unpack call.
        :return: the first element of the tuple, if it has length 1. Otherwise, the tuple is returned unchanged.
        """
        if isinstance(tuple_value, tuple) and len(tuple_value)==1:
            return tuple_value[0]
        else:
            return tuple_value

    @staticmethod
    def __float_to_time(float_value):
        """
        Helper method for Excel-style float to time object conversion.

        :param float_value float: fractional day to be converted.
        :return: converted time object with millisecond precision.
        :rtype: datetime.time
        """
        time_ms = int(float_value*24*60*60*1e3)
        return (datetime.datetime.min + datetime.timedelta(milliseconds=time_ms)).time()

    @staticmethod
    def __time_to_float(time_value):
        """
        Helper method for time object to Excel-style float conversion.

        :param time_value float: time object to be converted.
        :return: fractional day with millisecond precision.
        :rtype: float
        """
        return time_value.hour/24 + time_value.minute/(24*60) + time_value.second/(24*60*60) + round(time_value.microsecond, 3)/(24*60*60*1e6)