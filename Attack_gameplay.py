import random

from rich.text import Text

PIPES = ['═', '║', '╔', '╗', '╚', '╝', '╠', '╣', '╦', '╩', '╬']

ROTATIONS = {
    '═': '║', '║': '═',
    '╔': '╗', '╗': '╝', '╝': '╚', '╚': '╔',
    '╠': '╦', '╦': '╣', '╣': '╩', '╩': '╠',
    '╬': '╬',
}

# Defines which directions each pipe character opens up: (top, right, bottom, left)
CONNECTIONS = {
    '═': (False, True, False, True),
    '║': (True, False, True, False),
    '╔': (False, True, True, False),
    '╗': (False, False, True, True),
    '╚': (True, True, False, False),
    '╝': (True, False, False, True),
    '╠': (True, True, True, False),
    '╣': (True, False, True, True),
    '╦': (False, True, True, True),
    '╩': (True, True, False, True),
    '╬': (True, True, True, True),
}

# Direction indexes match CONNECTIONS: 0 = up, 1 = right, 2 = down, 3 = left
STEPS = ((-1, 0), (0, 1), (1, 0), (0, -1))


def can_link(pipe, side_a, side_b) -> bool:
    """True if some rotation of `pipe` opens both `side_a` and `side_b`."""
    for _ in range(4):
        conns = CONNECTIONS.get(pipe, (False, False, False, False))
        if conns[side_a] and conns[side_b]:
            return True
        pipe = ROTATIONS.get(pipe, pipe)
    return False


def check_file_access(sys_fs, filename, game_session=None):
    """
    Checks the file encryption. If encrypted, initializes and returns
    the DataPipelineGame session required to decrypt/access the file.

    Returns a dict. Anything the player should read is in "messages" so the
    caller can print it in the UI (print() would corrupt the Textual screen).
    """
    if filename not in sys_fs:
        return {"status": "error", "message": f"File '{filename}' not found in the system."}

    file_data = sys_fs[filename]
    is_encrypted = file_data.get("Encrypted", False)

    messages = [f"\n--- ACCESS ATTEMPT: {filename} ---"]

    if is_encrypted:
        messages += [
            "[!] ACCESS DENIED: File is ENCRYPTED.",
            "[!] Initiating Data Breach...",
        ]

        # Create a new game instance if one isn't provided
        game = game_session or DataPipelineGame(size=5)
        initial_board = game.start_game()

        return {
            "status": "encrypted",
            "action": "trigger_minigame",
            "file": filename,
            "risk": file_data.get("risk"),
            "game_instance": game,
            "display": initial_board,
            "messages": messages,
        }

    messages.append("[+] ACCESS GRANTED: File is unencrypted.")
    return {
        "status": "decrypted",
        "action": "open_file",
        "file": filename,
        "messages": messages,
    }


class DataPipelineGame:
    def __init__(self, size=5):
        self.size = size
        self.grid = []
        self.last_rotated = None  # Tracks only the most recent rotation
        self.game_active = False

    def is_solvable(self) -> bool:
        """True if some set of rotations connects [0,0] to the far corner."""
        end = (self.size - 1, self.size - 1)

        def walk(r, c, came_from, seen):
            if (r, c) == end:
                return True
            for side, (dr, dc) in enumerate(STEPS):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < self.size and 0 <= nc < self.size) or (nr, nc) in seen:
                    continue
                if came_from is not None and not can_link(self.grid[r][c], came_from, side):
                    continue
                if walk(nr, nc, (side + 2) % 4, seen | {(nr, nc)}):
                    return True
            return False

        return walk(0, 0, None, {(0, 0)})

    def start_game(self) -> Text:
        self.game_active = True
        self.last_rotated = None

        # Re-roll until the puzzle can actually be won
        while True:
            self.grid = [[random.choice(PIPES) for _ in range(self.size)] for _ in range(self.size)]

            # Designate clear start and end points
            self.grid[0][0] = '╔'
            self.grid[self.size - 1][self.size - 1] = '╝'
            if self.is_solvable():
                break
        return self.render_grid()

    def render_grid(self) -> Text:
        last = self.size - 1
        text = Text()
        text.append("\n[ DATA TRANSMISSION PIPELINE ACTIVE ]\n", style="bold cyan")
        text.append(
            f"> Start: [0,0] (Green)  |  Finish: [{last},{last}] (Magenta)  |  Last Rotated: (Yellow)\n\n",
            style="dim",
        )

        header = "    " + " ".join([str(i) for i in range(self.size)]) + "\n"
        text.append(header, style="bold white")
        text.append("    " + "---" * self.size + "\n", style="dim")

        for r_idx, row in enumerate(self.grid):
            text.append(f" {r_idx} | ")
            for c_idx, pipe in enumerate(row):
                if r_idx == 0 and c_idx == 0:
                    style = "bold green"
                elif r_idx == self.size - 1 and c_idx == self.size - 1:
                    style = "bold magenta"
                elif self.last_rotated == (r_idx, c_idx):
                    style = "bold yellow"  # Highlight ONLY the latest rotation
                else:
                    style = "white"

                text.append(f"{pipe} ", style=style)
            text.append("|\n")

        text.append("    " + "---" * self.size + "\n", style="dim")
        text.append("\n> Commands: rotate <row> <col>  |  transmit", style="cyan")
        return text

    def rotate_pipe(self, args) -> Text:
        if not self.game_active:
            return Text("> Pipeline minigame not active.", style="red")
        if len(args) < 2:
            return Text("> Usage: rotate <row> <col>", style="red")
        try:
            r, c = int(args[0]), int(args[1])
        except ValueError:
            return Text("> Error: Row and column must be numbers.", style="red")

        if 0 <= r < self.size and 0 <= c < self.size:
            current_pipe = self.grid[r][c]
            self.grid[r][c] = ROTATIONS.get(current_pipe, current_pipe)
            self.last_rotated = (r, c)  # Set the new latest rotated cell
            return self.render_grid()
        return Text(f"> Coordinates out of bounds (0-{self.size - 1}).", style="red")

    def check_transmission(self) -> tuple[bool, Text]:
        if not self.game_active:
            return False, Text("> Transmission loop not active.", style="red")

        # Breadth-First Search to check valid pipeline connectivity from [0,0] to [size-1, size-1]
        visited = set()
        queue = [(0, 0)]
        connected = False

        while queue:
            r, c = queue.pop(0)
            if (r, c) == (self.size - 1, self.size - 1):
                connected = True
                break

            if (r, c) in visited:
                continue
            visited.add((r, c))

            current_pipe = self.grid[r][c]
            curr_conns = CONNECTIONS.get(current_pipe, (False, False, False, False))

            # Check neighbors: Top (0), Right (1), Bottom (2), Left (3)
            neighbors = [
                (r - 1, c, 0, 2),  # Up
                (r, c + 1, 1, 3),  # Right
                (r + 1, c, 2, 0),  # Down
                (r, c - 1, 3, 1),  # Left
            ]

            for nr, nc, out_idx, in_idx in neighbors:
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if (nr, nc) not in visited:
                        neighbor_pipe = self.grid[nr][nc]
                        neigh_conns = CONNECTIONS.get(neighbor_pipe, (False, False, False, False))

                        # If current pipe has an opening pointing to neighbor AND neighbor opens back
                        if curr_conns[out_idx] and neigh_conns[in_idx]:
                            queue.append((nr, nc))

        if connected:
            self.game_active = False
            return True, Text("\n=== TRANSMISSION SEVERED: GHOST PACKET CONTAINED ===", style="bold green")
        return False, Text("\n> TRANSMISSION FAILED: Path is incomplete or blocked.", style="red")