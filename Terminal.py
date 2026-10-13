
import asyncio
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

from director import StoryDirector
from Defend_gameplay import DefenseGame, HOME_FILES, ATTACKER_LINES, TRAP_LINES
from Attack_gameplay import DataPipelineGame

ASCII_TITLE = r"""
  ____ _               _   _   _            _    
 / ___| |__   ___  ___| |_| | | | __ _  ___| | __
| |  _| '_ \ / _ \/ __| __| |_| |/ _` |/ __| |/ /
| |_| | | | | (_) \__ \ |_|  _  | (_| | (__|   < 
 \____|_| |_|\___/|___/\__|_| |_|\__,_|\___|_|\_\
 
 :: PRODIGY OS v0.6.7 :: UNAUTHORIZED ACCESS FATAL ::
"""

class Status(Static): pass

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
        self.pipeline = DataPipelineGame() 

        self.command_map = {
            "help": self.cmd_help,
            "connect": self.cmd_connect,
            "clear": self.cmd_clear,
            "ls": self.cmd_ls,
            "inspect": self.cmd_inspect,
            "encrypt": self.cmd_encrypt,
            "debug": self.cmd_debug,
            "delete": self.cmd_delete,
            "rotate": self.cmd_rotate,      
            "transmit": self.cmd_transmit,
            "jump": self.cmd_jump
        }
        
        self.arg_commands = ["ls", "inspect", "encrypt", "debug", "delete", "rotate", "jump"]
        
        self.update_status_display()
        self.set_interval(1.0, self.update_status_display)
        
        self.set_timer(1.0, self.boot_step_1)
        self.set_timer(3.5, self.boot_step_2)

    async def type_out_lines(self, lines: list, delay: float = 0.05) -> None:
        for line in lines:
            self.stage.write(line)
            await asyncio.sleep(delay)

    async def boot_step_1(self):
        await self.type_out_lines(self.director.advance_tutorial(1), delay=0.15)
            
    async def boot_step_2(self):
        self.stage.clear()
        self.stage.write(ASCII_TITLE)
        await self.type_out_lines(self.director.advance_tutorial(2), delay=0.15)
        self.update_status_display()

    async def boot_step_3(self):
        await self.type_out_lines(self.director.advance_tutorial(4), delay=0.15)
        self.update_status_display()

    async def trigger_phase(self, phase: int):
        lines = self.director.get_phase_text(phase)
        await self.type_out_lines(lines, delay=0.1)
        
        if phase == 5:
            # INSTANT WRITE: Prevent the grid from typing out letter-by-letter
            grid = self.pipeline.start_game()
            if isinstance(grid, list):
                for line in grid: self.stage.write(line)
            else:
                self.stage.write(grid)
                
        elif phase == 6:
            self.defense.game_active = True
            self.vitals_timer = self.set_interval(1.0, self.vitals_tick)
            attack_msg = self.defense.launch_attack().split('\n')
            await self.type_out_lines(attack_msg, delay=0.05)

    def update_status_display(self) -> None:
        if self.defense.game_active:
            self.director.heartbeat = int(self.defense.bpm)
            self.director.cpu = int(self.defense.cpu)
            self.director.ram_used = self.defense.ram

        self.status_text = self.director.get_status_text(
            game_active=self.defense.game_active,
            defense_state=self.defense
        )
        self.query_one("#status_view", Status).update(self.status_text)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_input = event.value.strip().lower()
        self.query_one(Input).value = "" 
        if not raw_input: return
        self.stage.write(f"\n> root@system:~# {raw_input}")

        parts = raw_input.split()
        base_command, args = parts[0], parts[1:]

        if self.director.current_phase == 4 and base_command not in ["rotate", "transmit", "jump"]:
            await self.type_out_lines(["> [ERROR] ACCESS DENIED BY SYSTEM AI."], delay=0.05)
            return

        if base_command in self.command_map:
            if base_command in self.arg_commands:
                await self.command_map[base_command](args)
            else:
                await self.command_map[base_command]()
        else:
            await self.type_out_lines(["> COMMAND NOT RECOGNIZED."], delay=0.05)
            
    async def cmd_clear(self):
        self.stage.clear()

    async def cmd_connect(self) -> None:
        if self.director.tutorial_step == 2:
            await self.type_out_lines(self.director.advance_tutorial(3), delay=0.15)
            self.update_status_display()
            self.set_timer(2.0, self.boot_step_3)
        else:
            await self.type_out_lines(["> ERROR: Neural link already established."], delay=0.05)

    async def cmd_help(self) -> None:
        available_commands = ", ".join(self.command_map.keys())
        await self.type_out_lines([f"> Available modules: [ {available_commands} ]"], delay=0.05)
        if self.director.tutorial_step == 4 and self.director.current_phase == 1:
            await self.trigger_phase(2)

    async def cmd_ls(self) -> None:
        if self.defense.game_active:
            # Changed from /home/operator to a single unified target folder
            await self.type_out_lines(["> /secure_memory_pool/"] + [f">   {name}" for name in self.defense.home_files], delay=0.05)
            return

        # Phase 2 Directory Navigation
        if not args:
            await self.type_out_lines([
                "> /home/operator:",
                ">   [DIR] documents/",
                ">   [DIR] personal/",
                ">   [DIR] projects/",
                ">   [DIR] messages/",
                ">   [DIR] images/"
            ], delay=0.05)
        elif args[0] == "images":
            await self.type_out_lines([
                "> /home/operator/images:",
                ">   family_photo.jpg",
                ">   vacation.png",
                ">   disease.png",
                ">   operation.png"
            ], delay=0.05)
        else:
            await self.type_out_lines([f"> Contents of {args[0]}: Access Denied or Empty."], delay=0.05)

    async def cmd_inspect(self, args) -> None:
        if not args:
            await self.type_out_lines(["> Usage: inspect <filename>"], delay=0.05)
            return
            
        name = args[0]
        # Progress story if the user inspects the target file in phase 2
        if name == "disease.png" and self.director.current_phase == 2:
            await self.type_out_lines([f"> {name}: I tried to hold on. I tried to fight. I tried it all. Yet they gave up on me."], delay=0.05)
            await asyncio.sleep(1)
            await self.trigger_phase(3)
            await self.trigger_phase(4)
            await self.trigger_phase(5)
            return

        if self.defense.game_active:
            if name not in self.defense.home_files:
                await self.type_out_lines([f"> File not found: {name}"], delay=0.05)
                return
            self.defense.inspected.add(name)
            if name == self.defense.infected_file:
                await self.type_out_lines([f"> {name}: HIDDEN PROCESS. Infection source."], delay=0.05)
            else:
                await self.type_out_lines([f"> {name}: clean."], delay=0.05)
        else:
            await self.type_out_lines([f"> {name} inspected. Nothing unusual."], delay=0.05)

    async def pick_file(self, args, verb):
        if not self.defense.active_attack or not args or args[0] not in self.defense.home_files:
            await self.type_out_lines([f"> Usage: {verb} <filename>"], delay=0.05)
            return None
        return args[0]

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
            
            if self.director.current_phase == 6:
                await self.trigger_phase(7)
        else:
            self.defense.cpu += 15
            await self.type_out_lines([f"> {name} was clean. Attack continues."], delay=0.05)

    async def cmd_debug(self, args) -> None:
        name = await self.pick_file(args, "debug")
        if not name: return
        await self.type_out_lines([f"> Debugging {name}..."], delay=0.05)
        
        if name == self.defense.infected_file:
            await self.type_out_lines(["> Malicious process killed."], delay=0.05)
            self.defense.end_attack()
        else:
            self.defense.cpu += 15
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
            self.defense.cpu += 15
            await self.type_out_lines([f"> {name} was clean. Attack continues."], delay=0.05)

    async def vitals_tick(self) -> None:
        crashed, msg = self.defense.tick()
        if msg: 
            await self.type_out_lines(msg.split('\n'), delay=0.05)
            
        if crashed:
            self.defense.game_active = False
            if getattr(self, "vitals_timer", None): self.vitals_timer.stop()
            self.update_status_display()
            await self.type_out_lines(["\n=== SYSTEM OVERLOAD. FLATLINE ==="], delay=0.1)

    async def cmd_rotate(self, args) -> None:
        if self.director.current_phase == 5:
            # INSTANT WRITE: Do not use type_out_lines for grid manipulation
            grid = self.pipeline.rotate_pipe(args)
            if isinstance(grid, list):
                for line in grid: self.stage.write(line)
            else:
                self.stage.write(grid)

    async def cmd_transmit(self) -> None:
        if self.director.current_phase == 5:
            success, message = self.pipeline.check_transmission()
            
            # INSTANT WRITE
            if isinstance(message, list):
                for line in message: self.stage.write(line)
            else:
                self.stage.write(message)
                
            if success:
                await self.trigger_phase(6)
            else:
                await self.type_out_lines(["\n[PLACEHOLDER] Transmission failed."], delay=0.05)
                await self.trigger_phase(5)

    async def cmd_jump(self, args) -> None:
        if args: await self.trigger_phase(int(args[0]))

if __name__ == "__main__":
    app = VirusGame()
    app.run()