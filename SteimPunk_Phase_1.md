Project Name: SteimPunk
Workspace Directory: <LOCAL_WORKSPACE_PATH>
Language: Python 3.10+
Primary Libraries: obspy, textual (or rich), sounddevice (optional for future audio easter eggs)

Objective:
Create a terminal-based, real-time miniSEED trace viewer ("SteimPunk") that connects to a local stream/server, unpacks Steim 2 compressed data using ObsPy, and renders scrolling seismic traces directly in the terminal using ASCII or Unicode Braille characters.

Phase 1: Environment & Dependency Setup
1. Initialize a clean virtual environment or poetry environment in the workspace directory.
2. Install dependencies: `obspy` (for miniSEED/Steim handling) and `textual` (for the TUI framework).
3. Create a basic directory structure:
   +-- README.md
   +-- requirements.txt
   +-- steimpunk/
   ¦   +-- __init__.py
   ¦   +-- cli.py         # Entry point & CLI argument parsing
   ¦   +-- stream.py      # Client connections (SeedLink/Local stub)
   ¦   +-- engine.py      # Decimation and ASCII/Braille rendering logic

Phase 2: Mock Stream Client & Header Parsing
1. Create a stream client stub in `stream.py` that can read a local miniSEED file or simulate an incoming stream from a GaiaCode Tau digitizer.
2. Use ObsPy to extract stream metadata: Network, Station, Location, Channel (NSLC), sample rate, and start time.
3. Handle wildcard filtering arguments (e.g., allow the user to pass "all channels" via '*' or specify 'HHZ').

Phase 3: The Data Rolling Buffer & Decimation
1. Implement a thread-safe rolling buffer in `engine.py` to store incoming time-series samples.
2. Build a decimation function: Terminal widths are finite (e.g., 100 columns). If a data packet contains 200 samples per second, decimate the data into min/max pairs (binned envelopes) matching the layout columns so that high-frequency peaks are not lost due to downsampling.
3. Implement an auto-scaling algorithm that computes the moving min/max amplitude window to dynamically fit the waveform to the terminal's row height without clipping or disappearing.

Phase 4: TUI Implementation (Textual)
1. Build a basic interface with a top banner showing the active station metadata, sample rate, and current time.
2. Render the rolling trace in the center body using standard terminal text lines. Ensure it catches terminal resize events (SIGWINCH) to recalculate column and row allocations dynamically.
3. Ensure graceful exit (`Ctrl+C`) resets terminal settings and closes all active streams without dumping a traceback.

Execution Step 1:
Begin by creating the project directory layout and verifying the environment setup. Write a simple script to read a sample miniSEED file using ObsPy and dump its header details to stdout to confirm the parsing foundation is solid. Do not build the full UI yet.