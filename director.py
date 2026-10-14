import getpass
import json
import re

from Defend_gameplay import bar

HEART_BAR_MAX = 180  # the heart bar fills up at the heart rate that flatlines you

PLAYER_SPEAKER = "YOU"  # who speaks an option's "reply" when no speaker is given


def _safe_username() -> str:
    try:
        return getpass.getuser().upper()
    except Exception:
        return "OPERATOR"


class StoryDirector:
    def __init__(self):
        self.heartbeat = 0
        self.cpu = 2
        self.ram_used = 0.4
        self.ram_total = 16.0
        self.username = _safe_username()
        self.heart_pulse = False
        self.tutorial_step = 0
        self.current_phase = 1

    def get_status_text(self, game_active=False, defense_state=None) -> str:
        self.heart_pulse = not self.heart_pulse
        heart_icon = "♥" if self.heart_pulse else "♡"

        if not game_active:
            if self.heartbeat == 0:
                hb_display = "FLATLINE [ ♡ ]"
            else:
                hb_display = f"{self.heartbeat} BPM [ {heart_icon} ]"
            return (
                f"NEURAL SYNC STATUS:\n\n"
                f"CPU (CORTEX): {self.cpu}%\n"
                f"RAM (MEM_BUFFER): {self.ram_used:.1f}GB / {self.ram_total}GB\n"
                f"HEARTBEAT: {hb_display}\n\n"
                f"PHASE: {self.current_phase}/13"
            )

        threat = defense_state.active_attack["name"] if defense_state.active_attack else "NONE"
        return (
            f"SYSTEM STATUS:\n\n"
            f"CPU:   [{bar(defense_state.cpu, 100)}] {int(defense_state.cpu)}%\n"
            f"RAM:   [{bar(defense_state.ram, 16)}] {defense_state.ram:.1f}/16GB\n"
            f"HEART: [{bar(defense_state.bpm, HEART_BAR_MAX)}] {int(defense_state.bpm)} BPM [ {heart_icon} ]\n\n"
            f"THREAT: {threat}\n"
            f"FIREWALLS: {defense_state.firewalls}\n"
            f"PERMANENT DAMAGE: {defense_state.scars}\n"
            f"BASELINE: {int(defense_state.base_cpu)}% / {defense_state.base_ram:.1f}GB / {int(getattr(defense_state, "base_bpm", 72))} BPM\n"
            f"PHASE: {self.current_phase}/13"
        )

    def advance_tutorial(self, step: int) -> list[str]:
        self.tutorial_step = step
        if step == 1:
            return ["INITIALIZING BIOS...", "LOADING KERNEL... [OK]", "MOUNTING DRIVES... [OK]"]
        elif step == 2:
            return [
                "\n[FATAL ERROR]: NO NEURAL LINK DETECTED.",
                "> Physical connection required to access Esper Group internal servers.",
                "> Awaiting vascular port connection...",
                "\n[ ACTION REQUIRED ]: Type 'connect' to jack in.",
            ]
        elif step == 3:
            self.heartbeat = 65
            self.cpu = 12
            self.ram_used = 1.2
            return [
                "\n> Syringe engaged. Piercing skin...",
                "> Neural pathways syncing... [OK]",
                "> Biometrics detected. Vitals stable.",
            ]
        elif step == 4:
            return [
                "\n--- CONNECTION ESTABLISHED ---",
                f"\n[SYSTEM AI]: Biometric sync complete. Welcome, {self.username}.",
                "[SYSTEM AI]: I am the local system for Esper Group.",
                "[SYSTEM AI]: Primary diagnostics nominal. Terminal port connection secured.",
                "[SYSTEM AI]: How can I assist your session today, Operator?",
                "\n[SYSTEM AI]: Training files are mounted in /tutorial.",
                "[SYSTEM AI]: Type 'ls' to list them, then 'open <file>' to read each one.",
            ]
        return []

    def get_phase_text(self, phase: int) -> list[str]:
        self.current_phase = phase
        if phase == 2:
            return ["\n[PHASE 2] [SYSTEM AI]: Diagnostics complete. Use 'ls' to view directories and 'inspect <file>' to analyze."]
        elif phase == 3:
            return ["\n[PHASE 3] [DISCOVERY] The file is heavily encrypted and pulsing..."]
        elif phase == 4:
            return ["\n[PHASE 4] [SYSTEM AI]: WARNING. ACCESS RESTRICTED. SEVERING TERMINAL LINK IMMEDIATELY."]
        elif phase == 5:
            return ["\n[PHASE 5] [ATTACK TRIAL] Counter-measure deployed. Commencing Data Pipeline override..."]
        elif phase == 6:
            return ["\n[PHASE 6] [ESCALATION] Override successful. AI hostile. Defense protocol initiated!"]
        elif phase == 7:
            return ["\n[PHASE 7] [CONVERSATION] [SYSTEM AI]: Why are you doing this? I just... want to rest."]
        elif phase == 8:
            return ["\n[PHASE 8] [SYSTEM OVERLOAD] CPU spiking. Memory fragmentation detected..."]
        elif phase == 9:
            return ["\n[PHASE 9] [SECOND DEFENSE] The AI lashes out wildly. Brace for impact!"]
        elif phase == 10:
            return ["\n[PHASE 10] [FREE EXPLORATION] AI presence suppressed. Local files unlocked."]
        elif phase == 11:
            return ["\n[PHASE 11] [FINAL DIALOGUE] The AI re-establishes connection. The truth comes out."]
        elif phase == 12:
            return ["\n[PHASE 12] [FINAL MINIGAME] Diving into the core datastream..."]
        elif phase == 13:
            return ["\n[PHASE 13] [VICTORY] Project Lazarus secured. The Ghost is free."]
        return []


class DialogueManager:
    """
    Branching dialogue driven by a JSON file. It never prints or reads input
    itself (that would corrupt the Textual screen). Instead:
      - start_dialogue() / choose() return the lines to show
      - `active` tells the app to route the player's next input to choose()
    A missing or broken JSON file just means there are no dialogues.

    A node can be written two ways:
      short:  {"speaker": "UNKNOWN", "text": "One line."}   (text may also be a list of lines)
      long:   {"lines": [ {"speaker": "A", "text": "..."}, {"speaker": "B", "text": "..."}, "bare string" ],
               "options": [...]}
    Each option may carry a "reply": what the player says and how the others answer,
    shown right after the choice and before the next node:
      {"text": "short menu label",
       "reply": [ {"speaker": "YOU", "text": "the full line"}, {"speaker": "UNKNOWN", "text": "..."} ],
       "next_node": "key"}
    """

    def __init__(self, dialogue_file_path):
        self.load_error = ""
        try:
            with open(dialogue_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("the top level must be an object { ... }")
        except OSError:
            data, self.load_error = {}, f"not found or unreadable: {dialogue_file_path}"
        except ValueError as err:
            data, self.load_error = {}, f"invalid JSON ({err})"

        self.triggers = data.get("file_triggers", {})
        self.nodes = data.get("nodes", {})

        self.opened_files = set()
        self.triggered_dialogues = set()
        self.current_node = None

    def problems(self) -> list[str]:
        """Plain-language list of everything wrong with the dialogue file (empty when it is fine)."""
        if self.load_error:
            return [self.load_error]
        found = []
        if not self.triggers:
            found.append("no file_triggers, so no conversation can start")
        for count, node in self.triggers.items():
            if node not in self.nodes:
                found.append(f"trigger {count} starts node '{node}', which does not exist")
        for name, node in self.nodes.items():
            if not isinstance(node, dict):
                continue
            for option in node.get("options", []):
                nxt = option.get("next_node")
                if nxt and nxt not in self.nodes:
                    found.append(f"node '{name}' has an option leading to '{nxt}', which does not exist")
        return found

    @property
    def active(self) -> bool:
        return self.current_node is not None

    def record_file_opened(self, filename: str):
        """
        Tracks unique opened files. Returns a dialogue trigger key if a threshold is hit.
        """
        self.opened_files.add(filename)
        count_str = str(len(self.opened_files))

        if count_str in self.triggers and count_str not in self.triggered_dialogues:
            self.triggered_dialogues.add(count_str)
            return self.triggers[count_str]

        return None

    def start_dialogue(self, start_node_key: str) -> list[str]:
        """Begins a dialogue at the given node and returns the lines to display."""
        if start_node_key not in self.nodes:
            self.current_node = None
            return []
        return self._render(start_node_key)

    def choose(self, choice: str) -> list[str]:
        """Applies the player's numbered choice and returns the next lines to display."""
        node = self.nodes.get(self.current_node)
        if node is None:
            self.current_node = None
            return []

        options = node.get("options", [])
        # Accept "1", " 1 ", "1.", "[1]", "(1)" and "#1"
        match = re.fullmatch(r"[\[\(#\s]*(\d+)[\]\)\.\s:]*", choice)
        if not match or not 1 <= int(match.group(1)) <= len(options):
            return [f"> Invalid selection. {self._choose_prompt(len(options))}"]

        option = options[int(match.group(1)) - 1]
        lines = []
        reply = self._normalise(option.get("reply"), PLAYER_SPEAKER)
        if reply:
            lines += [""] + self._speech(reply)

        next_node_key = option.get("next_node")
        if next_node_key in self.nodes:
            return lines + self._render(next_node_key)

        self.current_node = None
        return lines or [""]

    @staticmethod
    def _choose_prompt(count: int) -> str:
        """'Type 1 and press Enter.' / 'Type 1 or 2 ...' / 'Type 1, 2 or 3 ...'"""
        numbers = [str(n) for n in range(1, count + 1)]
        listed = numbers[0] if count == 1 else ", ".join(numbers[:-1]) + " or " + numbers[-1]
        return f"Type {listed} and press Enter."

    @staticmethod
    def _normalise(items, default_speaker: str) -> list:
        """Turn any accepted shape (str, dict, list of either) into [(speaker, text), ...]."""
        if not items:
            return []
        if isinstance(items, (str, dict)):
            items = [items]

        pairs = []
        for item in items:
            if isinstance(item, str):
                pairs.append((default_speaker, item))
                continue
            speaker = item.get("speaker", default_speaker)
            text = item.get("text", "")
            for part in ([text] if isinstance(text, str) else text):
                pairs.append((speaker, part))
        return pairs

    @staticmethod
    def _speech(pairs: list) -> list[str]:
        """[(speaker, text)] -> display lines, with a blank line between speakers."""
        lines = []
        for idx, (speaker, text) in enumerate(pairs):
            if idx:
                lines.append("")
            lines.append(f"[{speaker}]: {text}")
        return lines

    def _render(self, node_key: str) -> list[str]:
        node = self.nodes[node_key]
        default_speaker = node.get("speaker", "UNKNOWN")
        if "lines" in node:
            pairs = self._normalise(node["lines"], default_speaker)
        else:
            pairs = self._normalise({"speaker": default_speaker, "text": node.get("text", "")}, default_speaker)
        options = node.get("options", [])

        lines = ["", "=" * 42] + self._speech(pairs) + ["=" * 42]

        if not options:
            self.current_node = None
            return lines

        self.current_node = node_key
        lines += [f"  [{idx}] {opt.get('text', '...')}" for idx, opt in enumerate(options, 1)]
        lines += ["", f"> {self._choose_prompt(len(options))}"]
        return lines