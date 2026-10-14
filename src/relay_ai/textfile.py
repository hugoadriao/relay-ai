from pathlib import Path


def line_ending(content: str) -> str:
    return '\r\n' if '\r\n' in content else '\n'


def read_text(path: Path) -> str:
    if not path.exists():
        return ''
    with path.open(encoding='utf-8', newline='') as file:
        return file.read()


def write_text(path: Path, content: str, ending: str = '\n') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.replace('\r\n', '\n').replace('\n', ending)
    with path.open('w', encoding='utf-8', newline='') as file:
        file.write(normalized)
