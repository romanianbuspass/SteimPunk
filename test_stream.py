from obspy.clients.seedlink.easyseedlink import create_client
import time
import threading

def handle_data(trace):
    print("--- Received Trace ---")
    print(f"Network: {trace.stats.network}")
    print(f"Station: {trace.stats.station}")
    print(f"Location: {trace.stats.location}")
    print(f"Channel: {trace.stats.channel}")
    print(f"Sample Rate: {trace.stats.sampling_rate} Hz")
    print(f"Data Shape: {trace.data.shape}")

print("Connecting to SeedLink at <INTERNAL_IP>:18000...")
try:
    client = create_client('<INTERNAL_IP>:18000', handle_data)
    
    # Using the suggested selector '00???' for location 00 and all channels
    client.select_stream('XX', '<STATION_CODE>', '00???') 
    
    # Run the client in a background thread so we can stop it after 10 seconds
    def run_client():
        try:
            client.run()
        except Exception as e:
            print(f"Client stopped: {e}")

    t = threading.Thread(target=run_client)
    t.daemon = True
    t.start()

    print("Listening for 10 seconds...")
    time.sleep(10)
    print("10 seconds elapsed. Closing connection...")
    client.close()
    print("Done.")
except Exception as e:
    print(f"Failed to connect or stream: {e}")
