from EITSeries import EITSeries, BreathPhaseMarker, cv2
import csv

if __name__ == "__main__":
    name = 'P03_02_001_01'
    series = EITSeries(name, '/Volumes/brett/EIT Data/' + name + '.bin')
    series.mask = cv2.imread(series.name + '_TH70.png', 0) == 255
    tidal_data = series.tidal_data()
    with open(name + '.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, dialect='excel')
        csv_writer.writerow(["File name:", series.name])
        csv_writer.writerow(["Time stamp", "GI index"])
        csv_writer.writerow
        for fr in tidal_data:
            csv_writer.writerow([fr.time_stamp.strftime("%H:%M:%S.%f"), "{:.6f}".format(fr.global_inhomogeneity(series.mask))])
    csv_file.close()