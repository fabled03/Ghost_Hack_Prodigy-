from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

ASCII_TITLE = r"""
  ____ _               _   _   _            _    
 / ___| |__   ___  ___| |_| | | | __ _  ___| | __
| |  _| '_ \ / _ \/ __| __| |_| |/ _` |/ __| |/ /
| |_| | | | | (_) \__ \ |_|  _  | (_| | (__|   < 
 \____|_| |_|\___/|___/\__|_| |_|\__,_|\___|_|\_\
 
 :: PRODIGY OS v0.6.7 :: UNAUTHORIZED ACCESS FATAL ::
"""

class Status(Static):
    """The status panel."""
    pass

class VirusGame(App):
    """Terminal-based hacking containment game."""
    
    CSS = """
    Screen { layout: vertical; }
    Horizontal { height: 1fr; }
    #left-stage {
        width: 50%;
        height: 100%;
        border: solid lime;
        background: #050505;
    }
    #right-split {
        width: 50%;
        height: 100%;
    }
    #right-top {
        height: 50%;
        border: solid yellow;
        background: #050505;
    }
    #right-bottom {
        height: 50%;
        border: solid dodgerblue;
        background: #000000;
    }
    /* Updated Stage to target RichLog */
    RichLog {
        padding: 1;
        color: lime;
        text-style: bold;
    }
    Status {
        padding: 1;
        content-align: left top;
        color: yellow;
    }
    Input {
        border: none;
        background: #000000;
        color: cyan;
    }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    status_text = reactive("SYSTEM OFFLINE")

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Container(id="left-stage"):
                # REPLACED Static with RichLog
                yield RichLog(id="stage_view", markup=False)
            with Vertical(id="right-split"):
                with Container(id="right-top"):
                    yield Status(self.status_text, id="status_view")
                with Container(id="right-bottom"):
                    yield Input(placeholder="> root@system:~# ", id="command_input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        
        # Save a reference to the log so we can write to it easily
        self.stage = self.query_one("#stage_view", RichLog)
        
        self.command_map = {
            "clear": self.cmd_clear,
            "scan": self.cmd_scan,
            "help": self.cmd_help,
        }

        self.tutorial_step = 0
        
        self.stage.write("INITIALIZING BIOS...")
        self.set_timer(1.0, self.boot_step_1)
        self.set_timer(2.5, self.boot_step_2)
        self.set_timer(4.5, self.boot_step_3)

    # ==========================================
    # BOOT SEQUENCE LOGIC
    # ==========================================
    def boot_step_1(self):
        self.stage.write("\nLOADING KERNEL... [OK]\nMOUNTING DRIVES... [OK]")
        self.status_text = "BOOTING..."
        self.query_one("#status_view", Status).update(self.status_text)

    def boot_step_2(self):
        self.stage.clear()
        self.stage.write(ASCII_TITLE)
        self.stage.write("\nCONNECTION ESTABLISHED.")
        self.status_text = "SYSTEM STATUS:\n\nCPU: 4%\nRAM: 1.2GB/16GB\nTHREAT LEVEL: UNKNOWN"
        self.query_one("#status_view", Status).update(self.status_text)

    def boot_step_3(self):
        self.stage.write("\n[SYSTEM AI]: Greetings, Operator.")
        self.stage.write("[SYSTEM AI]: We have a containment breach.")
        self.stage.write("[SYSTEM AI]: Type 'help' and press Enter to view your modules.")
        self.tutorial_step = 1 

    # ==========================================
    # INPUT PARSING
    # ==========================================
    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_input = event.value.strip().lower()
        self.query_one(Input).value = "" 
        
        if not raw_input: return

        # Echo the player's command to the screen
        self.stage.write(f"\n> root@system:~# {raw_input}")

        base_command = raw_input.split()[0]

        if base_command in self.command_map:
            self.command_map[base_command]() 
        else:
            self.cmd_unknown(base_command)
            
    # ==========================================
    # COMMANDS
    # ==========================================
    def cmd_clear(self) -> None:
        self.stage.clear()

    def cmd_scan(self) -> None:
        self.stage.write("> Scanning memory sectors... [ OK ]")
        
        # Fixed Tutorial Logic: Proceeds immediately if they are on step 2
        if self.tutorial_step == 2:
            self.stage.write("\n[SYSTEM AI]: Good. Data is collected.")
            self.stage.write("[SYSTEM AI]: Get ready!!!")
            self.tutorial_step = 3 
            self.set_timer(2.0, self.start_main_game)

    def cmd_help(self) -> None:
        available_commands = ", ".join(self.command_map.keys())
        self.stage.write(f"> Available modules: [ {available_commands} ]")
        
        if self.tutorial_step == 1:
            self.stage.write("\n[SYSTEM AI]: Excellent. Your first task is to locate the source.")
            self.stage.write("[SYSTEM AI]: Type 'scan' to run a diagnostic.")
            self.tutorial_step = 2 

    def cmd_unknown(self, command: str) -> None:
        self.stage.write(f"> COMMAND NOT RECOGNIZED: {command}")

    # ==========================================
    # MAIN GAME LOOP START
    # ==========================================
    def start_main_game(self) -> None:
        self.stage.write("\n--- INFECTION DETECTED ---")
        self.stage.write("> Hex Dump Initializing...")

if __name__ == "__main__":
    app = VirusGame()
    app.run()