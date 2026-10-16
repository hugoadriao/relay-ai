import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

MANIFEST_FILE = Path('.github') / 'relay-ai.json'


@dataclass
class Manifest:
    agents: list[str] = field(default_factory=list)
    created_files: list[str] = field(default_factory=list)
    graphify_ignore: list[str] = field(default_factory=list)
    mcp_servers: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)


def load_manifest(project: Path) -> Manifest | None:
    manifest_file = project / MANIFEST_FILE
    if not manifest_file.exists():
        return None
    content = json.loads(manifest_file.read_text(encoding='utf-8'))
    known = {item.name for item in fields(Manifest)}
    return Manifest(**{key: value for key, value in content.items() if key in known})


def remove_manifest(project: Path) -> None:
    (project / MANIFEST_FILE).unlink(missing_ok=True)


def save_manifest(project: Path, manifest: Manifest) -> None:
    manifest_file = project / MANIFEST_FILE
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    content = {key: sorted(set(values)) for key, values in asdict(manifest).items()}
    manifest_file.write_text(f'{json.dumps(content, indent=2)}\n', encoding='utf-8')
