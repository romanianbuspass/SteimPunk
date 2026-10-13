# Update to Project SteimPunk (Phase 6: Smart Defaults & Character Sets)

We need to update the `DigitizerConfigModal` to optimize for a standard GaiaCode Tau digitizer setup while remaining flexible. We will populate the input fields with specific default values so the user can connect immediately, but still allow them to manually override the parameters. We are also adding a feature to toggle the terminal rendering character set dynamically.

## Task 1: Update the Configuration Modal (`config_panel.py`)
Modify the `DigitizerConfigModal` to include all connection parameters, but pre-fill the `value` attributes with our specific Tau defaults. Add a new `Select` widget for the Character Set.

Update the `compose` and `on_button_pressed` methods:

```python
from textual.widgets import Select

# ... (keep existing CSS and class definition) ...

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Configure Digitizer Connection", id="panel-title"),
            Grid(
                Label("IP / Hostname:"), Input(value="<INTERNAL_IP>", id="host"),
                Label("Port:"), Input(value="18000", id="port"),
                Label("Network Code:"), Input(value="XX", id="network"),
                Label("Station Code:"), Input(placeholder="e.g., TAU1", id="station"),
                Label("Location Code:"), Input(value="00", id="location"),
                Label("Channel Codes:"), Input(value="*.*.*.H??", id="channels"),
                Label("Selectors:"), Input(value="00???", id="selectors"),
                Label("Render Style:"), Select(
                    [
                        ("Unicode (Braille)", "unicode"), 
                        ("ASCII", "ascii"), 
                        ("ANSI Blocks", "ansi"), 
                        ("ISO-8859-1", "iso" )
                    ], 
                    id="charset", 
                    value="unicode"
                ),
                Label("FDSN Connection:"), Checkbox("Enable FDSN Web Services", id="fdsn_toggle"),
                id="form-grid"
            ),
            Horizontal(
                Button("Save", variant="success", id="save"),
                Button("Cancel", variant="error", id="cancel"),
                id="dialog-buttons"
            ),
            id="dialog-box"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "save":
            data = {
                "host": self.query_one("#host", Input).value,
                "port": self.query_one("#port", Input).value,
                "network": self.query_one("#network", Input).value,
                "station": self.query_one("#station", Input).value,
                "location": self.query_one("#location", Input).value,
                "channels": self.query_one("#channels", Input).value,
                "selectors": self.query_one("#selectors", Input).value,
                "charset": self.query_one("#charset", Select).value,
                "fdsn": self.query_one("#fdsn_toggle", Checkbox).value,
            }
            self.dismiss(data)

Task 2: Update the Engine Rendering Logic (engine.py)
Update the TraceBuffer and the rendering logic to accept the charset parameter passed from the UI.

Create a character mapping dictionary in engine.py. Depending on the charset string ("unicode", "ascii", "ansi", "iso"), the decimation function should map the normalized waveform amplitudes to different character palettes.

unicode: Use the existing Braille block logic (U+2800 to U+28FF).

ascii: Map normalized vertical heights to standard characters (e.g., _, ., -, ~, *, #).

ansi: Map to block elements (e.g.,  , ?, ?, _, ?, ?, ?, ¦).

iso: Utilize extended ISO-8859-1 drawing characters if applicable, or fallback to an alternate ASCII representation.

Ensure the TraceDisplay widget in app.py re-renders immediately when a new character set is selected and saved via the config panel.

Execution:
Implement these UI defaults and rendering updates. Verify that the form opens with the Tau parameters pre-filled, and that changing the dropdown from "Unicode" to "ASCII" dynamically updates the visual trace without dropping the connection.


***

This way, it acts exactly like a specialized GaiaCode tool out of the box, but won't artificially lock you out of your own configuration options. 

we should  add a hotkey command (like pressing 'R') to quickly reset the form back to those default values just in case a user scrambles them while testing.