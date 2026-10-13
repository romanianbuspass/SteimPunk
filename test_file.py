import obspy
import os

file_path = "miniSEED samples/20250729_230555_XX.<STATION_CODE>.00.HHZ.mseed"
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    print(f"Reading file: {file_path}")
    st = obspy.read(file_path)
    print(f"Found {len(st)} traces.")
    for tr in st:
        print("---")
        print(f"Network: {tr.stats.network}")
        print(f"Station: {tr.stats.station}")
        print(f"Location: {tr.stats.location}")
        print(f"Channel: {tr.stats.channel}")
        print(f"Sample Rate: {tr.stats.sampling_rate} Hz")
        print(f"Start Time: {tr.stats.starttime}")
        print(f"Data Shape: {tr.data.shape}")
