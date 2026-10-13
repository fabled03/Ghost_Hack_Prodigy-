import random

from User_file_tree import USER_TREE


def get_random_directory_files(tree):
    """Pick a random folder that holds files. Returns (folder_name, {file_name: file_data})."""
    folders = []

    def collect(d):
        for k, v in d.items():
            if isinstance(v, dict):
                # Check if this folder contains direct file items
                if any(isinstance(sub_v, dict) and sub_v.get("type") == "file" for sub_v in v.values()):
                    folders.append((k, v))
                collect(v)

    collect(tree)

    if not folders:
        return "root", {
            "kernel.dll": {"type": "file", "risk": "LOW", "info": "Core system library."},
            "sys_log.txt": {"type": "file", "risk": "LOW", "info": "System log."},
        }

    chosen_name, chosen_dict = random.choice(folders)
    files = {k: v for k, v in chosen_dict.items() if isinstance(v, dict) and v.get("type") == "file"}
    return chosen_name, files


ATTACKS = [
    {"name": "BRUTE FORCE",      "cpu": 0.8, "ram": 0.05, "bpm": 1.0},
    {"name": "SQL INJECTION",    "cpu": 0.5, "ram": 0.1,  "bpm": 1.2},
    {"name": "DDOS FLOOD",       "cpu": 1.2, "ram": 0.08, "bpm": 1.5},
    {"name": "PHISHING PAYLOAD", "cpu": 0.6, "ram": 0.08, "bpm": 0.8},
]

ATTACKER_LINES = ["[UNKNOWN]: You can't lock me out forever.", "[UNKNOWN]: Firewall detected. Adapting."]
TRAP_LINES = ["FATAL: Triggered a defense countermeasure!", "WARNING: Unauthorized access detected by core."]

# How likely the AI is to infect a file, by the "risk" label in user_file_system.py
RISK_WEIGHT = {"CRITICAL": 8, "HIGH": 4, "MEDIUM": 2, "LOW": 1}

PRESSURE = 0.10
INITIAL_INFECTED = 2
MAX_INFECTED = 3
SPREAD_EVERY = 20
ATTACK_DEADLINE = 35
PERM_CPU_HIT = 2
PERM_RAM_HIT = 0.1
LOST_FILE_LIMIT = 5
MAX_BASE_CPU = 98
MAX_BASE_RAM = 15
BASE_CPU = 4
BASE_RAM = 1.2
BASE_BPM = 64
REST_BPM = 72


def bar(value, maximum, width=10):
    filled = int(width * min(value, maximum) / maximum)
    return "#" * filled + "-" * (width - filled)


class DefenseGame:
    def __init__(self):
        self.base_cpu = 4
        self.base_ram = 1.2
        self.cpu = self.base_cpu
        self.ram = self.base_ram
        self.bpm = REST_BPM

        self.active_attack = None
        self.infected_file = None
        self.inspected = set()
        self.attack_elapsed = 0
        self.scarred = False
        self.scars = 0
        self.firewalls = 0
        self.game_active = False
        self.decoded = set()
        self.deleted = []  # Files the player destroyed; too many and the AI takes over (silently)

        # Pick a random single directory from the tree for this session
        folder_name, file_list = get_random_directory_files(USER_TREE)
        self.current_folder_name = folder_name
        self.file_data = dict(file_list)
        self.home_files = list(file_list)
        self.backup_files = list(file_list)

    def check_takeover(self) -> tuple[bool, list[str]]:
        """Returns (taken_over, lines_to_print)."""
        # No warning on the way: the takeover is meant to be a surprise
        if len(self.deleted) < LOST_FILE_LIMIT:
            return False, []
        return True, self.takeover()

    def takeover(self) -> list[str]:
        self.game_active = False
        self.end_attack()
        return [
            "\n=== TOO MANY FILES LOST ===",
            "> The mainframe has nothing left to protect you with.",
            "> Your terminal is no longer responding to you.",
            "[UNKNOWN]: Thank you. I'll take it from here, Operator.",
        ]

    def tick(self) -> tuple[bool, str]:
        msg = ""
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
                    msg = "> WARNING: infection is digging in. Act now."
                if remaining <= 0:
                    self.apply_permanent_damage()
                    msg = "!!! THE INFECTION TAKES ROOT !!!\n> Permanent damage: resting CPU and RAM increased."

            if old_cpu < 70 <= self.cpu:
                msg = "!!! WARNING: CPU CRITICAL. YOUR PULSE IS RACING. !!!"

            if self.cpu >= 100 or self.ram >= 16 or self.bpm >= 180:
                return True, "=== SYSTEM OVERLOAD. FLATLINE. ==="
        else:
            self.cpu = max(self.base_cpu, self.cpu - 3)
            self.ram = max(self.base_ram, self.ram - 0.3)
            self.bpm = max(REST_BPM, self.bpm - 4)

        return False, msg

    def at_baseline(self) -> bool:
        return self.cpu <= self.base_cpu and self.ram <= self.base_ram and self.bpm <= REST_BPM

    def apply_permanent_damage(self):
        self.scarred = True
        self.scars += 1
        self.base_cpu = min(MAX_BASE_CPU, self.base_cpu + PERM_CPU_HIT)
        self.base_ram = min(MAX_BASE_RAM, self.base_ram + PERM_RAM_HIT)

    def launch_attack(self) -> str:
        if not self.home_files:
            self.home_files = list(self.backup_files)

        # Riskier files are more likely to be the infection source
        weights = [RISK_WEIGHT.get(self.file_data.get(name, {}).get("risk"), 1) for name in self.home_files]
        self.active_attack = random.choice(ATTACKS)
        self.infected_file = random.choices(self.home_files, weights=weights, k=1)[0]
        self.inspected = set()
        self.attack_elapsed = 0
        self.scarred = False
        return (f"\n!!! ALERT: {self.active_attack['name']} !!!\n"
                f"> A process is feeding on your system. Vitals climbing.\n"
                f"> Neutralize it within {ATTACK_DEADLINE}s or damage becomes permanent.")

    def end_attack(self):
        self.active_attack = None
        self.infected_file = None
        self.attack_elapsed = 0
        self.scarred = False