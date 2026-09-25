from pathlib import Path

directory = Path(__file__).resolve().parent.parent / "prompts"


def load(name: str) -> str:
    return (directory / f"{name}.txt").read_text()
