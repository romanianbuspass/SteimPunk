# SteimPunk

A terminal-based, real-time miniSEED seismic trace viewer. SteimPunk connects to a live
SeedLink stream (e.g. from a GaiaCode Tau digitizer), unpacks Steim-compressed waveform
data using ObsPy, and renders scrolling seismic traces directly in the terminal using
Unicode Braille, ANSI block, ISO-8859-1 shaded, or plain ASCII characters — no GUI or
plotting window required.

## Features

- Live waveform rendering in the terminal via a Textual TUI
- Four selectable rendering charsets:
  - **Unicode Braille** (2x4 dot matrix — highest resolution)
  - **ANSI half-blocks** (▄▀█ — smooth 2x vertical resolution)
  - **ISO-8859-1** depth-shaded envelope (░▒▓█ gradient)
  - **ASCII** (`#` fill — universally compatible)
- Min/max envelope decimation: high-frequency peaks are preserved when downsampling
  high-rate data to finite terminal columns
- Auto-scaling amplitude window (moving min/max) so traces always fit the terminal height
- Single-channel (full-screen) and stacked multi-channel layouts, switchable at runtime
- Modal configuration panel for digitizer connection parameters (host, port, NSLC,
  selectors, render style) with hot-reconnect on change
- Thread-safe rolling trace buffer decoupling the SeedLink client from the UI loop

## Technology Stack

- **Python 3.10+**
- **[ObsPy](https://obspy.org/)** — miniSEED / Steim-1 / Steim-2 decoding and the
  SeedLink client (`obspy.clients.seedlink`)
- **[Textual](https://textual.textualize.io/)** — terminal UI framework
- **[Rich](https://rich.readthedocs.io/)** — startup banner / markup
- **NumPy** — trace buffering and decimation math

## Hardware Dependencies

Designed for digitizers that serve miniSEED over a SeedLink server (default port
18000), developed and tested against a **GaiaCode Tau** digitizer on a local network.
Any SeedLink source (including public servers) should work — host, network, station,
location, and channel selectors are all configurable in the app's config panel (`c` key).

## Setup & Installation

```bash
git clone <repo-url>
cd SteimPunk
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Stacked mode (Z, N, E channels sharing the screen)
python run.py --layout stacked

# Single mode (vertical Z-channel fills the terminal)
python run.py --layout single

# Equivalent module entry point
python -m steimpunk.app --layout single
```

### Hotkeys (inside the app)

| Key | Action |
|-----|--------|
| `s` | Toggle single / stacked layout |
| `c` | Open the digitizer configuration panel |
| `r` | (in config panel) Reset fields to Tau defaults |
| `q` | Quit |

### Test scripts

- `test_stream_info.py` — query a SeedLink server's `INFO STREAMS` (available stations/channels)
- `test_stream.py` — connect to a SeedLink stream and print incoming trace metadata for 10 s
- `test_file.py` — read a local miniSEED file and dump its trace headers

> Note: sample miniSEED data files are **not** included in this repository
> (see `.gitignore`). Point `test_file.py` at your own miniSEED file.

## Data Formats & Protocols

- **miniSEED** — Standard for the Exchange of Earthquake Data (SEED) waveform records,
  read via ObsPy
- **Steim-1 / Steim-2 compression** — the data compression inside miniSEED records
  (decoded transparently by ObsPy)
- **SeedLink** — real-time data transport protocol over TCP (default port 18000),
  using NSLC stream selection (e.g. network `XX`, location `00`, selectors `00???`
  or channel wildcards `*.*.*.H??`)
- Channel naming follows SEED convention: `HHZ`/`HHN`/`HHE` (100 Hz broadband)
  and `HNZ`/`HNN`/`HNE` are pre-wired as display channels

## Project Layout

```
steimpunk/
  __init__.py
  app.py           # Textual TUI: layouts, hotkeys, SeedLink wiring
  config_panel.py  # Modal digitizer configuration screen
  engine.py        # TraceBuffer + Braille/ANSI/ISO/ASCII renderers
  stream.py        # (stub) stream client helpers
  cli.py           # (stub) CLI entry point
run.py             # Launcher with banner and --layout argument
test_*.py          # SeedLink / miniSEED smoke tests
SteimPunk_Phase_*.md, Phase_6.md  # Original build-phase design notes
development_notes.md              # Dev handover notes
```

## Repository Notes

This repository contains code and documentation only. Internal host addresses,
station codes, and local paths in the source have been replaced with placeholders
(`<INTERNAL_IP>`, `<STATION_CODE>`, etc.) — substitute your own values before
connecting to a live digitizer.
