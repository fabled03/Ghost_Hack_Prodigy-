
def frame(art: str, pad: int = 1) -> str:
    lines = art.strip("\n").split("\n")
    width = max(len(line) for line in lines)
    edge = "-" * (width + 2 * pad)
    body = ["|" + " " * pad + line.ljust(width) + " " * pad + "|" for line in lines]
    return "\n".join(["." + edge + "."] + body + ["'" + edge + "'"])

