import getpass

class StoryDirector:
    def __init__(self):
        # Physical / System Stats
        self.heartbeat = 0  # Starts at 0 until jacked in
        self.cpu = 2        # Low idle CPU
        self.ram_used = 0.4
        self.ram_total = 16.0
        self.username = getpass.getuser().upper()

        self.heart_pulse = False

        # Narrative State
        self.tutorial_step = 0
        
    def get_status_text(self) -> str:
        """Returns the formatted status text with a flashing heart emoji."""
        self.heart_pulse = not self.heart_pulse  # Toggle state every second
        
        if self.heartbeat == 0:
            hb_display = "FLATLINE [ ♡ ]"
        else:
            heart_icon = "♥" if self.heart_pulse else "♡"
            hb_display = f"{self.heartbeat} BPM [ {heart_icon} ]"

        return (
            f"NEURAL SYNC STATUS:\n\n"
            f"CPU (CORTEX): {self.cpu}%\n"
            f"RAM (MEM_BUFFER): {self.ram_used:.1f}GB / {self.ram_total}GB\n"
            f"HEARTBEAT: {hb_display}"
        )

    def advance_tutorial(self, step: int) -> list[str]:
        """Returns a list of strings to print to the terminal based on the step."""
        self.tutorial_step = step
        
        if step == 1:
            return [
                "INITIALIZING BIOS...",
                "LOADING KERNEL... [OK]",
                "MOUNTING DRIVES... [OK]"
            ]
            
        elif step == 2:
            return [
                "\n[FATAL ERROR]: NO NEURAL LINK DETECTED.",
                "> Physical connection required to access Esper Group internal servers.",
                "> Awaiting vascular port connection...",
                "\n[ ACTION REQUIRED ]: Type 'connect' to jack in."
            ]
            
        elif step == 3:
            # Player has typed 'connect'
            self.heartbeat = 65 # Heartbeat starts!
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