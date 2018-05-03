import numpy as np
from collections import OrderedDict
import struct

__version__ = "0.1"
__author__ = "Brett Hannigan"
__email__ = "hanniganbrett@gmail.com"
__date__ = "2018-04-26"

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
            self.__min_max_flag = 0
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

    @property
    def time_stamp(self):
        return self.__time_stamp

    @time_stamp.setter
    def time_stamp(self, value):
        self.__time_stamp = EITFrame.__tuple_to_scalar(value)

    @property
    def dummy(self):
        return self.__dummy

    @dummy.setter
    def dummy(self, value):
        self.__dummy = EITFrame.__tuple_to_scalar(value)

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value):
        if isinstance(value, tuple):
            self.__image = np.asarray(value, dtype=np.float32).reshape((32, 32))

    @property
    def min_max_flag(self):
        return self.__min_max_flag

    @min_max_flag.setter
    def min_max_flag(self, value):
        self.__min_max_flag = EITFrame.__tuple_to_scalar(value)

    @property
    def event_marker(self):
        return self.__event_marker

    @event_marker.setter
    def event_marker(self, value):
        self.__event_marker = EITFrame.__tuple_to_scalar(value)

    @property
    def event_text(self):
        return self.__event_text

    @event_text.setter
    def event_text(self, value):
        self.__event_text = EITFrame.__tuple_to_scalar(value).decode("utf-8")

    @property
    def timing_error(self):
        return self.__timing_error

    @timing_error.setter
    def timing_error(self, value):
        self.__timing_error = EITFrame.__tuple_to_scalar(value)

    def unpack_frame(self, frame_bytes):
        byte_index = 0
        for i in iter(EITFrame.block_sizes.keys()):
            setattr(self, i, struct.unpack(EITFrame.block_types[i], frame_bytes[byte_index:(byte_index+EITFrame.block_sizes[i])]))
            byte_index = byte_index + EITFrame.block_sizes[i]

    @staticmethod
    def __tuple_to_scalar(tuple_value):
        if isinstance(tuple_value, tuple) and len(tuple_value)==1:
            return tuple_value[0]
        else:
            return tuple_value