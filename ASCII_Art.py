def frame(art: str, pad: int = 1) -> str:
    lines = art.strip("\n").split("\n")
    width = max(len(line) for line in lines)
    edge = "-" * (width + 2 * pad)
    body = ["|" + " " * pad + line.ljust(width) + " " * pad + "|" for line in lines]
    return "\n".join(["." + edge + "."] + body + ["'" + edge + "'"])

# Define the variables here so user_file_system.py can import them!
Takeover = r"""
[ Replace this with your Takeover ASCII art ]
"""

Daughter = r"""
[ Replace this with your Daughter ASCII art ]
"""

Appartment = r"""
[ Replace this with your Appartment ASCII art ]
"""

Together = r"""
[ Replace this with your Together ASCII art ]
"""

Smile = r"""
[ Replace this with your Smile ASCII art ]
"""