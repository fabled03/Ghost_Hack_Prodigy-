import asyncio
import copy
import os
import random
import re

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, RichLog, Static

from Attack_gameplay import DataPipelineGame, check_file_access
from Defend_gameplay import ATTACKER_LINES, DefenseGame
from director import DialogueManager, StoryDirector
from file_tree import AI_FILE, AI_FILE_NAME, BLUEPRINT_FILES, FILE_TREE

ASCII_TITLE = r"""
  ____ _               _   _   _            _
 / ___| |__   ___  ___| |_| | | | __ _  ___| | __
| |  _| '_ \ / _ \/ __| __| |_| |/ _` |/ __| |/ /
| |_| | | | | (_) \__ \ |_|  _  | (_| | (__|   <
 \____|_| |_|\___/|___/\__|_| |_|\__,_|\___|_|\_\
 
 :: PRODIGY OS v0.6.7 :: UNAUTHORIZED ACCESS FATAL ::
"""
 
PROMPT = "> root@system:~# "
TRAINING_FENCE = "> [ACCESS DENIED] Finish your training first: 'open' every file in /tutorial."
CHOICE_INPUT = re.compile(r"[\[\(#\s]*\d+[\]\)\.\s:]*")  # "1", "1.", "[1]", "(1)", "#1"
def find_dialogue_file() -> str:
    """dialogue_tree.json next to main.py; failing that, any .json there that has "file_triggers"."""
    here = os.path.dirname(os.path.abspath(__file__))
    wanted = os.path.join(here, "dialogue_tree.json")
    if os.path.exists(wanted):
        return wanted
    for name in sorted(os.listdir(here)):
        if name.lower().endswith(".json"):
            try:
                with open(os.path.join(here, name), encoding="utf-8") as f:
                    if "file_triggers" in f.read():
                        return os.path.join(here, name)
            except OSError:
                pass
    return wanted
 
 
DIALOGUE_FILE = find_dialogue_file()
 
TUTORIAL_PATH = ["tutorial"]
HOME_PATH = ["home", "operator"]      # what "~" means
RISK_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
FILE_THRESHOLD = 20                   # unique files to open before the blueprints appear
ENDGAME_ATTACK_GAP = 12               # seconds between attacks during the final minigame
 
# The only commands the tutorial files teach. `help` lists exactly these.
TUTORIAL_COMMANDS = ["ls", "tree", "cd", "open", "inspect", "scan", "encrypt", "delete", "help", "manual"]
 
# Story commands the game prompts for itself when they matter (the jack-in prompt,
# the pipeline grid, the blueprint alert). They work but are not listed by `help`.
STORY_COMMANDS = ["connect", "rotate", "transmit", "copy"]
 
# Developer shortcuts (`clear`, `jump <phase>`). Switch on while testing.
DEBUG_COMMANDS = False
 
# Commands usable before the neural link is established
PRE_LINK_COMMANDS = {"connect", "help"} | ({"clear", "jump"} if DEBUG_COMMANDS else set())
 
# phase -> (message, commands that still work). Everything else is refused in that phase.
PHASE_LOCKS = {
    4: ("> [ERROR] ACCESS DENIED BY SYSTEM AI.", {"rotate", "transmit", "jump"}),
    8: ("> [ERROR] SYSTEM OVERLOAD. STAND BY.", {"jump"}),
}
 
 
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
 
    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
 
    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self.stage = self.query_one("#stage_view", RichLog)
 
        self.command_map = {
            "help": self.cmd_help,
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "tree": self.cmd_tree,
            "open": self.cmd_open,
            "inspect": self.cmd_inspect,
            "scan": self.cmd_scan,
            "manual": self.cmd_manual,
            "encrypt": self.cmd_encrypt,
            "delete": self.cmd_delete,
            "connect": self.cmd_connect,
            "copy": self.cmd_copy,
            "rotate": self.cmd_rotate,
            "transmit": self.cmd_transmit,
        }
        if DEBUG_COMMANDS:
            self.command_map["clear"] = self.cmd_clear
            self.command_map["jump"] = self.cmd_jump
 
        self.run_id = 0
        self.vitals_timer = None
        self.new_game()
        self.set_interval(1.0, self.update_status_display)
 
    def new_game(self) -> None:
        """Reset everything and start the boot sequence. Also used by `restart`."""
        self.run_id += 1
        self.stop_vitals_timer()
        self.stage.clear()
 
        self.director = StoryDirector()
        self.defense = DefenseGame()
        self.pipeline = DataPipelineGame()
        self.dialogue = DialogueManager(DIALOGUE_FILE)
 
        # The mainframe. A copy, so the AI file and blueprints never touch FILE_TREE itself.
        self.fs = copy.deepcopy(FILE_TREE)
        self.cwd = []
 
        self.tutorial_read = set()
        self.decrypted = set()          # encrypted files the player has already breached
        self.pending_dialogues = []     # conversations waiting for an attack or breach to finish
        self.pending_notice = False     # "incoming transmission" already shown for the waiting chat
        self.sprung = set()             # unsafe files that have already attacked
        self.pending_decrypt = None     # (command, absolute path) waiting on the pipeline minigame
        self.end_game_active = False
        self.read_blueprints = set()
        self.copied_blueprints = set()
        self.game_over = False
 
        self.update_status_display()
        self.set_timer(1.0, self.boot_step_1)
        self.set_timer(3.5, self.boot_step_2)
 
    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------
 
    async def type_out_lines(self, lines: list, delay: float = 0.05) -> None:
        for line in lines:
            self.stage.write(line)
            await asyncio.sleep(delay)
 
    def show(self, content) -> None:
        """Write a renderable (or a list of them) to the stage."""
        if isinstance(content, list):
            for line in content:
                self.stage.write(line)
        else:
            self.stage.write(content)
 
    def schedule(self, delay: float, action) -> None:
        """Run `await action()` after `delay` seconds, unless the game ended or restarted meanwhile."""
        run_id = self.run_id
 
        async def fire():
            if run_id == self.run_id and not self.game_over:
                await action()
 
        self.set_timer(delay, fire)
 
    # ------------------------------------------------------------------
    # Boot sequence
    # ------------------------------------------------------------------
 
    async def boot_step_1(self):
        if self.director.tutorial_step != 0:  # `jump` already skipped the boot
            return
        await self.type_out_lines(self.director.advance_tutorial(1), delay=0.15)
 
    async def boot_step_2(self):
        if self.director.tutorial_step != 1:
            return
        self.stage.clear()
        self.stage.write(ASCII_TITLE)
        await self.type_out_lines(self.director.advance_tutorial(2), delay=0.15)
        self.update_status_display()
 
    async def boot_step_3(self):
        # Link established: mount the player in the tutorial folder from the file tree
        self.cwd = list(TUTORIAL_PATH)
        await self.type_out_lines(self.director.advance_tutorial(4), delay=0.15)
        problems = self.dialogue.problems()
        if problems:  # a working dialogue file prints nothing here
            await self.type_out_lines(["", "> [DIALOGUE FILE] conversations will not work until this is fixed:"]
                                      + [f">   - {p}" for p in problems], delay=0.05)
        else:
            await self.type_out_lines(
                [f"> [DIALOGUE] loaded {os.path.basename(DIALOGUE_FILE)}: {len(self.dialogue.triggers)} conversations ready."], delay=0.05)
        self.update_status_display()
 
    # ------------------------------------------------------------------
    # Phases
    # ------------------------------------------------------------------
 
    async def trigger_phase(self, phase: int):
        # Prevent double-triggering if we are already on this phase
        if self.director.current_phase == phase and phase in (10, 13):
            return
 
        await self.type_out_lines(self.director.get_phase_text(phase), delay=0.1)
 
        if phase == 5:
            self.pending_decrypt = None
            self.show(self.pipeline.start_game())
 
        elif phase == 6:
            await self.start_defense()
 
        elif phase == 7:
            # Conversation -> system overload after a short pause
            self.schedule(4.0, lambda: self.trigger_phase(8))
 
        elif phase == 8:
            # Vitals spike with no attack running, then the second defense begins
            self.defense.cpu = max(self.defense.cpu, 45)
            self.defense.ram = max(self.defense.ram, 6.0)
            self.defense.bpm = max(self.defense.bpm, 120)
            self.start_vitals_timer()
            self.schedule(8.0, lambda: self.trigger_phase(9))
 
        elif phase == 9:
            await self.start_defense()
 
        elif phase == 10:
            # Free exploration: the 20-file counter drives the end game
            await self.check_endgame()
 
        elif phase == 11:
            await self.materialize_blueprints()
            await self.trigger_phase(12)
 
        elif phase == 12:
            self.end_game_active = True
            await self.start_defense()
 
        elif phase == 13:
            await self.win()
 
    def sync_vitals(self) -> None:
        self.director.heartbeat = int(self.defense.bpm)
        self.director.cpu = int(self.defense.cpu)
        self.director.ram_used = self.defense.ram
 
    def update_status_display(self) -> None:
        if self.defense.game_active:
            self.sync_vitals()
 
        self.status_text = self.director.get_status_text(
            game_active=self.defense.game_active,
            defense_state=self.defense,
        )
        self.query_one("#status_view", Status).update(self.status_text)
 
    # ------------------------------------------------------------------
    # Defense
    # ------------------------------------------------------------------
 
    def in_attack(self) -> bool:
        return self.defense.active_attack is not None
 
    def start_vitals_timer(self) -> None:
        self.defense.game_active = True
        if self.vitals_timer is None:
            self.vitals_timer = self.set_interval(1.0, self.vitals_tick)
 
    def stop_vitals_timer(self) -> None:
        if self.vitals_timer is not None:
            self.vitals_timer.stop()
            self.vitals_timer = None
 
    async def start_defense(self) -> None:
        self.start_vitals_timer()
        await self.type_out_lines(self.defense.launch_attack().split("\n"), delay=0.05)
 
    async def clear_attack(self) -> None:
        """The infection source is gone: end the attack and move the story on."""
        self.defense.end_attack()
        phase = self.director.current_phase
        if phase == 6:
            await self.trigger_phase(7)
        elif phase == 9:
            await self.trigger_phase(10)
        elif phase == 12:
            self.schedule(ENDGAME_ATTACK_GAP, self.relaunch_endgame_attack)
        await self.flush_pending_dialogue()
 
    async def relaunch_endgame_attack(self) -> None:
        if self.director.current_phase == 12 and not self.in_attack():
            await self.start_defense()
 
    async def vitals_tick(self) -> None:
        if self.game_over:
            return
 
        crashed, msg = self.defense.tick()
        if msg:
            await self.type_out_lines(msg.split("\n"), delay=0.05)
 
        if crashed:
            await self.game_over_screen([], flatline=True)
        elif not self.in_attack() and self.defense.at_baseline():
            # Vitals have settled after an attack or spike
            self.sync_vitals()
            self.defense.game_active = False
            self.stop_vitals_timer()
 
    async def game_over_screen(self, lines: list, flatline: bool) -> None:
        self.game_over = True
        self.stop_vitals_timer()
        self.defense.game_active = False
        self.defense.end_attack()
        if flatline:
            self.director.heartbeat = 0
        self.update_status_display()
        await self.type_out_lines(lines + ["", "> Type 'restart' to reconnect."], delay=0.1)
 
    async def win(self) -> None:
        self.defense.end_attack()
        self.stop_vitals_timer()
        self.defense.game_active = False
        self.update_status_display()
        await self.type_out_lines([
            "==================================================",
            "[+] Objective achieved.",
            "[+] Jacking out now.",
            "==================================================",
            "",
            "> Session complete. Type 'restart' to play again.",
        ], delay=0.1)
        self.game_over = True
 
    # ------------------------------------------------------------------
    # End game
    # ------------------------------------------------------------------
 
    def find_blueprint(self, name: str):
        for key in BLUEPRINT_FILES:
            if key.lower() == name.lower():
                return key
        return None
 
    async def check_endgame(self) -> None:
        if (
            self.director.current_phase == 10
            and not self.end_game_active
            and len(self.dialogue.opened_files) >= FILE_THRESHOLD
        ):
            await self.trigger_phase(11)
 
    async def materialize_blueprints(self) -> None:
        self.end_game_active = True
 
        # Put the blueprints in ~ so `ls` shows them and `open` can read them
        home = self.fs["home"]["operator"]
        for name, data in BLUEPRINT_FILES.items():
            home[name] = {"type": "file", "risk": data["risk"], "info": data["info"], "blueprint": True}
 
        await self.type_out_lines([
            "\n==================================================",
            "[!] CRITICAL ALERT: I have what you are looking for now.",
            "[!] BLUEPRINT FILES HAVE MATERIALIZED IN THE DIRECTORY.",
            "[!] Lets see if you can still get out intacted...",
            "==================================================\n",
            "> Use 'open <file>' to read each blueprint, then 'copy <file>' to take it.",
        ], delay=0.05)
 
    async def check_win(self) -> None:
        total = len(BLUEPRINT_FILES)
        if (
            self.end_game_active
            and len(self.read_blueprints) == total
            and len(self.copied_blueprints) == total
        ):
            await self.trigger_phase(13)
 
    # ------------------------------------------------------------------
    # Filesystem helpers (the mainframe tree, self.fs)
    # ------------------------------------------------------------------
 
    @staticmethod
    def is_file(node) -> bool:
        return isinstance(node, dict) and node.get("type") == "file"
 
    def folder_at(self, path):
        """The folder dict at `path`, or None if it doesn't exist or is a file."""
        node = self.fs
        for part in path:
            node = node.get(part)
            if not isinstance(node, dict) or self.is_file(node):
                return None
        return node
 
    def node_at(self, path):
        if not path:
            return self.fs
        parent = self.folder_at(path[:-1])
        return parent.get(path[-1]) if parent is not None else None
 
    @staticmethod
    def match_name(folder: dict, name: str):
        """Exact name first, otherwise a unique case-insensitive match."""
        if name in folder:
            return name
        matches = [key for key in folder if key.lower() == name.lower()]
        return matches[0] if len(matches) == 1 else None
 
    def resolve(self, raw: str):
        """Turn what the player typed into an absolute path (list of names), or None if it doesn't exist."""
        raw = raw.replace("\\", "/")
        if raw == "~" or raw.startswith("~/"):
            path, raw = list(HOME_PATH), raw[2:]
        elif raw.startswith("/"):
            path = []
        else:
            path = list(self.cwd)
 
        for part in raw.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                path = path[:-1]
                continue
            folder = self.folder_at(path)
            if folder is None:
                return None
            key = self.match_name(folder, part)
            if key is None:
                return None
            path.append(key)
        return path
 
    def is_off_limits(self, path) -> bool:
        """During training (phase 1) the player is kept to /tutorial. Reading every file there lifts it."""
        if self.director.current_phase != 1:
            return False
        return path[:1] != TUTORIAL_PATH
 
    def find_folder_by_name(self, name: str):
        """Absolute path of the only folder called `name` anywhere in the mainframe, else None."""
        hits = []
 
        def walk(node, path):
            for key, val in node.items():
                if isinstance(val, dict) and not self.is_file(val):
                    if key.lower() == name.lower():
                        hits.append(path + [key])
                    walk(val, path + [key])
 
        walk(self.fs, [])
        return hits[0] if len(hits) == 1 else None
 
    async def locate_folder(self, args):
        """Resolve an optional folder argument. Returns (path, folder), or (None, None) after explaining why."""
        raw = args[0] if args else None
        path = self.resolve(raw) if raw else list(self.cwd)
        folder = self.folder_at(path) if path is not None else None
        if folder is None and raw and "/" not in raw and raw not in ("~", ".", ".."):
            # `cd images` from /home/operator: find the folder by name instead of leaving the player lost
            path = self.find_folder_by_name(raw)
            folder = self.folder_at(path) if path is not None else None
        if folder is None:
            await self.type_out_lines([f"> Directory not found: {raw}"], delay=0.05)
            return None, None
        if self.is_off_limits(path):
            await self.type_out_lines([TRAINING_FENCE], delay=0.05)
            return None, None
        return path, folder
 
    @staticmethod
    def risk_list_lines(title: str, items: list) -> list:
        """items: [(file name, risk level)]. A risk level per file, then how many of each."""
        lines = [f"> RISK LEVELS: {title}"]
        if not items:
            return lines + ["> No files here."]
        width = max(len(name) for name, _ in items)
        lines += [f">   {name.ljust(width)}  {risk}" for name, risk in items]
 
        counts = {}
        for _, risk in items:
            counts[risk] = counts.get(risk, 0) + 1
        order = RISK_ORDER + sorted(set(counts) - set(RISK_ORDER))
        lines.append("> " + "   ".join(f"{risk}: {counts[risk]}" for risk in order if risk in counts))
        return lines
 
    def tree_lines(self, folder: dict, prefix: str = "") -> list:
        entries = [(key, val) for key, val in folder.items() if isinstance(val, dict)]
        lines = []
        for idx, (key, val) in enumerate(entries):
            last = idx == len(entries) - 1
            is_dir = not self.is_file(val)
            lines.append(f"> {prefix}{'└── ' if last else '├── '}{key}{'/' if is_dir else ''}")
            if is_dir:
                lines += self.tree_lines(val, prefix + ("    " if last else "│   "))
        return lines
 
    def defense_listing(self) -> list:
        lines = ["> YOUR FILES:"]
        for name in self.defense.home_files:
            lines.append(f">   {name}   (/{self.defense.file_folder.get(name, '?')}/)")
        if self.end_game_active:
            lines += ["", "> BLUEPRINTS:"]
            for name in BLUEPRINT_FILES:
                state = "copied" if name in self.copied_blueprints else "read" if name in self.read_blueprints else "unread"
                lines.append(f">   {name}  [{state}]")
        return lines
 
    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------
 
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_input = event.value.strip()
        self.query_one(Input).value = ""
        if not raw_input:
            return
        self.stage.write(f"\n{PROMPT}{raw_input}")
 
        # Only the command is case-insensitive; file names keep their case
        parts = raw_input.split()
        base_command, args = parts[0].lower(), parts[1:]
 
        if self.game_over:
            if base_command == "restart":
                self.new_game()
            else:
                await self.type_out_lines(["> Session ended. Type 'restart' to reconnect."], delay=0.05)
            return
 
        if self.dialogue.active:
            busy = self.in_attack() or self.pipeline.game_active
            if not busy or CHOICE_INPUT.fullmatch(raw_input):
                await self.type_out_lines(self.dialogue.choose(raw_input), delay=0.05)
                await self.flush_pending_dialogue()
                return
            # an attack or breach is running: let the player's command through, the chat can wait
 
        if self.director.tutorial_step < 4 and base_command not in PRE_LINK_COMMANDS:
            await self.type_out_lines(["> [ERROR] No neural link. Type 'connect' to jack in."], delay=0.05)
            return
 
        lock = PHASE_LOCKS.get(self.director.current_phase)
        if lock and base_command not in lock[1]:
            await self.type_out_lines([lock[0]], delay=0.05)
            return
 
        handler = self.command_map.get(base_command)
        if handler is None:
            await self.type_out_lines(["> COMMAND NOT RECOGNIZED."], delay=0.05)
        else:
            await handler(args)
 
    # ------------------------------------------------------------------
    # General commands
    # ------------------------------------------------------------------
 
    async def cmd_clear(self, args) -> None:
        self.stage.clear()
 
    async def cmd_connect(self, args) -> None:
        step = self.director.tutorial_step
        if step == 2:
            await self.type_out_lines(self.director.advance_tutorial(3), delay=0.15)
            self.update_status_display()
            self.set_timer(2.0, self.boot_step_3)
        elif step < 2:
            await self.type_out_lines(["> Neural interface still initializing..."], delay=0.05)
        else:
            await self.type_out_lines(["> ERROR: Neural link already established."], delay=0.05)
 
    async def cmd_help(self, args) -> None:
        available_commands = ", ".join(TUTORIAL_COMMANDS)
        await self.type_out_lines([f"> Available modules: [ {available_commands} ]"], delay=0.05)
 
    async def cmd_manual(self, args) -> None:
        text = self.fs.get("tutorial", {}).get("03_defending.txt", {}).get("text", "")
        await self.type_out_lines(["> DEFENSE REMINDERS"] + text.strip("\n").split("\n"), delay=0.03)
 
    async def cmd_jump(self, args) -> None:
        if not args or not args[0].isdigit() or not 1 <= int(args[0]) <= 13:
            await self.type_out_lines(["> Usage: jump <1-13>"], delay=0.05)
            return
        if self.director.tutorial_step < 4:
            # Debug shortcut: skip the boot sequence
            self.director.tutorial_step = 4
            self.cwd = list(HOME_PATH)
        await self.trigger_phase(int(args[0]))
 
    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
 
    async def cmd_ls(self, args) -> None:
        if self.in_attack():
            await self.type_out_lines(self.defense_listing(), delay=0.05)
            return
 
        path, folder = await self.locate_folder(args)
        if folder is None:
            return
 
        output = [f"> /{'/'.join(path)}:"]
        if path:
            output.append(">   [DIR] ../")
        for key, val in folder.items():
            if not isinstance(val, dict):
                continue
            if self.is_file(val):
                tag = "  (read)" if val.get("tutorial") and key in self.tutorial_read else ""
                output.append(f">   {key}{tag}")
            else:
                output.append(f">   [DIR] {key}/")
 
        await self.type_out_lines(output, delay=0.05)
 
    async def cmd_cd(self, args) -> None:
        if self.in_attack():
            await self.type_out_lines(["> Cannot change directory while under attack."], delay=0.05)
            return
 
        path, folder = await self.locate_folder(args or ["~"])
        if folder is None:
            return
        self.cwd = path
        await self.type_out_lines([f"> /{'/'.join(path)}"], delay=0.05)
 
    async def cmd_tree(self, args) -> None:
        if self.in_attack():
            await self.type_out_lines(self.defense_listing(), delay=0.05)
            return
 
        path, folder = await self.locate_folder(args)
        if folder is None:
            return
        await self.type_out_lines([f"> /{'/'.join(path)}"] + self.tree_lines(folder), delay=0.02)
 
    async def cmd_scan(self, args) -> None:
        if self.in_attack():
            await self.type_out_lines([
                f"> SCAN: infection detected in /{self.defense.file_folder.get(self.defense.infected_file, self.defense.current_folder_name)}/",
                f"> Threat: {self.defense.active_attack['name']}",
                "> Use 'ls' to list the folder and 'inspect <file>' to find the source.",
            ], delay=0.05)
            return
 
        # No attack running: scan for encryption. Locked files need the pipeline
        # minigame (`open` them) before they can be read, so scanning lets you prepare.
        if args:
            file_path = self.resolve(args[0])
            file_node = self.node_at(file_path) if file_path is not None else None
            if self.is_file(file_node):
                await self.scan_file(file_path, file_node)
                return
 
        path, folder = await self.locate_folder(args)
        if folder is None:
            return
 
        lines = [f"> SCAN: /{'/'.join(path)}"]
        locked = 0
        for name, node in folder.items():
            if not self.is_file(node):
                continue
            if not node.get("Encrypted"):
                state = "not encrypted"
            elif "/" + "/".join(path + [name]) in self.decrypted:
                state = "ENCRYPTED - breached"
            else:
                state = "ENCRYPTED - locked"
                locked += 1
            lines.append(f">   {name}  [{state}]")
 
        if len(lines) == 1:
            lines.append("> No files here.")
        elif locked:
            lines.append(f"> {locked} locked file(s). 'open <file>' starts a data breach.")
        else:
            lines.append("> No locked files here.")
        await self.type_out_lines(lines, delay=0.05)
 
    async def scan_file(self, path: list, node: dict) -> None:
        """`scan <file>`: say whether it is encrypted, so the player can prepare for a data breach."""
        if self.is_off_limits(path):
            await self.type_out_lines([TRAINING_FENCE], delay=0.05)
            return
 
        key = "/" + "/".join(path)
        lines = [f"> SCAN: {key}"]
        if not node.get("Encrypted"):
            lines += [">   Encryption : none", "> Not encrypted. 'open' reads it straight away."]
        elif key in self.decrypted:
            lines += [">   Encryption : ENCRYPTED - already breached", "> You broke this one already. 'open' reads it."]
        else:
            lines += [
                ">   Encryption : ENCRYPTED - locked",
                "> Prepare for a data breach: 'open' starts the pipeline puzzle.",
                "> Connect the start (green) to the finish (magenta) with 'rotate <row> <col>', then 'transmit'.",
            ]
        await self.type_out_lines(lines, delay=0.05)
 
    # ------------------------------------------------------------------
    # Reading files
    # ------------------------------------------------------------------
 
    async def cmd_open(self, args) -> None:
        await self.access_file(args, "open")
 
    async def cmd_inspect(self, args) -> None:
        await self.access_file(args, "inspect")
 
    async def access_file(self, args, mode: str) -> None:
        """Shared by `open` and `inspect`: blueprints, files under attack, then the mainframe."""
        if not args:
            if mode != "inspect":
                await self.type_out_lines([f"> Usage: {mode} <filename>"], delay=0.05)
            elif self.in_attack():
                items = [(n, self.defense.file_data.get(n, {}).get("risk", "LOW")) for n in self.defense.home_files]
                await self.type_out_lines(self.risk_list_lines("your files", items), delay=0.05)
            else:
                await self.read_file("", mode)  # inspect with no file: risk levels for this folder
            return
 
        name = args[0]
        blueprint = self.find_blueprint(name)
 
        # Blueprints only exist once the end game has started
        if blueprint and self.end_game_active:
            await self.inspect_blueprint(blueprint, mode)
            return
        if blueprint:
            await self.type_out_lines([f"> File not found: {name}"], delay=0.05)
            return
 
        if self.in_attack():
            await self.inspect_defense_file(name, mode)
            return
 
        await self.read_file(name, mode)
 
    async def inspect_defense_file(self, name: str, mode: str) -> None:
        """During an attack: `inspect` gives risk level and the infection verdict, `open` gives the file's info."""
        if name not in self.defense.home_files:
            await self.type_out_lines([f"> File not found: {name}"], delay=0.05)
            return
 
        data = self.defense.file_data.get(name, {})
        if mode == "open":
            lines = [f"\n> {name}", f"> {data.get('info', '')}"]
            art = data.get("ASCII")
            if art:
                lines += str(art).split("\n")
        else:
            self.defense.inspected.add(name)
            lines = [f"> INSPECT: {name}", f">   Risk level  : {data.get('risk', 'LOW')}"]
            if name == self.defense.infected_file:
                lines.append(">   Source scan : HIDDEN PROCESS. Infection source.")
            else:
                lines.append(">   Source scan : clean.")
        await self.type_out_lines(lines, delay=0.05)
 
    async def inspect_blueprint(self, name: str, mode: str) -> None:
        """`inspect` shows a blueprint's risk level; `open` shows its info and counts it as read."""
        data = BLUEPRINT_FILES[name]
        if mode == "inspect":
            await self.type_out_lines([
                f"> INSPECT: {name}",
                f">   Risk level  : {data['risk']}",
                f">   Type        : {data['type']}",
            ], delay=0.05)
        elif name in self.read_blueprints:
            await self.type_out_lines([f"> {name} (Already Read): {data['info']}"], delay=0.05)
        else:
            self.read_blueprints.add(name)
            await self.type_out_lines([
                f"\n=== READING BLUEPRINT: {name} ===",
                f"> Info: {data['info']}",
                f"> Read Progress: [{len(self.read_blueprints)}/{len(BLUEPRINT_FILES)} blueprints read]\n",
            ], delay=0.05)
        await self.check_win()
 
    @staticmethod
    def art_lines(node: dict) -> list:
        """The file's ASCII picture (its "ASCII" key), as extra lines after `open`."""
        art = node.get("ASCII")
        return [""] + str(art).strip("\n").split("\n") if art else []
 
    async def read_file(self, raw: str, mode: str) -> None:
        """Outside of attacks: `open` shows a file's contents (info), `inspect` shows only its risk level."""
        path = self.resolve(raw) if raw else list(self.cwd)
        if path is not None and self.is_off_limits(path):
            await self.type_out_lines([TRAINING_FENCE], delay=0.05)
            return
 
        node = self.node_at(path) if path is not None else None
        if path is not None and self.folder_at(path) is not None:
            if mode == "inspect":  # a folder: list the risk level of everything in it
                folder = self.folder_at(path)
                items = [(k, v.get("risk", "LOW")) for k, v in folder.items() if self.is_file(v)]
                await self.type_out_lines(self.risk_list_lines("/" + "/".join(path), items), delay=0.05)
            else:
                await self.type_out_lines([f"> {raw} is a folder. Use 'ls' or 'cd'."], delay=0.05)
            return
        if not self.is_file(node):
            await self.type_out_lines([f"> File not found: {raw}"], delay=0.05)
            return
 
        name = path[-1]
        key = "/" + "/".join(path)
        info = node.get("info", "")
 
        if node.get("blueprint"):
            await self.inspect_blueprint(name, mode)
            return
 
        # Story trigger: the file the whole plot hangs on
        if name == "disease.png" and self.director.current_phase == 2:
            if mode == "open":
                await self.type_out_lines([f"> {name}: {info}"] + self.art_lines(node), delay=0.05)
            else:
                await self.type_out_lines([f"> {name}: risk level {node.get('risk', 'LOW')}"], delay=0.05)
            await asyncio.sleep(1)
            await self.trigger_phase(3)
            await self.trigger_phase(4)
            await self.trigger_phase(5)
            return
 
        # Encrypted files have to be breached with the pipeline minigame first
        if mode == "open" and node.get("Encrypted") and key not in self.decrypted:
            await self.begin_breach(mode, self.folder_at(path[:-1]), name, key)
            return
 
        if mode == "open":
            body = (node.get("text") or info).strip("\n").split("\n")
            await self.type_out_lines([f"\n> {name}"] + body + self.art_lines(node), delay=0.15 if node.get("ai") else 0.04)
        else:
            lines = [
                f"> INSPECT: {name}",
                f">   Risk level  : {node.get('risk', 'LOW')}",
            ]
            if node.get("safe") is False:
                lines.append(">   Virus check : UNSAFE - opening it could trigger an attack")
            elif node.get("safe") is True:
                lines.append(">   Virus check : no threats found")
            if node.get("tutorial"):
                lines.append("> Use 'open <file>' to read it.")
            await self.type_out_lines(lines, delay=0.05)
 
        if node.get("tutorial"):
            if mode == "open":
                await self.mark_tutorial_read(name)
        elif node.get("ai"):
            pass
        else:
            if mode == "open":  # only opening a file counts toward the blueprint unlock
                await self.register_read(key)
            await self.spring_trap(name, key, node, mode)
            await self.flush_pending_dialogue()  # after the trap, so a chat never opens over an attack
 
    async def spring_trap(self, name: str, key: str, node: dict, mode: str) -> None:
        """Opening a file marked `"safe": False` unleashes an attack (once per file, during free exploration)."""
        if (
            mode != "open"
            or node.get("safe") is not False
            or key in self.sprung
            or self.director.current_phase not in (2, 10)
            or self.in_attack()
            or self.pipeline.game_active
        ):
            return
        self.sprung.add(key)
        await self.type_out_lines([f"\n[!] {name} EXECUTED A HIDDEN PAYLOAD."], delay=0.1)
        await self.start_defense()
 
    async def mark_tutorial_read(self, name: str) -> None:
        self.tutorial_read.add(name)
        total = sum(1 for node in self.fs["tutorial"].values() if node.get("tutorial"))
        await self.type_out_lines([f"> [ training files read: {len(self.tutorial_read)}/{total} ]"], delay=0.05)
 
        home = self.fs["home"]["operator"]
        if len(self.tutorial_read) >= total and AI_FILE_NAME not in home:
            home[AI_FILE_NAME] = copy.deepcopy(AI_FILE)
            await self.type_out_lines([
                "",
                f"> [!] UNREGISTERED FILE DETECTED IN ~ : {AI_FILE_NAME}",
                f"> Use 'cd ~' then 'open {AI_FILE_NAME}'.",
            ], delay=0.1)
            await self.trigger_phase(2)  # training done: the whole mainframe is open
            await self.type_out_lines([
                "> [SYSTEM AI]: 'tree /' maps the whole mainframe. 'cd <folder>' moves you around and 'cd ..' goes up.",
            ], delay=0.05)
 
    async def register_read(self, key: str) -> None:
        """Count a unique file toward the end-game threshold and fire any dialogue it unlocks."""
        trigger = self.dialogue.record_file_opened(key)
        if self.director.current_phase >= 2:
            await self.type_out_lines(
                [f"> [ files opened: {len(self.dialogue.opened_files)}/{FILE_THRESHOLD} ]"], delay=0.05
            )
        if trigger:
            self.pending_dialogues.append(trigger)
        await self.check_endgame()
 
    async def flush_pending_dialogue(self) -> None:
        """Start the next waiting conversation, but never over an attack, a breach or another chat."""
        if not self.pending_dialogues or self.dialogue.active or self.game_over:
            return
        if self.in_attack() or self.pipeline.game_active:
            if not self.pending_notice:  # say it once, so a waiting chat never looks like a missing one
                self.pending_notice = True
                await self.type_out_lines(["> [ incoming transmission - deal with this first ]"], delay=0.05)
            return
        self.pending_notice = False
        lines = self.dialogue.start_dialogue(self.pending_dialogues.pop(0))
        await self.type_out_lines(lines, delay=0.05)
        if not lines:  # that trigger had no usable node: try the next one
            await self.flush_pending_dialogue()
 
    # ------------------------------------------------------------------
    # Encrypted files (pipeline minigame)
    # ------------------------------------------------------------------
 
    async def begin_breach(self, command: str, folder: dict, name: str, key: str) -> None:
        if self.pipeline.game_active:
            await self.type_out_lines(["> A data breach is already running. Finish it with 'transmit' first."], delay=0.05)
            return
 
        result = check_file_access(folder, name, self.pipeline)
        self.pending_decrypt = (command, key)
        await self.type_out_lines(result["messages"], delay=0.05)
        self.show(result["display"])
 
    async def finish_breach(self) -> None:
        if self.director.current_phase == 5:
            await self.trigger_phase(6)
        elif self.pending_decrypt:
            command, key = self.pending_decrypt
            self.pending_decrypt = None
            self.decrypted.add(key)
            await self.type_out_lines([f"> Decryption complete: {key}"], delay=0.05)
            await self.command_map[command]([key])
            await self.flush_pending_dialogue()
 
    async def cmd_rotate(self, args) -> None:
        self.show(self.pipeline.rotate_pipe(args))
 
    async def cmd_transmit(self, args) -> None:
        success, message = self.pipeline.check_transmission()
        self.show(message)
 
        if success:
            await self.finish_breach()
        elif self.pipeline.game_active:
            await self.type_out_lines(["\n> Transmission failed. Keep rotating."], delay=0.05)
 
    # ------------------------------------------------------------------
    # Defense commands
    # ------------------------------------------------------------------
 
    async def pick_file(self, args, verb):
        if not self.in_attack():
            await self.type_out_lines([f"> No active attack. Nothing to {verb}."], delay=0.05)
            return None
        if not args:
            await self.type_out_lines([f"> Usage: {verb} <filename>"], delay=0.05)
            return None
        if args[0] not in self.defense.home_files:
            await self.type_out_lines([f"> File not found: {args[0]}"], delay=0.05)
            return None
        return args[0]
 
    async def cmd_encrypt(self, args) -> None:
        name = await self.pick_file(args, "encrypt")
        if not name:
            return
        await self.type_out_lines([f"> Encrypting {name}..."], delay=0.05)
        await asyncio.sleep(1.5)  # Encrypting takes time, as the training file promises
 
        if not self.in_attack():  # the attack ended (or the game did) while encrypting
            return
 
        if name == self.defense.infected_file:
            self.defense.firewalls += 1
            await self.type_out_lines([
                f"> Encryption complete. Firewall #{self.defense.firewalls} online.",
                random.choice(ATTACKER_LINES),
            ], delay=0.05)
            await self.clear_attack()
        else:
            self.defense.cpu += 5
            await self.type_out_lines([f"> {name} was clean. Attack continues."], delay=0.05)
 
    async def cmd_delete(self, args) -> None:
        name = await self.pick_file(args, "delete")
        if not name:
            return
        self.defense.home_files.remove(name)
        self.defense.deleted.append(name)
        await self.type_out_lines([f"> {name} deleted permanently."], delay=0.05)
 
        taken_over, lines = self.defense.check_takeover()
        if taken_over:
            await self.game_over_screen(lines, flatline=False)
            return
        if lines:
            await self.type_out_lines(lines, delay=0.05)
 
        if name == self.defense.infected_file:
            await self.type_out_lines(["> Infection source destroyed."], delay=0.05)
            await self.clear_attack()
        else:
            self.defense.cpu += 5
            await self.type_out_lines([f"> {name} was clean. Attack continues."], delay=0.05)
 
    async def cmd_copy(self, args) -> None:
        if not args:
            await self.type_out_lines(["> Usage: copy <filename>"], delay=0.05)
            return
 
        name = self.find_blueprint(args[0]) if self.end_game_active else None
        if name is None:
            await self.type_out_lines([f"> Nothing to copy: {args[0]}"], delay=0.05)
            return
 
        if name in self.copied_blueprints:
            await self.type_out_lines([f"> {name} is already copied."], delay=0.05)
        else:
            self.copied_blueprints.add(name)
            await self.type_out_lines([
                f"> Copying {name}... done.",
                f"> Copy Progress: [{len(self.copied_blueprints)}/{len(BLUEPRINT_FILES)} blueprints copied]",
            ], delay=0.05)
        await self.check_win()
 
 
if __name__ == "__main__":
    app = VirusGame()
    app.run()