import json
from pathlib import Path

from relay_ai import console
from relay_ai.textfile import line_ending, read_text, write_text

SCHEMA_KEY = '$schema'


def is_empty_config(path: Path) -> bool:
    content = load_json(path)
    if content is None:
        return False
    return not any(value for key, value in content.items() if key != SCHEMA_KEY)


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None


def save_json(path: Path, content: dict) -> None:
    ending = line_ending(read_text(path))
    write_text(path, f'{json.dumps(content, indent=2)}\n', ending)


def warn_not_plain_json(path: Path, entries: dict | list[str]) -> None:
    console.warn(
        f'{path.as_posix()} is not plain JSON (comments?), so it was left untouched. '
        f'Update these entries by hand: {json.dumps(entries)}'
    )
