# Update to Project SteimPunk (Phase 5: Configuration Panel)

We need to add a graphical configuration panel to the Textual UI so we can dynamically add or edit digitizer connections (specifically targeting GaiaCode Tau digitizers) without hardcoding parameters.

## Architecture Requirements:
* Use `Textual`'s `ModalScreen` to create an overlay that dims the background traces.
* Capture standard seismic parameters: IP/Host, Port, Network, Station, Location, Channels, Selectors, and a toggle for FDSN connections.

## Task 1: Create the Modal Component (`config_panel.py`)
Create a new file in the workspace named `config_panel.py` and implement the following `ModalScreen` class:

```python
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Label, Input, Button, Checkbox

class DigitizerConfigModal(ModalScreen[dict]):
    """A modal screen to configure digitizer connection parameters."""

    CSS = """
    DigitizerConfigModal {
        align: center middle;
        background: $background 50%;
    }

    #dialog-box {
        padding: 1 2;
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
    }

    #panel-title {
        text-align: center;
        width: 100%;
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }

    #form-grid {
        grid-size: 2;
        grid-columns: 1fr 2fr;
        padding: 1 0;
        grid-gutter: 1 2;
    }

    #dialog-buttons {
        align: right middle;
        height: 3;
        margin-top: 1;
    }
    
    Button {
        margin-left: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Configure Digitizer Connection", id="panel-title"),
            Grid(
                Label("IP / Hostname:"), Input(placeholder="<INTERNAL_IP>", id="host"),
                Label("Port:"), Input(value="18000", id="port"),
                Label("Network Code:"), Input(placeholder="GC", id="network"),
                Label("Station Code:"), Input(placeholder="TAU1", id="station"),
                Label("Location Code:"), Input(placeholder="00", id="location"),
                Label("Channel Codes:"), Input(placeholder="HHZ, HHN, HHE", id="channels"),
                Label("Selectors:"), Input(placeholder="???", id="selectors"),
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
                "fdsn": self.query_one("#fdsn_toggle", Checkbox).value,
            }
            self.dismiss(data)
Task 2: Integrate Modal into the Main UI (app.py)
Update the main application to handle the modal invocation and data payload:

Import DigitizerConfigModal from config_panel.py.

Add a BINDINGS entry to map the key c to the action configure (e.g., ("c", "configure", "Config")).

Implement the action_configure method to push the screen and handle the callback dictionary:
def action_configure(self) -> None:
        def handle_new_config(config_data: dict | None) -> None:
            if config_data:
                # TODO: Implement connection reset logic using the new config_data dictionary
                self.notify(f"Updated config for {config_data['host']}:{config_data['port']}")

        self.push_screen(DigitizerConfigModal(), handle_new_config)

Execution:
Apply these changes to the workspace. Run the application to verify that pressing c dims the background, opens the modal, and successfully prints the notification banner with the inputted IP and port upon clicking 'Save'.

