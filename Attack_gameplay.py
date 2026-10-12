import random
from rich.text import Text

PIPES = ['═', '║', '╔', '╗', '╚', '╝', '╠', '╣', '╦', '╩', '╬']

ROTATIONS = {
    '═': '║', '║': '═',
    '╔': '╗', '╗': '╝', '╝': '╚', '╚': '╔',
    '╠': '╦', '╦': '╣', '╣': '╩', '╩': '╠',
    '╬': '╬'
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

class DataPipelineGame:
    def __init__(self, size=5):
        self.size = size
        self.grid = []
        self.last_rotated = None  # Tracks only the most recent rotation
        self.game_active = False

    def start_game(self) -> Text:
        self.game_active = True
        self.last_rotated = None
        self.grid = [[random.choice(PIPES) for _ in range(self.size)] for _ in range(self.size)]
        
        # Designate clear start and end points
        self.grid[0][0] = '╔'
        self.grid[self.size - 1][self.size - 1] = '╝'
        return self.render_grid()

    def render_grid(self) -> Text:
        text = Text()
        text.append("\n[ DATA TRANSMISSION PIPELINE ACTIVE ]\n", style="bold cyan")
        text.append("> Start: [0,0] (Green)  |  Finish: [4,4] (Magenta)  |  Last Rotated: (Yellow)\n\n", style="dim")
        
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
            if 0 <= r < self.size and 0 <= c < self.size:
                current_pipe = self.grid[r][c]
                self.grid[r][c] = ROTATIONS.get(current_pipe, current_pipe)
                self.last_rotated = (r, c)  # Set the new latest rotated cell
                return self.render_grid()
            else:
                return Text(f"> Coordinates out of bounds (0-{self.size-1}).", style="red")
        except ValueError:
            return Text("> Error: Row and column must be numbers.", style="red")

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
                (r, c - 1, 3, 1)   # Left
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
        else:
            return False, Text("\n> TRANSMISSION FAILED: Path is incomplete or blocked.", style="red")