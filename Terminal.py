import asyncio
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual import work

from director import StoryDirector
from Defend_gameplay import DefenseGame, FILES, HOME_FILES, ATTACKER_LINES, TRAP_LINES

ASCII_TITLE = r"""
  ____ _               _   _   _            _    
 / ___| |__   ___  ___| |_| | | | __ _  ___| | __
| |  _| '_ \ / _ \/ __| __| |_| |/ _` |/ __| |/ /
| |_| | | | | (_) \__ \ |_|  _  | (_| | (__|   < 
 \____|_| |_|\___/|___/\__|_| |_|\__,_|\___|_|\_\
 
 :: PRODIGY OS v0.6.7 :: UNAUTHORIZED ACCESS FATAL ::
"""

class Status(Static):
    pass

class VirusGame(App):
    CSS = """
    Screen { layout: vertical; }
    Horizontal { height: 1fr; }
    #left-stage { width: 50%; height: 100%; border: solid lime; background: #050505; overflow-x: hidden; }
    #right-split { width: 50%; height: 100%; }
    #right-top { height: 50%; border: solid yellow; background: #050505; }
    #right-bottom { height: 50%; border: solid dodgerblue; background: #000000; }
    RichLog { padding: 1; color: lime; text-style: bold; overflow-x: hidden; }
    Status { padding: 1; content-align: left top; color: yellow; }
    Input { border: none; background: #000000; color: cyan; }
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
        
        self.director = StoryDirector() 
        self.defense = DefenseGame()

        self.command_map = {
            "clear": self.cmd_clear,
            "scan": self.cmd_scan,
            "help": self.cmd_help,
            "connect": self.cmd_connect,
            "files": self.cmd_files,
            "ls": self.cmd_ls,
            "manual": self.cmd_manual,
            "decode": self.cmd_decode,
            "inspect": self.cmd_inspect,
            "encrypt": self.cmd_encrypt,
            "debug": self.cmd_debug,
            "delete": self.cmd_delete,
        }
        
        self.update_status_display()
        self.set_interval(1.0, self.update_status_display)
        
        self.set_timer(1.0, self.boot_step_1)
        self.set_timer(3.5, self.boot_step_2)

    @work
    async def type_out_lines(self, lines: list[str], delay: float = 0.15) -> None:
        for line in lines:
            self.stage.write(line)
            await asyncio.sleep(delay)

    def boot_step_1(self):
        self.type_out_lines(self.director.advance_tutorial(1), delay=0.25)
            
    def boot_step_2(self):
        self.stage.clear()
        self.stage.write(ASCII_TITLE)
        self.type_out_lines(self.director.advance_tutorial(2), delay=0.2)
        self.update_status_display()

    def boot_step_3(self):
        self.type_out_lines(self.director.advance_tutorial(4), delay=0.2)
        self.update_status_display()
        self.director.tutorial_step = 3

    def update_status_display(self) -> None:
        if self.director.tutorial_step >= 3 and self.defense.game_active:
            self.director.heartbeat = int(self.defense.bpm)
            self.director.cpu = int(self.defense.cpu)
            self.director.ram_used = self.defense.ram

        self.status_text = self.director.get_status_text(
            game_active=self.defense.game_active,
            defense_state=self.defense
        )
        self.query_one("#status_view", Status).update(self.status_text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_input = event.value.strip().lower()
        self.query_one(Input).value = "" 
        
        if not raw_input: return
        self.stage.write(f"\n> root@system:~# {raw_input}")

        parts = raw_input.split()
        base_command, parts_args = parts[0], parts[1:]

        if base_command in self.command_map:
            if base_command in ["decode", "inspect", "encrypt", "debug", "delete"]:
                self.command_map[base_command](parts_args)
            elif base_command == "connect":
                self.cmd_connect(parts_args)
            else:
                self.command_map[base_command]()
        else:
            self.cmd_unknown(base_command)
            
    def cmd_connect(self, args) -> None:
        if self.director.tutorial_step == 2:
            self.type_out_lines(self.director.advance_tutorial(3), delay=0.3)
            self.update_status_display()
            self.set_timer(2.0, self.boot_step_3)
        else:
            self.stage.write("> ERROR: Neural link already established or invalid command.")

    def cmd_clear(self) -> None:
        self.stage.clear()

    def cmd_help(self) -> None:
        available_commands = ", ".join(self.command_map.keys())
        self.stage.write(f"> Available modules: [ {available_commands} ]")
        if self.director.tutorial_step in [3, 4]:
            self.stage.write("\n[SYSTEM AI]: Diagnostic complete. Type 'scan' to run sector analysis.")
            self.director.tutorial_step = 5

    def cmd_scan(self) -> None:
        self.stage.write("> Scanning memory sectors... [ OK ]")
        if self.director.tutorial_step >= 3:
            self.stage.write("\n[SYSTEM AI]: Anomaly detected in core cluster. Stand by.")
            self.set_timer(2.0, self.start_main_game)

    def cmd_unknown(self, command: str) -> None:
        self.stage.write(f"> COMMAND NOT RECOGNIZED: {command}")

    def cmd_manual(self) -> None:
        self.stage.write("> DEFENSE MANUAL:")
        self.stage.write(">   files              list the infected directory")
        self.stage.write(">   decode <file>      decode a file")
        self.stage.write(">   ls                 list your local directory")
        self.stage.write(">   inspect <file>     check file for infection")
        self.stage.write(">   encrypt <file>     deploy defense")
        self.stage.write(">   debug <file>       purge process")
        self.stage.write(">   delete <file>      purge target file")

    def start_main_game(self) -> None:
        self.stage.write("\n--- INFECTION DETECTED ---")
        self.stage.write("> Type 'files' for the infected directory, 'manual' for defense steps.")
        self.defense.game_active = True
        self.update_status_display()
        self.vitals_timer = self.set_interval(1.0, self.vitals_tick)
        alert_msg = self.defense.launch_attack()
        self.stage.write(alert_msg)

    def vitals_tick(self) -> None:
        crashed, msg = self.defense.tick()
        if msg:
            self.stage.write(f"\n{msg}")
        if crashed:
            self.system_crash()
            return
        self.update_status_display()

    def system_crash(self) -> None:
        self.defense.game_active = False
        if self.vitals_timer: self.vitals_timer.stop()
        self.update_status_display()
        self.stage.write("\n=== SYSTEM OVERLOAD. FLATLINE. ===")
        self.stage.write("[UNKNOWN]: I'm in.")
        self.query_one(Input).disabled = True

    def win(self) -> None:
        if self.vitals_timer: self.vitals_timer.stop()
        self.defense.game_active = False
        self.stage.write("\n=== SOURCE LOCATED ===")
        self.stage.write("[UNKNOWN]: No... how did you...")
        self.query_one(Input).disabled = True

    def cmd_files(self) -> None:
        if not self.defense.game_active: return
        self.stage.write("> Infected directory:")
        for name in FILES:
            mark = " (decoded)" if name in self.defense.decoded else ""
            self.stage.write(f">   {name}{mark}")

    def cmd_decode(self, args) -> None:
        if not self.defense.game_active or self.defense.active_attack or not args: return
        name = args[0]
        if name not in FILES or name in self.defense.decoded: return
        self.defense.decoded.add(name)
        self.stage.write(f"> Decoding {name}...")
        f = FILES[name]
        if f["safe"]:
            self.stage.write(f"> {f['result']}")
            if f.get("win"): self.win()
        else:
            self.stage.write(random.choice(TRAP_LINES))
            alert_msg = self.defense.launch_attack()
            self.stage.write(alert_msg)

    def cmd_ls(self) -> None:
        if not self.defense.game_active: return
        self.stage.write("> /home/operator:")
        for name in self.defense.home_files:
            mark = " [inspected]" if name in self.defense.inspected else ""
            self.stage.write(f">   {name}{mark}")

    def pick_file(self, args, verb):
        if not self.defense.active_attack or not args or args[0] not in self.defense.home_files:
            self.stage.write(f"> Usage: {verb} <filename> (see 'ls')")
            return None
        return args[0]

    def wrong_file_penalty(self, name) -> None:
        self.defense.cpu = min(100, self.defense.cpu + 15)
        self.defense.ram = min(16, self.defense.ram + 1.5)
        self.defense.bpm = min(200, self.defense.bpm + 15)
        self.stage.write(f"> {name} was clean. The attacker remains active.")
        self.stage.write("[UNKNOWN]: Wasting time? Good.")
        if self.defense.cpu >= 100 or self.defense.ram >= 16 or self.defense.bpm >= 180:
            self.system_crash()
        else:
            self.update_status_display()

    def cmd_inspect(self, args) -> None:
        name = self.pick_file(args, "inspect")
        if not name: return
        self.defense.inspected.add(name)
        if name == self.defense.infected_file:
            self.stage.write(f"> {name}: HIDDEN PROCESS. Outbound traffic to unknown host.")
            self.stage.write("> This is the infection source.")
        else:
            self.stage.write(f"> {name}: clean. No anomalies.")

    def cmd_encrypt(self, args) -> None:
        name = self.pick_file(args, "encrypt")
        if not name: return
        self.stage.write(f"> Encrypting {name}...")
        if name == self.defense.infected_file:
            self.defense.firewalls += 1
            self.stage.write(f"> Encryption complete. Firewall #{self.defense.firewalls} online.")
            self.stage.write(random.choice(ATTACKER_LINES))
            self.defense.end_attack()
        else:
            self.wrong_file_penalty(name)

    def cmd_debug(self, args) -> None:
        name = self.pick_file(args, "debug")
        if not name: return
        self.stage.write(f"> Debugging {name}...")
        if name != self.defense.infected_file:
            self.wrong_file_penalty(name)
            return
        self.stage.write("> Malicious process killed.")
        if self.defense.scars > 0:
            self.defense.scars -= 1
            self.defense.base_cpu = max(4, self.defense.base_cpu - 8)
            self.defense.base_ram = max(1.2, self.defense.base_ram - 1.0)
            self.stage.write("> Memory repaired. One point of permanent damage removed.")
        self.defense.cpu = min(100, self.defense.cpu + 10)
        self.defense.end_attack()
        if self.defense.cpu >= 100 or self.defense.ram >= 16 or self.defense.bpm >= 180:
            self.system_crash()

    def cmd_delete(self, args) -> None:
        name = self.pick_file(args, "delete")
        if not name: return
        self.defense.home_files.remove(name)
        self.stage.write(f"> {name} deleted permanently.")
        if name == self.defense.infected_file:
            self.stage.write("> Infection source destroyed. No firewall gained.")
            self.defense.end_attack()
        else:
            self.wrong_file_penalty(name)

if __name__ == "__main__":
    app = VirusGame()
    app.run()