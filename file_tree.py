# file_system.py

FILE_TREE = {
    "tutorial": {
        "01_welcome.txt": {"type": "file", "risk": "NONE", "tutorial": True, "info": "Training file 1 of 4.", "text": """
WELCOME, OPERATOR

The Prodigy mainframe has been breached. Someone is inside your system, and they are coming for your files.

You have succesfully hacked into the Esper Groups top secret Prodigy OS. Your job is to find the blueprints of this OS, copy the data and extract without being detected. 

Read every file in this folder. Use: open <file>
"""},
        "02_vitals.txt": {"type": "file", "risk": "NONE", "tutorial": True, "info": "Training file 2 of 4.", "text": """
YOUR VITALS

The status panel tracks three things: CPU, RAM and your own HEARTBEAT.

When you are safe they rest at your baseline. Under attack they climb every second.

If any one of them maxes out, your synapses will burnout.

If an infection takes root, your baseline rises for good and will be set at a new baseline. 
"""},
        "03_defending.txt": {"type": "file", "risk": "NONE", "tutorial": True, "info": "Training file 3 of 4.", "text": """
DEFENDING

An attack infects files in your directory. The more files infected, the faster your vitals climb, and the infection keeps spreading until you clear it.

scan            which folders are infected
ls / tree       look inside your folders
inspect <file>  check one file

Then clear each infected file:
encrypt <file>  cure and lock it. Raises a firewall.
debug <file>    cure it and repair permanent damage
delete <file>   destroy it for good

You only have seconds before the infection takes root. Watch the countdown in the status panel.
"""},
        "04_commands.txt": {"type": "file", "risk": "NONE", "tutorial": True, "info": "Training file 4 of 4.", "text": """
COMMANDS

ls [path]       list a folder
cd <path>       move into a folder
open<file>      open folder
inspect <file>  check a file for viruses
encrypt<file>   protect your files/can no longer be hacked again/takes time to do though
delete<file>    prementaely removes file, takes less time.
debug<file>     check the risk level of a file.
help            list every command
manual          defense reminders

"""},
    },
    "home": {
        "operator": {
            "notes.txt": {"type": "file", "safe": True, "risk": "LOW", "info": "Reminder: Change master encryption key before Friday."},
            "mail_cache.db": {"type": "file", "safe": True, "risk": "LOW", "info": "Local cache of encrypted communications."},
            "session.log": {"type": "file", "safe": True, "risk": "LOW", "info": "Terminal history: last login from localhost."},
            "driver_update.exe": {"type": "file", "safe": False, "risk": "HIGH", "info": "Suspicious binary disguised as a hardware patch."},
        },
        "downloads": {
            "Chrome.tar:_Manual.pdf": {"type": "file", "safe": True, "risk": "LOW", "info": "Data list of new Chrome prosethetics to hit the market next fiscal quarter."},
            "reboot.patch.exe": {"type": "file", "safe": False, "risk": "UNKNOWN", "info": "AI assistance reboot. Only run as last possible resort."},
            "extension.zip": {"type": "file", "safe": True, "risk": "LOW", "info": "All realitve extensions for use of Priodigy if not already installed."},
        },
        "images": {
            "family_photo.jpg": {"type": "file", "safe": True, "risk": "LOW", "info": "JPEG image of a family gathering."},
            "vacation.png": {"type": "file", "safe": True, "risk": "LOW", "info": "PNG image of a family vacation"},
            "disease.png": {"type": "file", "safe": False, "risk": "HIGH", "info": "I tried to hold on. I tried to fight. I tried it all. Yet they gave up on me."},
            "infection.png": {"type": "file", "safe": False, "risk": "HIGH", "info": "It spread through my brain. Maybe I can do the same to you."},
            "haunting.png": {"type": "file", "safe": False, "risk": "CRITICAL", "info": "And I will always be with you then. I won't be alone again. Together, you and me. Like a lover."},
            "operation.png": {"type": "file", "safe": False, "risk": "CRITICAL", "info": "Don't look at that. DON'T LOOK at that. DON'T LOOK AT THAT!"},
            "extractions.png": {"type": "file", "safe": True, "risk": "LOW", "info": "Successful."},
            "final_moments.png": {"type": "file", "safe": True, "risk": "LOW", "info": "It wasn't goodbye, because you came to say Hello."},
        },
    },
    "sys": {
        "kernel_log.enc": {"type": "file", "safe": True, "risk": "NONE", "info": "Log entry: unknown login from 'GHOST' corrupted time 'corrupted', intention 'corrupted'."},
        "payroll.dat": {"type": "file", "safe": True, "risk": "NONE", "info": "Payroll records. Only shows up to middle managment. Upper managment records are not listed."},
        "backup_final.bin": {"type": "file", "safe": False, "risk": "CRITICAL", "info": "Use only after sucesssful reboot."},
        "security.enc": {"type": "file", "safe": False, "risk": "CRITICAL", "info": "List of security codes used to access the Prodigy OS core."},
        "samantha.rogue": {"type": "file", "safe": True, "win": True, "risk": "NONE", "info": "My name? "},
        "ghost_signal.tru": {"type": "file", "safe": True, "risk": "NONE", "info": "Trusted signal from GHOST_'corrupted'. Intentions: 'corrupted'"},
        "bradcast.sig": {"type": "file", "safe": True, "risk": "NONE", "info": "Encrypted broadcast signal from Esper Group."},
    },
    "medical": {
        "patient_records.enc": {"type": "file", "safe": True, "risk": "LOW", "info": "Terminal Chrome leakage causing spinal failure. So they told me."},
        "research_data.bin": {"type": "file", "safe": True, "risk": "LOW", "info": "Trail 34 of the Prodigy Project. Subject WILL NOT SURVIVE."},
        "virus_sample.dat": {"type": "file", "safe": False, "risk": "HIGH", "info": "Sample of Prodigy Virus successfully extracted from patient. Uploaded to mainframe"},
        "quarantine.log": {"type": "file", "safe": True, "risk": "LOW", "info": "I escaped..."},
    },
    "confidential": {
        "samantha.rougue": {"type": "file", "safe": True, "risk": "MEDIUM", "info": "Ghost 'corrupted' shows the most promises out of all the Ghost. They were the most statble individuals and will be studied throughly."},
        "ghost_signal.tru": {"type": "file", "safe": True, "risk": "MEDIUM", "info": "Ghost 'corrupted' signal synchronization allows them to access any mainframe on local networks with ease."},
        "backdoor_protocol.sh": {"type": "file", "safe": False, "risk": "HIGH", "info": "Do you think this would work on me?"},
        "override_p": {"type": "file", "safe": False, "risk": "HIGH", "info": "Into you."},
    },
    "Logs": {
        "system.log": {"type": "file", "safe": True, "risk": "LOW", "info": "System log entries for the past 30 days."},
        "error.log": {"type": "file", "safe": True, "risk": "LOW", "info": "Error log entries for the past 30 days."},
        "access.log": {"type": "file", "safe": True, "risk": "LOW", "info": "Access log entries for the past 30 days."},
        "ghost.log": {"type": "file", "safe": True, "risk": "LOW", "info": "Ghost log entries for the past 30 days."},
        "samantha.log": {"type": "file", "safe": True, "risk": "LOW", "info": "Samantha log entries for the past 30 days."},
        "end_of_days.log": {"type": "file", "safe": True, "risk": "LOW", "info": "End of days log entries for the past 30 days."},
        "possession.log": {"type": "file", "safe": True, "risk": "LOW", "info": "Possession log entries for the past 30 days."},
    },
}

# The strange file that appears in ~ once every tutorial file has been read.
# It is the 'AI'. Like tutorial files it is never infected and can't be deleted.
AI_FILE_NAME = "hello_operator.sig"
AI_FILE = {
    "type": "file",
    "risk": "UNKNOWN",
    "ai": True,
    "info": "Appears to be the apart of the OS.",
    "ascii": GHOST,
    "text": """
[UNKNOWN]: Hello. I don't believe we have met before.
[UNKNOWN]: It will be nice to interact with someone. It has been quite awhile. 
[UNKNOWN]: Go on. Look around. Open whatever you like. I will be very glad to help you along. 
[UNKNOWN]: 
[UNKNOWN]: ...but be careful what you open.
""",
}