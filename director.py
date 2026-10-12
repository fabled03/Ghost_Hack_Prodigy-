import getpass
from Defend_gameplay import bar

class StoryDirector:
    def __init__(self):
        self.heartbeat = 0
        self.cpu = 2
        self.ram_used = 0.4
        self.ram_total = 16.0
        self.username = getpass.getuser().upper()
        self.heart_pulse = False
        self.tutorial_step = 0

    def get_status_text(self, game_active=False, defense_state=None) -> str:
        self.heart_pulse = not self.heart_pulse
        
        if self.heartbeat == 0:
            hb_display = "FLATLINE [ ♡ ]"
        else:
            heart_icon = "♥" if self.heart_pulse else "♡"
            hb_display = f"{self.heartbeat} BPM [ {heart_icon} ]"

        if not game_active:
            return (
                f"NEURAL SYNC STATUS:\n\n"
                f"CPU (CORTEX): {self.cpu}%\n"
                f"RAM (MEM_BUFFER): {self.ram_used:.1f}GB / {self.ram_total}GB\n"
                f"HEARTBEAT: {hb_display}"
            )
        else:
            threat = defense_state.active_attack["name"] if defense_state.active_attack else "NONE"
            return (
                f"SYSTEM STATUS:\n\n"
                f"CPU:   [{bar(defense_state.cpu, 100)}] {int(defense_state.cpu)}%\n"
                f"RAM:   [{bar(defense_state.ram, 16)}] {defense_state.ram:.1f}/16GB\n"
                f"HEART: [{bar(defense_state.bpm, 180)}] {int(defense_state.bpm)} BPM\n\n"
                f"THREAT: {threat}\n"
                f"FIREWALLS: {defense_state.firewalls}\n"
                f"PERMANENT DAMAGE: {defense_state.scars}\n"
                f"BASELINE: {int(defense_state.base_cpu)}% / {defense_state.base_ram:.1f}GB"
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
                "\n[ ACTION REQUIRED ]: Type 'connect' to jack in."
            ]
        elif step == 3:
            self.heartbeat = 65
            self.cpu = 12
            self.ram_used = 1.2
            return [
                "\n> Syringe engaged. Piercing skin...",
                "> Neural pathways syncing... [OK]",
                "> Biometrics detected. Vitals stable."
            ]
        elif step == 4:
            return [
                "\n--- CONNECTION ESTABLISHED ---",
                f"\n[SYSTEM AI]: Biometric sync complete. Welcome, {self.username}.",
                "[SYSTEM AI]: I am the local system for Esper Group.",
                "[SYSTEM AI]: Primary diagnostics nominal. Terminal port connection secured.",
                "[SYSTEM AI]: How can I assist your session today, Operator?",
                "\n[SYSTEM AI]: Type 'help' to review your terminal capabilities."
            ]
        return []