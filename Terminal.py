import asyncio
import getpass
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual import work

# Import your director and defense gameplay module
from director import StoryDirector
from Defend_gameplay import (
    FILES, HOME_FILES, ATTACKER_LINES, TRAP_LINES, 
    ATTACK_DEADLINE, PERM_CPU_HIT, PERM_RAM_HIT, MAX_BASE_CPU, MAX_BASE_RAM, bar
)

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
        
        self.director = StoryDirector() 
        
        # --- DEFENSE GAME STATE VARIABLES ---
        self.base_cpu = 4
        self.base_ram = 1.2
        self.cpu = self.base_cpu
        self.ram = self.base_ram
        self.bpm = 72

        self.active_attack = None
        self.infected_file = None
        self.inspected = set()
        self.attack_elapsed = 0
        self.scarred = False
        self.scars = 0
        self.firewalls = 0
        self.vitals_timer = None
        self.game_active = False
        self.decoded = set()
        self.home_files = list(HOME_FILES)
        # ------------------------------------

        # Command mapping including defense commands
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
        lines = self.director.advance_tutorial(1)
        self.type_out_lines(lines, delay=0.25)
            
    def boot_step_2(self):
        self.stage.clear()
        self.stage.write(ASCII_TITLE)
        lines = self.director.advance_tutorial(2)
        self.type_out_lines(lines, delay=0.2)
        self.update_status_display()

    def boot_step_3(self):
        lines = self.director.advance_tutorial(4)
        self.type_out_lines(lines, delay=0.2)
        self.update_status_display()
        
        # Transition straight into the defense minigame tutorial step
        self.tutorial_step = 3

    # ==========================================
    # DYNAMIC STATUS DISPLAY (Integrates Vitals)
    # ==========================================
    def update_status_display(self) -> None:
        if self.director.tutorial_step == 0 or self.director.tutorial_step == 1:
            self.status_text = "SYSTEM OFFLINE"
        elif self.director.tutorial_step == 2 and self.active_attack is None:
            # Standby state before main game starts
            self.status_text = self.director.get_status_text()
        else:
            # Full defense minigame dashboard view
            self.director.heartbeat = int(self.bpm)
            self.director.cpu = int(self.cpu)
            self.director.ram_used = self.ram
            
            threat = self.active_attack["name"] if self.active_attack else "MONITORING"
            self.status_text = (
                f"NEURAL SYNC STATUS:\n\n"
                f"CPU:   [{bar(self.cpu, 100)}] {int(self.cpu)}%\n"
                f"RAM:   [{bar(self.ram, 16)}] {self.ram:.1f}/16GB\n"
                f"HEART: [{bar(self.bpm, 180)}] {int(self.bpm)} BPM\n\n"
                f"THREAT: {threat}\n"
                f"FIREWALLS: {self.firewalls}\n"
                f"SCARS: {self.scars}"
            )
        self.query_one("#status_view", Status).update(self.status_text)

    # ==========================================
    # INPUT PARSING
    # ==========================================
    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_input = event.value.strip().lower()
        self.query_one(Input).value = "" 
        
        if not raw_input: return

        self.stage.write(f"\n> root@system:~# {raw_input}")

        parts = raw_input.split()
        base_command = parts[0]
        args = parts[1:]

        if base_command in self.command_map:
            # Pass args if the command accepts them, otherwise call cleanly
            if base_command in ["decode", "inspect", "encrypt", "debug", "delete"]:
                self.command_map[base_command](args)
            elif base_command == "connect":
                self.cmd_connect(args)
            else:
                self.command_map[base_command]()
        else:
            self.cmd_unknown(base_command)
            
    # ==========================================
    # COMMANDS & DEFENSE GAME LOGIC
    # ==========================================
    def cmd_connect(self, args) -> None:
        if self.director.tutorial_step == 2:
            lines = self.director.advance_tutorial(3)
            self.type_out_lines(lines, delay=0.3)
            self.update_status_display()
            self.set_timer(2.0, self.boot_step_3)
        else:
            self.stage.write("> ERROR: Neural link already established or invalid command.")

    def cmd_clear(self) -> None:
        self.stage.clear()

    def cmd_help(self) -> None:
        available_commands = ", ".join(self.command_map.keys())
        self.stage.write(f"> Available modules: [ {available_commands} ]")
        
        if self.director.tutorial_step == 4 or self.director.tutorial_step == 3:
            self.stage.write("\n[SYSTEM AI]: Diagnostic complete. Type 'scan' to run sector analysis.")
            self.director.tutorial_step = 5

    def cmd_scan(self) -> None:
        self.stage.write("> Scanning memory sectors... [ OK ]")
        if self.director.tutorial_step >= 3:
            self.stage.write("\n[SYSTEM AI]: Anomaly detected in core cluster. Stand by.")
            self.tutorial_step = 3
            self.set_timer(2.0, self.start_main_game)

    def cmd_unknown(self, command: str) -> None:
        self.stage.write(f"> COMMAND NOT RECOGNIZED: {command}")

    def cmd_manual(self) -> None:
        self.stage.write("> DEFENSE MANUAL:")
        self.stage.write(">   files              list the infected directory")
        self.stage.write(">   decode <file>      decode a file (careful: traps exist)")
        self.stage.write(">   ls                 list your local directory")
        self.stage.write(">   inspect <file>     check a file for the infection")
        self.stage.write(">   encrypt <file>     deploy defensive encryption")
        self.stage.write(">   debug <file>       purge malicious process")
        self.stage.write(">   delete <file>      instantly purge target file")

    # --- DEFENSE GAMEPLAY INTEGRATION ---
    def start_main_game(self) -> None:
        self.stage.write("\n--- INFECTION DETECTED ---")
        self.stage.write("> Type 'files' for the infected directory, 'manual' for defense steps.")
        self.game_active = True
        self.update_status_display()
        self.vitals_timer = self.set_interval(1.0, self.vitals_tick)
        self.launch_attack()

    def vitals_tick(self) -> None:
        import random
        from Defend_gameplay import ATTACKS
        if not self.game_active:
            return

        if self.active_attack:
            a = self.active_attack
            scale = 0.85 ** self.firewalls
            old_cpu = self.cpu
            self.cpu = min(100, self.cpu + a["cpu"] * scale)
            self.ram = min(16, self.ram + a["ram"] * scale)
            self.bpm = min(200, self.bpm + a["bpm"] * scale)

            self.attack_elapsed += 1
            remaining = ATTACK_DEADLINE - self.attack_elapsed
            if not self.scarred:
                if remaining == 4:
                    self.stage.write("\n> WARNING: Infection is digging into neural pathways.")
                if remaining <= 0:
                    self.apply_permanent_damage()

            if old_cpu < 70 <= self.cpu:
                self.stage.write("\n!!! WARNING: CPU CRITICAL. YOUR PULSE IS RACING. !!!")

            if self.check_crash():
                return
        else:
            self.cpu = max(self.base_cpu, self.cpu - 3)
            self.ram = max(self.base_ram, self.ram - 0.3)
            self.bpm = max(72, self.bpm - 4)

        self.update_status_display()

    def check_crash(self) -> bool:
        if self.cpu >= 100 or self.ram >= 16 or self.bpm >= 180:
            self.system_crash()
            return True
        return False

    def apply_permanent_damage(self) -> None:
        self.scarred = True
        self.scars += 1
        self.base_cpu = min(MAX_BASE_CPU, self.base_cpu + PERM_CPU_HIT)
        self.base_ram = min(MAX_BASE_RAM, self.base_ram + PERM_RAM_HIT)
        self.stage.write("\n!!! THE INFECTION TAKES ROOT !!!")
        self.stage.write("> Permanent neural damage: baseline CPU and RAM usage increased.")

    def launch_attack(self) -> None:
        import random
        from Defend_gameplay import ATTACKS
        if not self.game_active:
            return
        if not self.home_files:
            self.home_files = list(HOME_FILES)
        self.active_attack = random.choice(ATTACKS)
        self.infected_file = random.choice(self.home_files)
        self.inspected = set()
        self.attack_elapsed = 0
        self.scarred = False
        self.stage.write(f"\n!!! ALERT: {self.active_attack['name']} !!!")
        self.stage.write("> Unauthorized process feeding on cortex. Vitals climbing.")
        self.stage.write(f"> Neutralize within {ATTACK_DEADLINE}s to prevent permanent damage.")
        self.update_status_display()

    def end_attack(self) -> None:
        self.active_attack = None
        self.infected_file = None
        self.attack_elapsed = 0
        self.scarred = False
        self.update_status_display()

    def defend_success(self) -> None:
        import random
        self.firewalls += 1
        self.stage.write(f"> Encryption complete. Firewall #{self.firewalls} online.")
        self.stage.write(random.choice(ATTACKER_LINES))
        self.end_attack()

    def system_crash(self) -> None:
        self.game_active = False
        if self.vitals_timer:
            self.vitals_timer.stop()
        self.update_status_display()
        self.stage.write("\n=== NEURAL OVERLOAD. FLATLINE. ===")
        self.query_one(Input).disabled = True

    def win(self) -> None:
        if self.vitals_timer:
            self.vitals_timer.stop()
        self.game_active = False
        self.stage.write("\n=== SOURCE SECURED ===")
        self.query_one(Input).disabled = True

    def cmd_files(self) -> None:
        if not self.game_active:
            self.stage.write("> No file access yet.")
            return
        self.stage.write("> Infected directory:")
        for name in FILES:
            mark = " (decoded)" if name in self.decoded else ""
            self.stage.write(f">   {name}{mark}")

    def cmd_decode(self, args) -> None:
        import random
        if not self.game_active:
            self.stage.write("> Nothing to decode yet.")
            return
        if self.active_attack:
            self.stage.write("> Under attack! Defend your system first.")
            return
        if not args:
            self.stage.write("> Usage: decode <filename>")
            return

        name = args[0]
        if name not in FILES:
            self.stage.write(f"> File not found: {name}")
            return
        if name in self.decoded:
            self.stage.write("> Already decoded.")
            return

        self.decoded.add(name)
        self.stage.write(f"> Decoding {name}...")
        f = FILES[name]

        if f["safe"]:
            self.stage.write(f"> {f['result']}")
            if f.get("win"):
                self.win()
        else:
            self.stage.write(random.choice(TRAP_LINES))
            self.launch_attack()

    def cmd_ls(self) -> None:
        if not self.game_active:
            self.stage.write("> No directory access yet.")
            return
        self.stage.write("> /home/operator:")
        for name in self.home_files:
            mark = " [inspected]" if name in self.inspected else ""
            self.stage.write(f">   {name}{mark}")

    def pick_file(self, args, verb):
        if not self.active_attack:
            self.stage.write(f"> No active threat. Nothing to {verb}.")
            return None
        if not args or args[0] not in self.home_files:
            self.stage.write(f"> Usage: {verb} <filename> (see 'ls')")
            return None
        return args[0]

    def wrong_file_penalty(self, name) -> None:
        self.cpu = min(100, self.cpu + 15)
        self.ram = min(16, self.ram + 1.5)
        self.bpm = min(200, self.bpm + 15)
        self.stage.write(f"> {name} was clean. The attacker remains active.")
        if not self.check_crash():
            self.update_status_display()

    def cmd_inspect(self, args) -> None:
        name = self.pick_file(args, "inspect")
        if not name: return
        self.inspected.add(name)
        if name == self.infected_file:
            self.stage.write(f"> {name}: HIDDEN PROCESS. Outbound neural traffic detected.")
        else:
            self.stage.write(f"> {name}: Clean. No anomalies.")

    def cmd_encrypt(self, args) -> None:
        name = self.pick_file(args, "encrypt")
        if not name: return
        self.stage.write(f"> Encrypting {name}...")
        if name == self.infected_file:
            self.defend_success()
        else:
            self.wrong_file_penalty(name)

    def cmd_debug(self, args) -> None:
        name = self.pick_file(args, "debug")
        if not name: return
        self.stage.write(f"> Debugging {name}...")
        if name != self.infected_file:
            self.wrong_file_penalty(name)
            return
        self.stage.write("> Malicious process terminated.")
        if self.scars > 0:
            self.scars -= 1
            self.base_cpu = max(4, self.base_cpu - PERM_CPU_HIT)
            self.base_ram = max(1.2, self.base_ram - PERM_RAM_HIT)
            self.stage.write("> Neural memory repaired.")
        self.cpu = min(100, self.cpu + 10)
        self.end_attack()
        self.check_crash()

    def cmd_delete(self, args) -> None:
        name = self.pick_file(args, "delete")
        if not name: return
        self.home_files.remove(name)
        self.stage.write(f"> {name} deleted permanently.")
        if name == self.infected_file:
            self.stage.write("> Infection source destroyed.")
            self.end_attack()
        else:
            self.wrong_file_penalty(name)

if __name__ == "__main__":
    app = VirusGame()
    app.run()