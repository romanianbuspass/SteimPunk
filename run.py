from steimpunk.app import SteimPunkApp
import argparse
from rich.console import Console
import time

banner = """
[bold #0EADB2]                ..:::---------::..                [/]
[bold #0EADB2]            ..:-==================-::.            [/]
[bold #0EADB2]         ..-=========---------========-:.         [/]
[bold #0EADB2]       .:-======-:...         ..:--======-.       [/]
[bold #10b981]      :======:..     .........     .:-=====:      [/]
[bold #10b981]    .-=====:.   ..:-==========-::.    .-=-:.      [/]
[bold #10b981]   .=====:.   .-==================-..   .         [/]
[bold #10b981]  .=====.   .-=====-::......::-====-.             [/]
[bold #10b981] .=====.   .=====:.            .::.               [/]
[bold #e2e8f0] :====:   .====-.                                 [/]
[bold #e2e8f0].====-   .====-.                                  [/]
[bold #e2e8f0]:====:   :====.                                   [/]
[bold #e2e8f0]:====:   :====.              ..:::::::::::::::::::[/]
[bold #e2e8f0]:====:   :====.           ..-====================-[/]
[bold #0EADB2].====-   .====-          .::::::::::::::::::-====:[/]
[bold #0EADB2] -====:   :====-.                          .=====. [/]
[bold #0EADB2] .=====.   :=====:.            .::::::.   .-====:  [/]
[bold #10b981]  .=====.   .-=====-:........:-======:   .-====:   [/]
[bold #10b981]   .=====:.   .-==================-:.   .-====:    [/]
[bold #10b981]    .-====-:.   .:--===========-:.    .-=====:     [/]
[bold #10b981]      :=====-:.     ...::::...     .:-=====-.      [/]
[bold #e2e8f0]       .:======--:..          ..::-======-.        [/]
[bold #e2e8f0]         .:-========-----:----========-:.          [/]
[bold #e2e8f0]            .::-==================--:.             [/]
[bold #e2e8f0]                ..::----------::..                 [/]

[bold white]Initializing GaiaCode SteimPunk Viewer...[/]
"""

if __name__ == "__main__":
    console = Console()
    console.print(banner)
    time.sleep(1.5)  # Pause briefly so they can admire it before Textual takes over the screen
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", choices=["single", "stacked"], default="stacked")
    args = parser.parse_args()
    app = SteimPunkApp(mode=args.layout)
    app.run()