# file_system.py

FILE_TREE = {
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