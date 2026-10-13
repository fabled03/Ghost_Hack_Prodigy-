import random

ATTACKS = [
    {"name": "BRUTE FORCE",      "cpu": 6, "ram": 0.5, "bpm": 5},
    {"name": "SQL INJECTION",    "cpu": 4, "ram": 0.9, "bpm": 6},
    {"name": "DDOS FLOOD",       "cpu": 8, "ram": 0.6, "bpm": 7},
    {"name": "PHISHING PAYLOAD", "cpu": 5, "ram": 0.7, "bpm": 4},
]

HOME_FILES = ["kernel.dll", "svch0st.exe", "sys_log.txt", "update_tmp.dat"]
ATTACKER_LINES = ["[UNKNOWN]: You can't lock me out forever.", "[UNKNOWN]: Firewall detected. Adapting."]
TRAP_LINES = ["FATAL: Triggered a defense countermeasure!", "WARNING: Unauthorized access detected by core."]
PRESSURE = 0.22          # global multiplier on how fast vitals climb
INITIAL_INFECTED = 2     # files infected when an attack starts
MAX_INFECTED = 3         # the infection never spreads beyond this many at once
SPREAD_EVERY = 20        # seconds between new infections while the attack lasts
ATTACK_DEADLINE = 10     # seconds before the infection takes root
PERM_CPU_HIT = 8         # permanent CPU baseline increase
PERM_RAM_HIT = 1.0       # permanent RAM baseline increase (GB)
LOST_FILE_LIMIT = 5      # delete this many files and the AI takes over
MAX_BASE_CPU = 98
MAX_BASE_RAM = 15
BASE_CPU = 4
BASE_RAM = 1.2
BASE_BPM = 64

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

    def check_takeover(self) -> bool:
        """Every deleted file feeds the AI. Too many and it takes over."""
        lost = len(self.files.deleted)
        left = LOST_FILE_LIMIT - lost
        if left > 0:
            if lost >= 2:
                self.write(f"> WARNING: {lost} files lost. The AI is learning from the gaps. "
                        f"{left} more and it takes over.")
            return False
        self.takeover()
        return True
    
    def takeover(self) -> None:
        self.running = False
        self.refresh()
        self.write("\n=== TOO MANY FILES LOST ===")
        self.write("> The mainframe has nothing left to protect you with.")
        self.write("> Your terminal is no longer responding to you.")
        self.write("[UNKNOWN]: Thank you. I'll take it from here, Operator.")
        self.on_crash()

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