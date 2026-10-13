
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
        else:
            threat = defense_state.active_attack["name"] if defense_state.active_attack else "NONE"
            return (
                f"SYSTEM STATUS:\n\n"
                f"CPU:   [{bar(defense_state.cpu, 100)}] {int(defense_state.cpu)}%\n"
                f"RAM:   [{bar(defense_state.ram, 16)}] {defense_state.ram:.1f}/16GB\n"
                f"HEART: [{bar(defense_state.bpm, 180)}] {int(defense_state.bpm)} BPM [ {heart_icon} ]\n\n"
                f"THREAT: {threat}\n"
                f"FIREWALLS: {defense_state.firewalls}\n"
                f"PERMANENT DAMAGE: {defense_state.scars}\n"
                f"BASELINE: {int(defense_state.base_cpu)}% / {defense_state.base_ram:.1f}GB\n"
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