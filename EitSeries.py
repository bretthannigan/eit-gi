import EITFrame
import struct
from collections import OrderedDict

__version__ = "0.1"
__author__ = "Brett Hannigan"
__email__ = "hanniganbrett@gmail.com"
__date__ = "2018-04-26"

class EITSeries:

    block_sizes = OrderedDict([('time_stamp',8), ('dummy',4), ('image',4096), 
        ('min_max_flag',4), ('event_marker',4), ('event_text',30), ('timing_error',4),
        ('medibus',208)])
    block_types = OrderedDict([('time_stamp','d'), ('dummy','f'), ('image','f'), 
        ('min_max_flag','i'), ('event_marker','i'), ('event_text','c'), ('timing_error','i'),
        ('medibus','f')])

    def __init__(self, name, file_path):
        self.name = name
        self.eit_data = self.import_file(file_path)
        self.start_time = None
        self.end_time = None

    def add_frame(self, frame):
        self.eit_data.append(frame)

    def import_file(self, file_path):
        with open(file_path, "rb") as fid:
            count = 0
            for chunk in self.__read_frame_chunk(fid):
                count += 1
                self.add_frame(__chunk_to_frame(chunk))
            print('Imported ' repr(count) ' frames.')

    @staticmethod
    def __read_frame_chunk(fid):
        buf = f.read(sum(block_sizes.values()))
        if buf:
            yield buf
        else:
            break

    @staticmethod
    def __chunk_to_frame(chunk):
        return frame