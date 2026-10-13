Update to Project SteimPunk (Phases 3 & 4: Engine and UI Integration)

The data connection to the local stream is verified. We will now build the processing engine and the Textual UI using Unicode Braille for high-resolution terminal rendering.

Architecture Requirements:
* Use `numpy` for fast array manipulation.
* Use `Textual` for the terminal UI framework.

Task 1: The Braille Decimation & Scaling Engine (`engine.py`)
1. Create a `TraceBuffer` class that maintains a fixed-length rolling history of incoming samples (e.g., keeping the last 60 seconds of data).
2. Implement an envelope decimation function: `decimate_to_braille(data, terminal_width, terminal_height)`.
   * Horizontal Resolution: Each Braille character is 2 dots wide. Divide the `data` array into chunks equal to `terminal_width * 2`.
   * Vertical Resolution: Each Braille character is 4 dots high. 
   * For each chunk, extract the minimum and maximum values (the envelope) to ensure high-frequency peaks are not lost due to downsampling.
3. Implement dynamic vertical scaling. Calculate the local min/max of the *current visible window* to normalize the trace values. Map these normalized min/max lines to the 4-dot vertical space of the Braille Unicode block (`U+2800` to `U+28FF`). 

Task 2: The Textual UI Application (`app.py`)
1. Create a custom Textual Widget called `TraceDisplay` that takes a `TraceBuffer` and renders the calculated Braille string matrix.
2. Implement two distinct layout modes, toggleable via a CLI argument (`--layout single` or `--layout stacked`) or a keyboard shortcut (e.g., pressing 's' while running):
   * Single Mode: A single `TraceDisplay` widget taking up the entire terminal body, defaulting to the Z (Vertical) channel.
   * Stacked Mode: A vertical grid containing three `TraceDisplay` widgets sharing the screen height equally, mapping to the Z, N, and E channels respectively.
3. Add a `Header` widget displaying the active station name, current sample rate, and current time. 
4. Add a `Footer` widget showing available hotkeys (e.g., `[Q] Quit`, `[S] Toggle Stacked View`).

Task 3: Integration
Wire the live SeedLink stream (<INTERNAL_IP>:18000) to the Textual app. The app must use an asynchronous worker or a background thread to poll the SeedLink client and push new data into the `TraceBuffer` instances, triggering a UI refresh without blocking the main event loop.

Execution:
Write the code for `engine.py` and `app.py`. Provide the exact terminal commands to run the application in both single and stacked modes. Ensure all terminal resize events dynamically trigger a recalculation of the Braille matrix.