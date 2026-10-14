from pathlib import Path


def read_block(path: Path, start: str, end: str) -> list[str]:
    content = _read(path)
    start_index = content.find(start)
    end_index = content.find(end)
    if start_index == -1 or end_index < start_index:
        return []
    return content[start_index + len(start) : end_index].splitlines()


def upsert_block(path: Path, start: str, end: str, block: str) -> None:
    content = _read(path)
    start_index = content.find(start)
    end_index = content.find(end)
    if start_index != -1 and end_index > start_index:
        tail = content[end_index + len(end) :].removeprefix('\r\n').removeprefix('\n')
        content = f'{content[:start_index]}{block}{tail}'
    elif content:
        separator = '\n' if content.endswith('\n') else '\n\n'
        content = f'{content}{separator}{block}'
    else:
        content = block

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as file:
        file.write(content)


def _read(path: Path) -> str:
    if not path.exists():
        return ''
    with path.open(encoding='utf-8', newline='') as file:
        return file.read()
