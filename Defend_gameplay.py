import random

ATTACKS = [
    {"name": "BRUTE FORCE",      "cpu": 6, "ram": 0.5, "bpm": 5},
    {"name": "SQL INJECTION",    "cpu": 4, "ram": 0.9, "bpm": 6},
    {"name": "DDOS FLOOD",       "cpu": 8, "ram": 0.6, "bpm": 7},
    {"name": "PHISHING PAYLOAD", "cpu": 5, "ram": 0.7, "bpm": 4},
]

FILES = {
    "sys_core.dat": {"safe": True, "result": "Core module verified."},
    "anomaly.tmp": {"safe": False},
    "lazarus_blueprint.enc": {"safe": True, "result": "Project Lazarus blueprint accessed.", "win": True}
}

HOME_FILES = ["kernel.dll", "svch0st.exe", "sys_log.txt", "update_tmp.dat"]
ATTACKER_LINES = ["[UNKNOWN]: You can't lock me out forever.", "[UNKNOWN]: Firewall detected. Adapting."]
TRAP_LINES = ["FATAL: Triggered a defense countermeasure!", "WARNING: Unauthorized access detected by core."]
ATTACK_DEADLINE = 8
PERM_CPU_HIT = 8
PERM_RAM_HIT = 1.0
MAX_BASE_CPU = 60
MAX_BASE_RAM = 10

def bar(value, maximum, width=10):
    filled = int(width * min(value, maximum) / maximum)
    return "#" * filled + "-" * (width - filled)


class DefenseGame:
    def __init__(self):
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
        self.game_active = False
        self.decoded = set()
        self.home_files = list(HOME_FILES)

    def tick(self) -> tuple[bool, str | None]:
        """Processes a second of gameplay. Returns (crashed, message)."""
        if not self.game_active:
            return False, None

        msg = None
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
            self.bpm = max(72, self.bpm - 4)

        return False, msg

    def apply_permanent_damage(self):
        self.scarred = True
        self.scars += 1
        self.base_cpu = min(MAX_BASE_CPU, self.base_cpu + PERM_CPU_HIT)
        self.base_ram = min(MAX_BASE_RAM, self.base_ram + PERM_RAM_HIT)

    def launch_attack(self) -> str:
        if not self.home_files:
            self.home_files = list(HOME_FILES)
        self.active_attack = random.choice(ATTACKS)
        self.infected_file = random.choice(self.home_files)
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