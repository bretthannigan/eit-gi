import EITFrame

__version__ = "0.1"
__author__ = "Brett Hannigan"
__email__ = "hanniganbrett@gmail.com"
__date__ = "2018-04-26"

class EITSeries:

    def __init__(self, name, file_path):
        self.name = name
        self.eit_data = []
        self.import_file(file_path)

    def add_frame(self, frame):
        self.eit_data.append(frame)

    def import_file(self, file_path):
        with open(file_path, "rb") as fid:
            count = 0
            for chunk in self.__read_frame_chunk(fid):
                count += 1
                frame = EITFrame()
                self.add_frame(frame.unpack_frame(chunk))
            print('Imported ' + repr(count) + ' frames.')

    @staticmethod
    def __read_frame_chunk(fid):
        while True:
            buf = f.read(sum(EITSeries.block_sizes.values()))
            if buf:
                yield buf
            else:
                break