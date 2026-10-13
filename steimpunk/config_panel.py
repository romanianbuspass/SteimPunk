from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Label, Input, Button, Checkbox, Select

# Default values for a standard GaiaCode Tau digitizer
TAU_DEFAULTS = {
    "host":      "<INTERNAL_IP>",
    "port":      "18000",
    "network":   "XX",
    "station":   "",
    "location":  "00",
    "channels":  "*.*.*.H??",
    "selectors": "00???",
    "charset":   "unicode",
    "fdsn":      False,
}

class DigitizerConfigModal(ModalScreen[dict]):
    """A modal screen to configure digitizer connection parameters."""

    BINDINGS = [
        ("r", "reset_defaults", "Reset to Defaults"),
    ]

    CSS = """
    DigitizerConfigModal {
        align: center middle;
        background: #0f172a 50%;
    }

    #dialog-box {
        padding: 1 2;
        width: 65;
        height: auto;
        border: thick #334155;
        background: #1e293b;
    }

    #ascii-logo {
        text-align: center;
        width: 100%;
        color: #0EADB2;
        padding-bottom: 1;
    }

    #panel-title {
        text-align: center;
        width: 100%;
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid #0EADB2;
        color: #0EADB2;
    }

    #form-grid {
        grid-size: 2;
        grid-columns: 1fr 2fr;
        padding: 1 0;
        grid-gutter: 1 2;
        color: #e2e8f0;
    }

    Input {
        background: #020a14;
        border: solid #334155;
        color: #4ade80;
    }
    
    Input:focus {
        border: solid #0EADB2;
    }

    Select {
        background: #020a14;
        border: solid #334155;
        color: #4ade80;
    }

    Select:focus {
        border: solid #0EADB2;
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
        logo = '''                ..:::---------::..                
            ..:-==================-::.            
         ..-=========---------========-:.         
       .:-======-:...         ..:--======-.       
      :======:..     .........     .:-=====:      
    .-=====:.   ..:-==========-::.    .-=-:.      
   .=====:.   .-==================-..   .         
  .=====.   .-=====-::......::-====-.             
 .=====.   .=====:.            .::.               
 :====:   .====-.                                 
.====-   .====-.                                  
:====:   :====.                                   
:====:   :====.              ..:::::::::::::::::::\
:====:   :====.           ..-====================-
.====-   .====-          .::::::::::::::::::-====:
 -====:   :====-.                          .=====.
 .=====.   :=====:.            .::::::.   .-====: 
  .=====.   .-=====-:........:-======:   .-====:  
   .=====:.   .-==================-:.   .-====:   
    .-====-:.   .:--===========-:.    .-=====:    
      :=====-:.     ...::::...     .:-=====-.     
       .:======--:..          ..::-======-.       
         .:-========-----:----========-:.         
            .::-==================--:.            
                ..::----------::..'''

        yield Vertical(
            Label(logo, id="ascii-logo"),
            Label("Configure Digitizer Connection", id="panel-title"),
            Grid(
                Label("IP / Hostname:"), Input(value=TAU_DEFAULTS["host"], id="host"),
                Label("Port:"), Input(value=TAU_DEFAULTS["port"], id="port"),
                Label("Network Code:"), Input(value=TAU_DEFAULTS["network"], id="network"),
                Label("Station Code:"), Input(placeholder="e.g., TAU1", id="station"),
                Label("Location Code:"), Input(value=TAU_DEFAULTS["location"], id="location"),
                Label("Channel Codes:"), Input(value=TAU_DEFAULTS["channels"], id="channels"),
                Label("Selectors:"), Input(value=TAU_DEFAULTS["selectors"], id="selectors"),
                Label("Render Style:"), Select(
                    [
                        ("Unicode (Braille)", "unicode"),
                        ("ASCII",             "ascii"),
                        ("ANSI Blocks",       "ansi"),
                        ("ISO-8859-1",        "iso"),
                    ],
                    id="charset",
                    value=TAU_DEFAULTS["charset"],
                ),
                Label("FDSN Connection:"), Checkbox("Enable FDSN Web Services", id="fdsn_toggle"),
                id="form-grid"
            ),
            Horizontal(
                Button("Save",  variant="success", id="save"),
                Button("Reset", variant="warning",  id="reset"),
                Button("Cancel", variant="error",   id="cancel"),
                id="dialog-buttons"
            ),
            id="dialog-box"
        )

    def on_mount(self) -> None:
        """Push defaults after mount so widgets are guaranteed to exist on Windows."""
        self._apply_defaults()

    def _apply_defaults(self) -> None:
        """Fill every field with the Tau default values."""
        self.query_one("#host",        Input).value    = TAU_DEFAULTS["host"]
        self.query_one("#port",        Input).value    = TAU_DEFAULTS["port"]
        self.query_one("#network",     Input).value    = TAU_DEFAULTS["network"]
        self.query_one("#station",     Input).value    = TAU_DEFAULTS["station"]
        self.query_one("#location",    Input).value    = TAU_DEFAULTS["location"]
        self.query_one("#channels",    Input).value    = TAU_DEFAULTS["channels"]
        self.query_one("#selectors",   Input).value    = TAU_DEFAULTS["selectors"]
        self.query_one("#charset",     Select).value   = TAU_DEFAULTS["charset"]
        self.query_one("#fdsn_toggle", Checkbox).value = TAU_DEFAULTS["fdsn"]

    def action_reset_defaults(self) -> None:
        """Hotkey 'R': reset the form to Tau defaults."""
        self._apply_defaults()
        self.notify("Reset to Tau defaults", severity="information")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "reset":
            self._apply_defaults()
            self.notify("Reset to Tau defaults", severity="information")
        elif event.button.id == "save":
            data = {
                "host":      self.query_one("#host",        Input).value,
                "port":      self.query_one("#port",        Input).value,
                "network":   self.query_one("#network",     Input).value,
                "station":   self.query_one("#station",     Input).value,
                "location":  self.query_one("#location",    Input).value,
                "channels":  self.query_one("#channels",    Input).value,
                "selectors": self.query_one("#selectors",   Input).value,
                "charset":   self.query_one("#charset",     Select).value,
                "fdsn":      self.query_one("#fdsn_toggle", Checkbox).value,
            }
            self.dismiss(data)
