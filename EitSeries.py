from EITFrame import EITFrame, BreathPhaseMarker, np
import cv2

__version__ = "0.1"
__author__ = "Brett Hannigan"
__email__ = "hanniganbrett@gmail.com"
__date__ = "2018-04-26"

class EITSeries:

    def __init__(self, name, file_path):
        self.name = name
        self.eit_data = []
        self.mask = np.ones((32, 32), dtype=bool)
        n_frame = self.import_file(file_path)
        print('Imported ' + repr(n_frame) + ' frames.')

    def add_frame(self, frame):
        self.eit_data.append(frame)

    def import_file(self, file_path):
        with open(file_path, "rb") as fid:
            count = 0
            for chunk in self.__read_frame_chunk(fid):
                count += 1
                frame = EITFrame()
                frame.unpack_frame(chunk)
                self.add_frame(frame)
            return count

    def flagged_data(self, flag):
        return list([fr for fr in self.eit_data if fr.min_max_flag==flag]) 

    def tidal_data(self):
        end_insp_data = self.flagged_data(BreathPhaseMarker.END_INSP)
        end_exp_data = self.flagged_data(BreathPhaseMarker.END_EXP)
        # Remove leading END_EXP that are without a preceeding END_INSP.
        while end_exp_data[0].time_stamp<end_insp_data[0].time_stamp:
            end_exp_data.pop(0)
        # Remove trailing END_INSP that are without a following END_EXP.
        while end_insp_data[-1].time_stamp>end_exp_data[-1].time_stamp:
            end_insp_data.pop()
        # Assume len(end_insp_data)==len(end_insp_data)
        return list(map(EITFrame.__sub__, end_insp_data, end_exp_data))  # Element-wise subtraction.

    @staticmethod
    def __read_frame_chunk(fid):
        """
        Generator to produce binary chunks by frame size.

        :param fid file: file handle.
        """
        while True:
            buf = fid.read(sum(EITFrame.block_sizes.values()))
            if buf:
                yield buf
            else:
                break