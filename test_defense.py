import asyncio
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

from Defend_gameplay import DefenseGame, bar, ATTACKER_LINES

class Status(Static): pass

class DefenseTesterApp(App):
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
                    yield Input(placeholder="> test_mode:~# ", id="command_input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self.stage = self.query_one("#stage_view", RichLog)
        
        self.defense = DefenseGame()
        self.defense.game_active = True
        
        self.command_map = {
            "ls": self.cmd_ls,
            "inspect": self.cmd_inspect,
            "encrypt": self.cmd_encrypt,
            "debug": self.cmd_debug,
            "delete": self.cmd_delete,
            "start": self.cmd_start, # Custom command to spawn new attacks!
            "clear": self.cmd_clear
        }

        self.arg_commands = ["inspect", "encrypt", "debug", "delete"]

        self.stage.write("=== DEFENSE TEST ENVIRONMENT ===")
        self.stage.write("> Type 'start' to launch an attack.")
        self.stage.write("> Use ls, inspect, encrypt, debug, delete to defend.\n")

        self.update_status_display()
        self.vitals_timer = self.set_interval(1.0, self.vitals_tick)

    async def type_out_lines(self, lines: list, delay: float = 0.05) -> None:
        for line in lines:
            self.stage.write(line)
            await asyncio.sleep(delay)

    def get_status_text(self) -> str:
        threat = self.defense.active_attack["name"] if self.defense.active_attack else "NONE"
        return (
            f"SYSTEM STATUS (TEST MODE):\n\n"
            f"CPU:   [{bar(self.defense.cpu, 100)}] {int(self.defense.cpu)}%\n"
            f"RAM:   [{bar(self.defense.ram, 16)}] {self.defense.ram:.1f}/16GB\n"
            f"HEART: [{bar(self.defense.bpm, 180)}] {int(self.defense.bpm)} BPM\n\n"
            f"THREAT: {threat}\n"
            f"FIREWALLS: {self.defense.firewalls}\n"
            f"PERM DAMAGE: {self.defense.scars}\n"
            f"BASELINE: {int(self.defense.base_cpu)}% / {self.defense.base_ram:.1f}GB"
        )

    def update_status_display(self) -> None:
        self.status_text = self.get_status_text()
        self.query_one("#status_view", Status).update(self.status_text)

    async def vitals_tick(self) -> None:
        if not self.defense.game_active:
            return
            
        crashed, msg = self.defense.tick()
        if msg: 
            await self.type_out_lines(msg.split('\n'), delay=0.05)
            
        if crashed:
            self.defense.game_active = False
            self.update_status_display()
            await self.type_out_lines(["\n=== SYSTEM OVERLOAD. FLATLINE ==="], delay=0.1)
            self.stage.write("\n> Type 'clear' then restart the app to try again.")
        else:
            self.update_status_display()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_input = event.value.strip().lower()
        self.query_one(Input).value = "" 
        if not raw_input: return
        self.stage.write(f"\n> {raw_input}")

        parts = raw_input.split()
        base_command, args = parts[0], parts[1:]

        if base_command in self.command_map:
            if base_command in self.arg_commands:
                await self.command_map[base_command](args)
            else:
                await self.command_map[base_command]()
        else:
            await self.type_out_lines(["> COMMAND NOT RECOGNIZED."], delay=0.05)

    # --- CUSTOM TEST COMMANDS ---
    async def cmd_clear(self):
        self.stage.clear()

    async def cmd_start(self):
        if self.defense.active_attack:
            await self.type_out_lines(["> Attack already in progress!"], delay=0.05)
            return
        attack_msg = self.defense.launch_attack().split('\n')
        await self.type_out_lines(attack_msg, delay=0.05)

    # --- CORE DEFENSE COMMANDS ---
    async def cmd_ls(self) -> None:
        await self.type_out_lines(["> /home/operator:"] + [f">   {name}" for name in self.defense.home_files], delay=0.05)

    async def pick_file(self, args, verb):
        if not self.defense.active_attack or not args or args[0] not in self.defense.home_files:
            await self.type_out_lines([f"> Usage: {verb} <filename>"], delay=0.05)
            return None
        return args[0]

    async def cmd_inspect(self, args) -> None:
        if not args:
            await self.type_out_lines(["> Usage: inspect <filename>"], delay=0.05)
            return
        name = args[0]
        if name not in self.defense.home_files:
            await self.type_out_lines([f"> File not found: {name}"], delay=0.05)
            return
            
        self.defense.inspected.add(name)
        if name == self.defense.infected_file:
            await self.type_out_lines([f"> {name}: HIDDEN PROCESS. Infection source."], delay=0.05)
        else:
            await self.type_out_lines([f"> {name}: clean."], delay=0.05)

    async def cmd_encrypt(self, args) -> None:
        name = await self.pick_file(args, "encrypt")
        if not name: return
        await self.type_out_lines([f"> Encrypting {name}..."], delay=0.05)
        
        if name == self.defense.infected_file:
            self.defense.firewalls += 1
            await self.type_out_lines([
                f"> Encryption complete. Firewall #{self.defense.firewalls} online.",
                random.choice(ATTACKER_LINES)
            ], delay=0.05)
            self.defense.end_attack()
        else:
            self.defense.cpu += 5  # Forgiving penalty
            await self.type_out_lines([f"> {name} was clean. Attack continues."], delay=0.05)

    async def cmd_debug(self, args) -> None:
        name = await self.pick_file(args, "debug")
        if not name: return
        await self.type_out_lines([f"> Debugging {name}..."], delay=0.05)
        
        if name == self.defense.infected_file:
            await self.type_out_lines(["> Malicious process killed."], delay=0.05)
            self.defense.end_attack()
        else:
            self.defense.cpu += 5
            await self.type_out_lines([f"> {name} was clean. Attack continues."], delay=0.05)

    async def cmd_delete(self, args) -> None:
        name = await self.pick_file(args, "delete")
        if not name: return
        self.defense.home_files.remove(name)
        await self.type_out_lines([f"> {name} deleted permanently."], delay=0.05)
        
        if name == self.defense.infected_file:
            await self.type_out_lines(["> Infection source destroyed."], delay=0.05)
            self.defense.end_attack()
        else:
            self.defense.cpu += 5
            await self.type_out_lines([f"> {name} was clean. Attack continues."], delay=0.05)

if __name__ == "__main__":
    app = DefenseTesterApp()
    app.run()