from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical
from textual.reactive import reactive
import threading
from obspy.clients.seedlink.easyseedlink import create_client
from steimpunk.engine import TraceBuffer, render_trace
from steimpunk.config_panel import DigitizerConfigModal

class TraceDisplay(Static):
    def __init__(self, channel_name: str, color_class: str, **kwargs):
        super().__init__(**kwargs)
        self.channel_name = channel_name
        self.add_class(color_class)
        self.buffer = TraceBuffer(max_samples=6000) # 60 secs at 100Hz
        self.charset = "unicode"

    def on_mount(self) -> None:
        self.set_interval(0.1, self.refresh_trace)

    def refresh_trace(self) -> None:
        w, h = self.size.width, self.size.height
        if w > 0 and h > 0:
            data = self.buffer.get_data()
            lines = render_trace(data, w, h - 2, self.charset)  # leaves room for title
            content = f"[b]{self.channel_name}[/b]\n" + "\n".join(lines)
            self.update(content)

class SteimPunkApp(App):
    CSS = """
    TraceDisplay {
        height: 1fr;
    }
    TraceDisplay.vertical {
        border: solid #0EADB2;
        color: #0EADB2;
    }
    TraceDisplay.north_south {
        border: solid #10b981;
        color: #10b981;
    }
    TraceDisplay.east_west {
        border: solid #e2e8f0;
        color: #e2e8f0;
    }
    Header {
        background: #1e293b;
        color: #0EADB2;
    }
    Footer {
        background: #1e293b;
        color: #94a3b8;
    }
    """
    BINDINGS = [
        ("q", "quit",          "Quit"),
        ("s", "toggle_layout", "Toggle Stacked View"),
        ("c", "configure",     "Config"),
    ]

    def __init__(self, mode="single"):
        super().__init__()
        self.mode = mode
        self.displays = {
            "HHZ": TraceDisplay("HHZ", "vertical"),
            "HHN": TraceDisplay("HHN", "north_south"),
            "HHE": TraceDisplay("HHE", "east_west"),
            "HNZ": TraceDisplay("HNZ", "vertical"),
            "HNN": TraceDisplay("HNN", "north_south"),
            "HNE": TraceDisplay("HNE", "east_west"),
        }
        self.client = None
        self.sl_thread = None
        # Current connection params (used for reconnect on config change)
        self._conn = {
            "host":      "<INTERNAL_IP>",
            "port":      "18000",
            "network":   "XX",
            "station":   "<STATION_CODE>",
            "location":  "00",
            "selectors": "00???",
        }

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="display-container"):
            if self.mode == "single":
                yield self.displays["HHZ"]
            else:
                yield self.displays["HHZ"]
                yield self.displays["HHN"]
                yield self.displays["HHE"]
                yield self.displays["HNZ"]
                yield self.displays["HNN"]
                yield self.displays["HNE"]
        yield Footer()

    def action_toggle_layout(self):
        container = self.query_one("#display-container")
        container.remove_children()
        if self.mode == "single":
            self.mode = "stacked"
            container.mount(
                self.displays["HHZ"], self.displays["HHN"], self.displays["HHE"],
                self.displays["HNZ"], self.displays["HNN"], self.displays["HNE"]
            )
        else:
            self.mode = "single"
            container.mount(self.displays["HHZ"])

    def action_configure(self) -> None:
        def handle_new_config(config_data: dict | None) -> None:
            if not config_data:
                return

            # --- Apply charset immediately without reconnect ---
            new_charset = config_data.get("charset", "unicode")
            charset_changed = any(
                d.charset != new_charset for d in self.displays.values()
            )
            for display in self.displays.values():
                display.charset = new_charset

            # --- Check if connection params changed ---
            new_conn = {
                "host":      config_data["host"],
                "port":      config_data["port"],
                "network":   config_data["network"],
                "station":   config_data["station"],
                "location":  config_data["location"],
                "selectors": config_data["selectors"],
            }
            conn_changed = (new_conn != self._conn)
            self._conn = new_conn

            if conn_changed:
                self._restart_seedlink()
                self.notify(
                    f"Reconnecting to {config_data['host']}:{config_data['port']}"
                )
            elif charset_changed:
                self.notify(f"Render style -> {new_charset}")
            else:
                self.notify("Config saved (no changes)")

        self.push_screen(DigitizerConfigModal(), handle_new_config)

    def on_mount(self):
        self.title = "GaiaCode SteimPunk Viewer"
        self.start_seedlink()

    def start_seedlink(self):
        def handle_data(trace):
            ch = trace.stats.channel
            if ch in self.displays:
                self.displays[ch].buffer.append(trace.data)
                
        def run_sl():
            try:
                addr = f"{self._conn['host']}:{self._conn['port']}"
                self.client = create_client(addr, handle_data)
                self.client.select_stream(
                    self._conn['network'],
                    self._conn['station'],
                    self._conn['selectors']
                )
                self.client.run()
            except Exception:
                pass

        self.sl_thread = threading.Thread(target=run_sl, daemon=True)
        self.sl_thread.start()

    def _restart_seedlink(self):
        """Tear down the existing SeedLink connection and start a new one."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None
        # Give the old thread a moment to notice the close before spawning new one
        self.set_timer(0.3, self.start_seedlink)

    def on_unmount(self):
        if self.client:
            self.client.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", choices=["single", "stacked"], default="single")
    args = parser.parse_args()
    app = SteimPunkApp(mode=args.layout)
    app.run()
