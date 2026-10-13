from obspy.clients.seedlink.slclient import SLClient
import time

slClient = SLClient()
slClient.sladdr = "<INTERNAL_IP>:18000"
slClient.multiselect = False
slClient.begin_time = None
slClient.end_time = None

print("Connecting to SeedLink at <INTERNAL_IP>:18000...")

try:
    info = slClient.get_info('STREAMS')
    print("SeedLink INFO STREAMS:")
    print(info)
except Exception as e:
    print("Failed to get info:", e)
