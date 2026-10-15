# GhostHack

A cyberpunk hacking game that runs in your terminal, built with Python and [Textual](https://textual.textualize.io/).

You are an operator who has jacked into the **Prodigy OS** mainframe of the Esper Group. Your job is to find the OS blueprints, copy them and get out. You are not alone in the system.

## Requirements

- **Python 3.9 or newer** (built and tested on 3.12 and 3.13)
- **[Textual](https://pypi.org/project/textual/)**, which installs [Rich](https://pypi.org/project/rich/) with it
- A terminal window with colour support, about **120 columns by 35 rows**. The game shows a status panel next to the console, so maximise the window
- Windows, macOS or Linux. iPhone and iPad are not supported, because iOS has no real terminal that can run Textual reliably

The game needs no internet connection once Textual is installed.

## Install and run

Pick your system. Every route does the same four things: put the game files in one folder, open a terminal in that folder, install Textual, run `main.py`.

### Files

Keep all of these together in **one folder**. If one is missing, the game stops on start with an `ImportError`.

```
main.py              Defend_gameplay.py    file_system.py    ASCII_Art.py
director.py          Attack_gameplay.py    User_file_tree.py dialogue_tree.json
```

If your main file has a different name, use that name wherever the steps below say `main.py`.

### Windows

1. **Install Python** from [python.org/downloads](https://www.python.org/downloads/). On the first installer screen, tick **Add python.exe to PATH**, then click Install Now.
2. **Open a terminal in the game folder.** In File Explorer, open the folder, click the address bar, type `cmd` and press Enter. Or open **Windows Terminal** (recommended) or PowerShell and run:

   ```
   cd C:\Users\you\Ghost_Hack_Prodigy-
   ```

   Run `dir` to check that `main.py` is listed.
3. **Install Textual** (once):

   ```
   py -m pip install textual
   ```

4. **Run the game:**

   ```
   py main.py
   ```

   `python main.py` works too if `py` is not found.

### macOS

1. **Install Python 3.** Check first with `python3 --version`. If it is missing or older than 3.9, install it from [python.org/downloads](https://www.python.org/downloads/macos/) or with Homebrew (`brew install python`). If macOS offers to install the Command Line Tools, accept.
2. **Open Terminal** (Spotlight, then "Terminal"; [iTerm2](https://iterm2.com/) looks better) and go to the game folder:

   ```bash
   cd ~/Downloads/Ghost_Hack_Prodigy-
   ls
   ```

   Run `ls` to check that `main.py` is listed. You can also type `cd ` and drag the folder from Finder into the window.
3. **Create a virtual environment and install Textual** (once). Recent macOS and Homebrew Pythons refuse a plain `pip install`, so this is the reliable way:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install textual
   ```

4. **Run the game:**

   ```bash
   python3 main.py
   ```

   Next time, only `cd` to the folder, run `source .venv/bin/activate` and start the game.

### Linux

Same as macOS. Install Python 3 and `venv` first if needed (Debian and Ubuntu: `sudo apt install python3 python3-venv`), then follow the macOS steps 2 to 4.

### Playing

The game boots and asks you to type `connect`. Then you start in the training folder. Type `restart` after a game ends to play again. Press `Ctrl+C` or `Ctrl+Q` to quit.

For the best look, use **Windows Terminal** on Windows and **iTerm2** or the built-in **Terminal** on macOS. The old Windows `cmd` window shows colours and the status panel poorly.

### If it will not start

| Message | Fix |
|---|---|
| `can't open file '...main.py': No such file or directory` | The terminal is in the wrong folder. `cd` into the game folder and check `main.py` is listed with `dir` (Windows) or `ls` (macOS and Linux) |
| `No module named 'textual'` | Install it: `py -m pip install textual` (Windows) or, with the virtual environment active, `python3 -m pip install textual` |
| `externally-managed-environment` (macOS, Linux) | Use the virtual environment from macOS step 3. Do not use `--break-system-packages` |
| `python` is not recognised, or Windows opens the Microsoft Store | Install Python from python.org with **Add python.exe to PATH** ticked, then use `py` instead of `python` |
| `command not found: python` (macOS, Linux) | Use `python3` instead of `python` |
| `command not found: pip` | Use `python3 -m pip` (macOS, Linux) or `py -m pip` (Windows) |
| `ImportError` or `ModuleNotFoundError` naming one of the game's files | That file is missing or misnamed. Check the file list at the top of this section |
| The screen is cut off, squashed or garbled | Maximise the window and make the font smaller (about 120 columns by 35 rows). On Windows, switch to Windows Terminal |
| PowerShell says running scripts is disabled (only if you use a virtual environment on Windows) | Use `cmd` instead, or run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |
| A `[DIALOGUE FILE]` warning appears after `connect` | `dialogue_tree.json` is missing or has a mistake. See "Dialogue" below |

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

**Exploring.** Browse the mainframe with `ls`, `cd` and `tree`, and read files with `open`. Some files are dangerous, so `inspect` a file first to see its risk level. Opening certain files can wake something up.

**Defending.** When you are attacked, your three vitals (CPU, RAM and heartbeat) climb every second, and the more dangerous the attack the faster they climb. One of five of your own files is the source. Use `inspect` to work out which one, then `encrypt` it to cure it, or `delete` it. Encrypting the wrong file makes things worse. If any vital maxes out, you flatline. If you take too long, the damage becomes permanent and your resting vitals stay higher from then on. Each firewall you raise slows the next attack.

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

**When a conversation starts.** Only files you read with `open` count, and each file counts once. The four training files and the AI's own file do not count, and neither does `inspect`. After the training, the status line `[ files opened: n/20 ]` shows your count. An encrypted file counts once you have breached and read it.

A conversation never opens over an attack or a breach puzzle. It waits until the attack is cleared, then starts.

**If a conversation never appears.** Check the line the game prints just after `connect`. If `dialogue_tree.json` is missing, is not next to `main.py`, is not valid JSON, or points at a node that does not exist, the game prints a `[DIALOGUE FILE]` warning saying exactly what is wrong. A working file prints `[DIALOGUE] loaded: N conversations ready.` instead. If you do not see that line, the game is not running the current `main.py`, `director.py` and `dialogue_tree.json`.

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

**Spoiler note:** `POOL_SIZE` and the takeover limit (`LOST_FILE_LIMIT` in `Defend_gameplay.py`) are both 5, on purpose. A player who deletes that many files in total is taken over, and the game gives no warning. Keep `POOL_SIZE` at least as large as `LOST_FILE_LIMIT`, or a defense may not offer enough files to reach it. You may want to remove this paragraph from any copy of the README that players will read.