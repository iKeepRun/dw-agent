from pathlib import Path


def load_prompt(name:str)->str:
    path=Path(__file__).parents[2]/ "prompt" / f"{name}.prompt"

    return path.read_text(encoding="utf-8")