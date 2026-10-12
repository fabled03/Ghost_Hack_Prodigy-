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

USER_TREE = {
    "documents": {
        "Mission_Brief.txt": {"type": "file", "risk": "LOW", "info": "Operator briefing: the Prodigy OS core must stay isolated from the outer network at all times."},
        "access_codes.txt": {"type": "file", "risk": "HIGH", "info": "Handwritten codes for the core. The pages are warm, like someone just held them."},
        "budget_q3.xls": {"type": "file", "risk": "LOW", "info": "Quarterly budget. The Chrome division is over by 40% and nobody will say why."},
        "resignation_draft.doc": {"type": "file", "risk": "LOW", "info": "I can't keep doing this. They never tell us what the Chrome does to people."},
    },
    "personal": {
        "diary.txt": {"type": "file", "risk": "LOW", "info": "Night shift, day 112. The mainframe hums at a pitch I can almost feel in my teeth."},
        "voicemail.wav": {"type": "file", "risk": "MEDIUM", "info": "Three missed calls from an unknown number. Someone is breathing on the line."},
        "photos": {
            "sister.jpg": {"type": "file", "risk": "LOW", "info": "She stopped answering my calls after the implant."},
            "apartment.png": {"type": "file", "risk": "LOW", "info": "The view from the 40th floor. The rain never stops."},
            "mirror.png": {"type": "file", "risk": "HIGH", "info": "Why is there someone standing behind you?"},
        },
    },
    "projects": {
        "firewall_v2.py": {"type": "file", "risk": "LOW", "info": "Draft of the second-generation firewall. Unfinished."},
        "ghost_tracker.py": {"type": "file", "risk": "LOW", "info": "Script that watches for the GHOST signal. It has been quiet since last Tuesday."},
        "backdoor_test.sh": {"type": "file", "risk": "HIGH", "info": "I never wrote this."},
        "patch_notes.md": {"type": "file", "risk": "LOW", "info": "Changelog for the Prodigy OS patches. The last entry is blank."},
    },
    "messages": {
        "inbox.db": {"type": "file", "risk": "LOW", "info": "Forty unread messages. Most are automated."},
        "esper_memo.eml": {"type": "file", "risk": "LOW", "info": "Esper Group reminder: all Operators must report anomalies within 24 hours."},
        "unknown_sender.eml": {"type": "file", "risk": "CRITICAL", "info": "Hello, Operator. I have been in your files for a long time. Did you not notice?"},
        "last_words.txt": {"type": "file", "risk": "CRITICAL", "info": "If you are reading this, I'm already inside."},
    },
}