import numpy as np

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

    def __init__(self):
        self.time_stamp = 0.0
        self.dummy = 0.0
        self.image = np.zeros((32, 32), np.float32)
        self.min_max_flag = 0
        self.event_marker = 0
        self.event_text = ""
        self.timing_error = 0
        self.medibus = []