from pathlib import Path

from relay_ai.textfile import line_ending, read_text, write_text


def read_block(path: Path, start: str, end: str) -> list[str]:
    content = read_text(path)
    start_index = content.find(start)
    end_index = content.find(end)
    if start_index == -1 or end_index < start_index:
        return []
    return content[start_index + len(start) : end_index].splitlines()


def remove_block(path: Path, start: str, end: str) -> bool:
    content = read_text(path)
    start_index = content.find(start)
    end_index = content.find(end)
    if start_index == -1 or end_index < start_index:
        return False

    head = content[:start_index]
    tail = content[end_index + len(end) :].removeprefix('\r\n').removeprefix('\n')
    if not tail and head.strip():
        head = f'{head.rstrip()}\n'
    write_text(path, f'{head}{tail}', line_ending(content))
    return True


def upsert_block(path: Path, start: str, end: str, block: str) -> None:
    content = read_text(path)
    start_index = content.find(start)
    end_index = content.find(end)
    if start_index != -1 and end_index > start_index:
        tail = content[end_index + len(end) :].removeprefix('\r\n').removeprefix('\n')
        updated = f'{content[:start_index]}{block}{tail}'
    elif content:
        separator = '\n' if content.endswith('\n') else '\n\n'
        updated = f'{content}{separator}{block}'
    else:
        updated = block
    write_text(path, updated, line_ending(content))
