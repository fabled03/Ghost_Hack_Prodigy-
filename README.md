# GhostHack

A cyberpunk hacking game that runs in your terminal, built with Python and [Textual](https://textual.textualize.io/).

You are an operator who has jacked into the **Prodigy OS** mainframe of the Esper Group. Your job is to find the OS blueprints, copy them and get out. 

## Requirements

- Python 3.9 or newer (built and tested on 3.12 and 3.13)
- [Textual](https://pypi.org/project/textual/) (installs [Rich](https://pypi.org/project/rich/) with it)
- A roomy terminal window with colour support (the game shows a status panel next to the console)

```bash
pip install textual
```

## Run it

From the game folder:

```bash
python main.py
```

The game boots, asks you to type `connect`, and then starts in the training folder. Type `restart` after a game ends to play again.

## How to play

You type commands at a prompt. The first four files you open are in `/tutorial` and explain the rest. Do those first.

### Commands

| Command | What it does |
|---|---|
| `ls [path]` | List a folder |
| `tree [path]` | Show everything inside a folder |
| `cd <path>` | Move into a folder (`cd ..` goes back; a bare folder name works too) |
| `open <file>` | Read a file. This is the only command that counts toward your file total |
| `inspect <file>` | Show a file's risk level and check it for viruses. With no file, it lists the risk level of every file in the folder |
| `scan [path]` | Check whether a file or folder is encrypted, so you can prepare to breach it. During an attack it shows the infected folder instead |
| `encrypt <file>` | During an attack: cure and lock a file. Takes a moment and raises a firewall |
| `delete <file>` | During an attack: destroy a file for good. Faster than `encrypt` |
| `help` | List the commands |
| `manual` | Show the defense reminders again |

Some commands appear only when the story asks for them: `connect`, `rotate <row> <col>`, `transmit` and `copy <file>`. They are not listed by `help`.

### The three parts of the game

**Exploring.** Browse the mainframe with `ls`, `cd` and `tree`, and read files with `open`. Some files are dangerous, so `inspect` a file first to see its risk level. Opening certain files could cause you to become attacked by the system... or something else. 

**Defending.** When you are attacked, your three vitals (CPU, RAM and heartbeat) climb every second, and the more dangerous the attack the faster they climb. One of five of your own files is the source of the attack. Use `inspect` to work out which one, then `encrypt` it to cure it, or `delete` it. Encrypting the wrong file makes things worse. If any vital maxes out, you flatline. If you take too long, the damage becomes permanent and your resting vitals stay higher from then on. Each firewall you raise slows the next attack.

**Breaching.** Some mainframe files are encrypted. `open` one and you get a pipe puzzle: rotate pieces with `rotate <row> <col>` (counting from 0) until a connected path runs from the green start to the magenta finish, then `transmit`.

Open enough different files and the real target appears. Reach it, read it, and `copy` it before the system stops you.

## Project layout

| File | Purpose |
|---|---|
| `main.py` | The game: boot sequence, commands, story phases, end game |
| `Defend_gameplay.py` | The defense minigame: vitals, attacks, permanent damage |
| `Attack_gameplay.py` | The pipe puzzle used to breach encrypted files |
| `director.py` | Story text, the status panel and the dialogue system |
| `file_system.py` | The mainframe's files, the tutorial text and the end-game files |
| `User_file_tree.py` | Your own files, which the defense minigame draws from |
| `dialogue_tree.json` | The conversations with the AI |

`User_file_tree.py` must define a dictionary called `USER_TREE`, in the same format as `FILE_TREE` in `file_system.py`.

## Editing the content

### Files and folders

Both file trees are plain nested dictionaries. A file looks like this:

```python
"notes.txt": {"type": "file", "safe": True, "Encrypted": False, "risk": "LOW", "info": "Text shown when the file is opened."}
```

- `risk` is shown by `inspect`. In the defense minigame, riskier files are more likely to be the infected one.
- `safe: False` marks a mainframe file as dangerous; opening one during the exploring phases can launch an attack.
- `Encrypted: True` makes the file need the pipe puzzle before it can be read.

### Dialogue

Conversations live in `dialogue_tree.json`. The player picks an answer by typing `1` or `2`.

```json
{
  "file_triggers": { "4": "Introduction" },
  "nodes": {
    "Introduction": {
      "lines": [
        { "speaker": "Samantha", "text": "How do you like what you see so far?" },
        { "speaker": "Samantha", "text": "Do you know me?" }
      ],
      "options": [
        {
          "text": "Who are you?",
          "reply": [{ "speaker": "Operator", "text": "Who are you?" }],
          "next_node": "Next"
        },
        {
          "text": "Leave me alone.",
          "reply": [{ "speaker": "Operator", "text": "Leave me alone." }],
          "next_node": "Next"
        }
      ]
    },
    "Next": {
      "lines": [{ "speaker": "Samantha", "text": "A node with no options ends the conversation." }]
    }
  }
}
```

- `file_triggers` maps a number of opened files to the node that starts. Each one fires once.
- `lines` is everything the AI says that turn, as many lines as you like.
- `text` is the short menu label. `reply` is the line the player says.
- Both options can point to the same `next_node`, so the AI's answer does not change, or to different nodes to branch.
- A node with no `options`, or an option with no `next_node`, ends the conversation.
- Keys that start with an underscore are notes and are ignored.

Keep the file valid JSON. Use double quotes, put a comma between items, and none after the last one.

## Tuning the difficulty

These values are at the top of `Defend_gameplay.py`:

| Setting | Effect |
|---|---|
| `ATTACKS` | How fast CPU, RAM and heartbeat climb per second for each attack |
| `ATTACK_DEADLINE` | Seconds before an attack causes permanent damage |
| `PERM_CPU_HIT`, `PERM_RAM_HIT` | How much each permanent damage raises your resting CPU and RAM |
| `MAX_BASE_CPU`, `MAX_BASE_RAM` | The highest your resting levels can be pushed |
| `RISK_WEIGHT` | How much more likely riskier files are to be infected |
| `POOL_SIZE` | Number of files shown in each defense |

In `main.py`, `FILE_THRESHOLD` is the number of files you must open for the real target to appear, and `ENDGAME_ATTACK_GAP` is the seconds between attacks in the final stage.

## Development

Set `DEBUG_COMMANDS = True` near the top of `main.py` to turn on two shortcuts, `clear` and `jump <1-13>`, which skips ahead to a story phase. Turn it back to `False` before you hand the game to anyone.

**Spoiler note:** `POOL_SIZE` and the takeover limit (`LOST_FILE_LIMIT` in `Defend_gameplay.py`) are both 5, on purpose. A player who deletes that many files in total is taken over, and the game gives no warning. Keep `POOL_SIZE` at least as large as `LOST_FILE_LIMIT`, or a defense may not offer enough files to reach it. 
