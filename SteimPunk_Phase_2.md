Update to Project SteimPunk (Phase 2 Integration):

We have actual test data and a live server available. Do not generate synthetic data. 

Task 1: Static File Parsing
There is a local directory named "miniSEED samples". 
Write a short diagnostic script (`test_file.py`) using ObsPy to load a sample file from this directory. Have the script read the file, handle the Steim 2 decompression automatically via ObsPy, and print out the stream metadata (Network, Station, Channel, Sample Rate) and the array shape of the data payload.

Task 2: Live SeedLink Connection
The GaiaCode Tau digitizer is pushing a live stream via SeedLink on the local network.
Write a second diagnostic script (`test_stream.py`) using `obspy.clients.seedlink`. 
* Target: <INTERNAL_IP>
* Port: 18000
Configure the client to connect, subscribe to all available streams (using wildcards if necessary), and pull live data for exactly 10 seconds. Print the header information of the incoming packets to stdout, then gracefully close the connection.

Execute Task 1 and Task 2 to verify our data pipelines before we begin building the Textual UI and decimation engine.