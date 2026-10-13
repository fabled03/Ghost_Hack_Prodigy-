# user_file_system.py
#
# The player's OWN directory. This is the tree the rogue AI attacks during the
# defend gameplay (see defense.py). file_system.py holds the mainframe's files.
#
# Same format as file_system.py:
#   a folder is a dict of names -> folders or files
#   a file is {"type": "file", "risk": str, "info": str}
#
# "risk" is shown to the player and also sets how likely the AI is to infect the
# file (see RISK_WEIGHT in user_files.py): CRITICAL > HIGH > MEDIUM > LOW. The
# "info" text is shown when the player runs `inspect`. The story text below is
# placeholder, so rewrite it however you like. Folders can be nested as deeply
# as you want.
from ASCII_Art import Takeover, Daughter, Appartment, Together, Smile

USER_TREE = {
    "documents": {
        "Mission_Brief.txt": {"type": "file", "risk": "LOW", "info": "Infiltrate the Esper Group and aquire senstitive documents in regards to Prodigy OS."},
        "access_port.txt": {"type": "file", "risk": "HIGH", "info": "Encrypted key for entry into Prodigy OS."},
        "offshore_account.xls": {"type": "file", "risk": "LOW", "info": "Current value: $2,500 credits. Transfer of 10,000,000 credits pending."},
        "resume.doc": {"type": "file", "risk": "LOW", "info": "Succesful hacks into Arasaka Corportaion, Militech, and Kyroshi Corporation."},
    },
    "personal": {
        "diary.txt": {"type": "file", "risk": "LOW", "info": "Every dive feels like more of me is code. This has to be the last one. This job should give me enough to give her a chrome body to finally live her life."},
        "voicemail.wav": {"type": "file", "risk": "MEDIUM", "info": "Three missed calls from an Samantha. 1. 'I miss you, come home soon please.' 2. 'I love you please be careful for me.' 3. 'Happy Birthday!!!' "},
        "photos": {
            "daughter.jpg": {"type": "file", "risk": "LOW", "info": "Her birthday before the attack.", "ASCII": Daughter},
            "apartment.png": {"type": "file", "risk": "LOW", "info": "The first day we moved in.", "ASCII": Appartment},
            "together.png": {"type": "file", "risk": "HIGH", "info": "That's not Samantha.", "ASCII": Together},
            "takeover.png": {"type": "file", "risk": "CRITICAL", "info": "I feel the potential of this shell.", "ASCII": Takeover},
            "smile.png": {"type": "file", "risk": "LOW", "info": "Smile, because I will take care of it now.", "ASCII": Smile},
        },
    },
    "projects": {
        "firewall_v2.py": {"type": "file", "risk": "LOW", "info": "Self made firewall to protect myself from netrunners."},
        "home_security.py": {"type": "file", "risk": "LOW", "info": "In case of an attack on me or the appartment, security lockdown and trauma team suppport."},
        "backdoor_test.sh": {"type": "file", "risk": "HIGH", "info": "Self writing code into my interface?"},
        "patch_notes.md": {"type": "file", "risk": "MEDIUM", "info": "I just did a system update...."},
    },
    "messages": {
        "inbox.db": {"type": "file", "risk": "LOW", "info": "5 unread messages and 4 saved messages."},
        "esper_memo.eml": {"type": "file", "risk": "LOW", "info": "Note: Higher potential secruity risk expected in the coming weeks."},
        "f8s9_0-4ty.eml": {"type": "file", "risk": "CRITICAL", "info": "Corruption, corruption, corruption."},
        "last_words.txt": {"type": "file", "risk": "CRITICAL", "info": "Don't delete; if you do, it is only a matter of time."},
        "unknown.txt":{"type": "file", "risk": "CRITICAL", "info": "Just let go."}
    },
}