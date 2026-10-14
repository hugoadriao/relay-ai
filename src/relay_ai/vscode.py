import json
from pathlib import Path

from relay_ai import console
from relay_ai.content import asset

EXTENSIONS_CONFIG = Path('.vscode') / 'extensions.json'
MCP_CONFIG = Path('.vscode') / 'mcp.json'


def add_extension_recommendations(project: Path) -> None:
    source = asset('extensions.json')
    if not source.is_file():
        return

    recommended = json.loads(source.read_text(encoding='utf-8'))['recommendations']
    config = _load(project, EXTENSIONS_CONFIG, recommended)
    if config is None:
        return

    project_recommendations = config.setdefault('recommendations', [])
    missing = [extension for extension in recommended if extension not in project_recommendations]
    if not missing:
        return

    console.info(
        f'Recommending VS Code extensions in {EXTENSIONS_CONFIG.as_posix()}: {", ".join(missing)}'
    )
    project_recommendations.extend(missing)
    _save(project, EXTENSIONS_CONFIG, config)


def add_mcp_servers(project: Path) -> None:
    source = asset('mcp.json')
    if not source.is_file():
        return

    servers = json.loads(source.read_text(encoding='utf-8'))['servers']
    config = _load(project, MCP_CONFIG, servers)
    if config is None:
        return

    project_servers = config.setdefault('servers', {})
    missing = {name: server for name, server in servers.items() if name not in project_servers}
    if not missing:
        return

    console.info(f'Adding MCP servers to {MCP_CONFIG.as_posix()}: {", ".join(missing)}')
    project_servers.update(missing)
    _save(project, MCP_CONFIG, config)


def _load(project: Path, config: Path, additions: dict[str, dict] | list[str]) -> dict | None:
    config_file = project / config
    if not config_file.exists():
        return {}
    try:
        return json.loads(config_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        console.warn(
            f'{config.as_posix()} is not plain JSON (comments?), so it was left untouched. '
            f'Add these entries by hand: {json.dumps(additions)}'
        )
        return None


def _save(project: Path, config: Path, content: dict) -> None:
    config_file = project / config
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(f'{json.dumps(content, indent=2)}\n', encoding='utf-8')
