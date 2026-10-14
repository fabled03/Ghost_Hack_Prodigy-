import random

from User_file_tree import USER_TREE


POOL_SIZE = 5  # files shown (and deletable) in every defense; matches LOST_FILE_LIMIT


def collect_folders(tree):
    """Every folder that holds files: [(folder_name, {file_name: file_data})]."""
    folders = []

    def walk(d):
        for k, v in d.items():
            if isinstance(v, dict) and v.get("type") != "file":
                files = {n: f for n, f in v.items() if isinstance(f, dict) and f.get("type") == "file"}
                if files:
                    folders.append((k, files))
                walk(v)

    walk(tree)
    return folders


def get_random_directory_files(tree, exclude=(), size=POOL_SIZE):
    """Pick `size` files for one defense. Starts from one random folder and tops up with
    files from other folders when it has too few, so there are always enough to delete.
    Returns (folder_name, {file_name: file_data}, {file_name: folder_name})."""
    folders = collect_folders(tree)
    if not folders:
        return "root", {
            "kernel.dll": {"type": "file", "risk": "LOW", "info": "Core system library."},
            "sys_log.txt": {"type": "file", "risk": "LOW", "info": "System log."},
        }, {"kernel.dll": "root", "sys_log.txt": "root"}

    main_name, main_files = random.choice(folders)
    chosen = {n: f for n, f in main_files.items() if n not in exclude}
    origin = {n: main_name for n in chosen}
    if len(chosen) > size:
        keep = random.sample(list(chosen), size)
        chosen, origin = {n: chosen[n] for n in keep}, {n: main_name for n in keep}

    others = [(n, f, fname) for fname, files in folders if fname != main_name
              for n, f in files.items() if n not in exclude and n not in chosen]
    random.shuffle(others)
    for n, f, fname in others:
        if len(chosen) >= size:
            break
        chosen[n], origin[n] = f, fname
    return main_name, chosen, origin


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
        self.new_pool()

    def new_pool(self):
        """Fresh set of POOL_SIZE files for this defense. Destroyed files never come back."""
        folder_name, files, origin = get_random_directory_files(USER_TREE, exclude=set(self.deleted))
        self.current_folder_name = folder_name
        self.file_data = dict(files)
        self.file_folder = dict(origin)
        self.home_files = list(files)

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
        self.new_pool()  # every attack: POOL_SIZE files to inspect, encrypt or delete

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