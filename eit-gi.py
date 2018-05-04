from EITSeries import EITSeries, BreathPhaseMarker

if __name__ == "__main__":
    series = EITSeries('test', 'C:\\Users\\bhannigan\\Documents\\MATLAB\\ID_SC_37_001_01.bin')
    test = series.tidal_data()
    test[0].image_median(series.mask)
    gi = test[0].global_inhomogeneity(series.mask)
    print(gi)