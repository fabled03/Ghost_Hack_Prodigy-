from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

class Stage(Static):
    """The visual game stage."""
    pass

class Status(Static):
    """The status panel."""
    pass

class VirusGame(App):
    """Terminal-based hacking containment game."""
    
    # CSS styling to create the aesthetic and split screen
    CSS = """
    Screen {
        layout: vertical;
    }
    Horizontal {
        height: 1fr;
    }
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
    Stage {
        padding: 1;
        content-align: left top;
        text-style: bold;
        color: lime;
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

    # Adds a keyboard shortcut to quit safely
    BINDINGS = [("ctrl+c", "quit", "Quit")]

    # Reactive variables automatically update the UI when changed
    game_text = reactive("SYSTEM INITIALIZED...\nAwaiting commands.")
    status_text = reactive("SYSTEM STATUS:\n\nCPU: 12%\nRAM: 2.1GB/16GB\nTHREAT LEVEL: NONE")

    def compose(self) -> ComposeResult:
        """Builds the UI layout."""
        yield Header()
        
        with Horizontal():
            with Container(id="left-stage"):
                yield Stage(self.game_text, id="stage_view")
            
            with Vertical(id="right-split"):
                with Container(id="right-top"):
                    yield Status(self.status_text, id="status_view")
                    
                with Container(id="right-bottom"):
                    yield Input(placeholder="> root@system:~# ", id="command_input")
            
        yield Footer()

    def on_mount(self) -> None:
        """Fires exactly once when the game starts."""
        self.query_one(Input).focus() # Auto focus the typing area
        
        # THIS IS THE GAME LOOP. 
        self.tick_timer = self.set_interval(2.0, self.game_tick)

    def game_tick(self) -> None:
        """The background loop that updates the game world."""
        # For now, it does nothing. We will add the virus spawning logic here.
        pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Fires every time the player presses Enter."""
        raw_input = event.value.strip().lower()
        self.query_one(Input).value = "" # Instantly clear the input box
        
        if not raw_input:
            return

        # 1. Map text strings to class methods
        command_map = {
            "clear": self.cmd_clear,
            "scan": self.cmd_scan,
            "help": self.cmd_help,
        }

        # 2. Grab just the first word 
        base_command = raw_input.split()[0]

        # 3. Look up the command 
        if base_command in command_map:
            command_map[base_command]()
        else:
            self.cmd_unknown(base_command)
            
        # Push the updated text to the screens
        self.query_one("#stage_view", Stage).update(self.game_text)
        self.query_one("#status_view", Status).update(self.status_text)

    # ==========================================
    # INDIVIDUAL COMMAND LOGIC
    # ==========================================

    def cmd_clear(self) -> None:
        self.game_text = ""

    def cmd_scan(self) -> None:
        self.game_text += "\n> Scanning memory sectors... [ OK ]"
        self.status_text = "SYSTEM STATUS:\n\nCPU: 89% [SCANNING]\nRAM: 4.5GB/16GB\nTHREAT LEVEL: SEARCHING..."

    def cmd_help(self) -> None:
        self.game_text += "\n> Available commands: scan, clear, help"

    def cmd_unknown(self, command: str) -> None:
        self.game_text += f"\n> COMMAND NOT RECOGNIZED: {command}"


if __name__ == "__main__":
    app = VirusGame()
    app.run()