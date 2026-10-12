import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual import work

# Import your director
from director import StoryDirector  

# ==========================================
# SAFE STUB (this part should get removed and moved to the minigame py later)
# ==========================================
class FileSystemGame:
    def __init__(self):
        self.current_path = "/"
    def list_dir(self, args) -> str:
        return "[STUB] Waiting for partner's file system module (ls)..."
    def change_dir(self, args) -> str:
        return "Navigation offline. Waiting for partner module (cd)."
    def scan_file(self, args) -> str:
        return "Scanner offline. Waiting for partner module (scan)."
    def decode_file(self, args):
        return None, "Decoder offline. Waiting for partner module (decode)."
# ==========================================

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
        overflow-x: hidden;
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
    RichLog {
        padding: 1;
        color: lime;
        text-style: bold;
        overflow-x: hidden;
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
                yield RichLog(id="stage_view", markup=False, wrap=True)
            with Vertical(id="right-split"):
                with Container(id="right-top"):
                    yield Status(self.status_text, id="status_view")
                with Container(id="right-bottom"):
                    yield Input(placeholder="> root@system:~# ", id="command_input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self.stage = self.query_one("#stage_view", RichLog)
        
        # Initialize modules using the safe stub
        self.fs_game = FileSystemGame()
        self.director = StoryDirector() 
        
        self.command_map = {
            "clear": self.cmd_clear,
            "scan": self.cmd_scan,
            "help": self.cmd_help,
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "decode": self.cmd_decode,
            "connect": self.cmd_connect,
        }
        
        # Start the narrative boot sequence with animations
        self.query_one("#status_view", Status).update(self.director.get_status_text())
        self.set_timer(1.0, self.boot_step_1)
        self.set_timer(3.5, self.boot_step_2)

    # ==========================================
    # ANIMATION WORKER
    # ==========================================
    @work
    async def type_out_lines(self, lines: list[str], delay: float = 0.15) -> None:
        """Asynchronously prints lines one by one to simulate terminal typing."""
        for line in lines:
            self.stage.write(line)
            await asyncio.sleep(delay)

    # ==========================================
    # BOOT SEQUENCE LOGIC
    # ==========================================
    def boot_step_1(self):
        lines = self.director.advance_tutorial(1)
        self.type_out_lines(lines, delay=0.25)
            
    def boot_step_2(self):
        self.stage.clear()
        self.stage.write(ASCII_TITLE)
        lines = self.director.advance_tutorial(2)
        self.type_out_lines(lines, delay=0.2)
        self.query_one("#status_view", Status).update(self.director.get_status_text())

    def boot_step_3(self):
        lines = self.director.advance_tutorial(4)
        self.type_out_lines(lines, delay=0.2)
        self.query_one("#status_view", Status).update(self.director.get_status_text())

    # ==========================================
    # INPUT PARSING
    # ==========================================
    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_input = event.value.strip().lower()
        self.query_one(Input).value = "" 
        
        if not raw_input: return

        self.stage.write(f"\n> {self.fs_game.current_path}# {raw_input}")

        parts = raw_input.split()
        base_command = parts[0]
        args = parts[1:]

        if base_command in self.command_map:
            self.command_map[base_command](args) 
        else:
            self.cmd_unknown(base_command)
            
    # ==========================================
    # COMMANDS
    # ==========================================
    def cmd_connect(self, args) -> None:
        if self.director.tutorial_step == 2:
            lines = self.director.advance_tutorial(3)
            self.type_out_lines(lines, delay=0.3)
            self.query_one("#status_view", Status).update(self.director.get_status_text())
            self.set_timer(2.0, self.boot_step_3)
        else:
            self.stage.write("> ERROR: Neural link already established or invalid command.")

    def cmd_clear(self, args) -> None:
        self.stage.clear()

    def cmd_help(self, args) -> None:
        available_commands = ", ".join(self.command_map.keys())
        self.stage.write(f"> Available modules: [ {available_commands} ]")

    def cmd_ls(self, args) -> None:
        self.stage.write(self.fs_game.list_dir(args))

    def cmd_cd(self, args) -> None:
        self.stage.write(f"> {self.fs_game.change_dir(args)}")

    def cmd_scan(self, args) -> None:
        self.stage.write(self.fs_game.scan_file(args))

    def cmd_decode(self, args) -> None:
        was_malicious, message = self.fs_game.decode_file(args)
        self.stage.write(f"> {message}")
        
        if was_malicious is True:
            self.director.heartbeat += 15
        elif was_malicious is False:
            self.director.cpu += 25
            
        self.query_one("#status_view", Status).update(self.director.get_status_text())

    def cmd_unknown(self, command: str) -> None:
        self.stage.write(f"> COMMAND NOT RECOGNIZED: {command}")

if __name__ == "__main__":
    app = VirusGame()
    app.run()