from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container
from textual.reactive import reactive

class Stage(Static):
    """The visual game stage."""
    pass

class VirusGame(App):
    """Terminal-based hacking containment game."""
    
    # CSS styling to create the aesthetic and split screen
    CSS = """
    Screen {
        layout: vertical;
    }
    #stage-container {
        height: 75%;
        border: solid lime;
        background: #050505;
    }
    #console-container {
        height: 25%;
        border: solid dodgerblue;
        background: #000000;
    }
    Stage {
        padding: 1;
        content-align: left top;
        text-style: bold;
        color: lime;
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

    def compose(self) -> ComposeResult:
        """Builds the UI layout."""
        yield Header()
        
        with Container(id="stage-container"):
            yield Stage(self.game_text, id="stage_view")
        
        with Container(id="console-container"):
            yield Input(placeholder="> root@system:~# ", id="command_input")
            
        yield Footer()

    def on_mount(self) -> None:
        """Fires exactly once when the game starts."""
        self.query_one(Input).focus() # Auto focus the typing area
        
        # THIS IS THE GAME LOOP 
        self.tick_timer = self.set_interval(2.0, self.game_tick)

    def game_tick(self) -> None:
        """The background loop that updates the game world."""
        # For now, it does nothing. We will add the virus logic here.
        pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Fires every time the player presses Enter."""
        command = event.value.strip().lower()
        self.query_one(Input).value = "" # Instantly clear the input box
        
        if not command:
            return

        # Basic Command Parser
        if command == "clear":
            self.game_text = ""
        elif command == "scan":
            self.game_text += "\n> Scanning memory sectors... [ OK ]"
        elif command == "help":
            self.game_text += "\n> Available commands: scan, clear, help"
        else:
            self.game_text += f"\n> COMMAND NOT RECOGNIZED: {command}"
            
        # Push the updated text to the screen
        self.query_one("#stage_view", Stage).update(self.game_text)

if __name__ == "__main__":
    app = VirusGame()
    app.run()
