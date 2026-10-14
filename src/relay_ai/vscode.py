import json
from pathlib import Path

from relay_ai import console
from relay_ai.content import asset
from relay_ai.textfile import line_ending, read_text, write_text

EXTENSIONS_CONFIG = Path('.vscode') / 'extensions.json'
MCP_CONFIG = Path('.vscode') / 'mcp.json'


def add_extension_recommendations(project: Path) -> list[str]:
    source = asset('extensions.json')
    if not source.is_file():
        return []

    recommended = json.loads(source.read_text(encoding='utf-8'))['recommendations']
    config = _load(project, EXTENSIONS_CONFIG)
    if config is None:
        _warn_not_plain_json(EXTENSIONS_CONFIG, recommended)
        return []

    project_recommendations = config.setdefault('recommendations', [])
    missing = [extension for extension in recommended if extension not in project_recommendations]
    if not missing:
        return []

    console.info(
        f'Recommending VS Code extensions in {EXTENSIONS_CONFIG.as_posix()}: {", ".join(missing)}'
    )
    project_recommendations.extend(missing)
    _save(project, EXTENSIONS_CONFIG, config)
    return missing


def add_mcp_servers(project: Path) -> list[str]:
    source = asset('mcp.json')
    if not source.is_file():
        return []

    servers = json.loads(source.read_text(encoding='utf-8'))['servers']
    config = _load(project, MCP_CONFIG)
    if config is None:
        _warn_not_plain_json(MCP_CONFIG, servers)
        return []

    project_servers = config.setdefault('servers', {})
    missing = {name: server for name, server in servers.items() if name not in project_servers}
    if not missing:
        return []

    console.info(f'Adding MCP servers to {MCP_CONFIG.as_posix()}: {", ".join(missing)}')
    project_servers.update(missing)
    _save(project, MCP_CONFIG, config)
    return list(missing)


def is_empty_config(project: Path, config: Path) -> bool:
    content = _load(project, config)
    return content is not None and not any(content.values())


def managed_extensions() -> list[str]:
    source = asset('extensions.json')
    if not source.is_file():
        return []
    return json.loads(source.read_text(encoding='utf-8'))['recommendations']


def managed_mcp_servers() -> list[str]:
    source = asset('mcp.json')
    if not source.is_file():
        return []
    return list(json.loads(source.read_text(encoding='utf-8'))['servers'])


def remove_extension_recommendations(project: Path, extensions: list[str]) -> None:
    if not (project / EXTENSIONS_CONFIG).exists():
        return
    config = _load(project, EXTENSIONS_CONFIG)
    if config is None:
        _warn_not_plain_json(EXTENSIONS_CONFIG, extensions)
        return
    recommendations = config.get('recommendations', [])
    config['recommendations'] = [item for item in recommendations if item not in extensions]
    _save(project, EXTENSIONS_CONFIG, config)


def remove_mcp_servers(project: Path, servers: list[str]) -> None:
    if not (project / MCP_CONFIG).exists():
        return
    config = _load(project, MCP_CONFIG)
    if config is None:
        _warn_not_plain_json(MCP_CONFIG, servers)
        return
    for server in servers:
        config.get('servers', {}).pop(server, None)
    _save(project, MCP_CONFIG, config)


def _load(project: Path, config: Path) -> dict | None:
    config_file = project / config
    if not config_file.exists():
        return {}
    try:
        return json.loads(config_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None


def _save(project: Path, config: Path, content: dict) -> None:
    config_file = project / config
    ending = line_ending(read_text(config_file))
    write_text(config_file, f'{json.dumps(content, indent=2)}\n', ending)


def _warn_not_plain_json(config: Path, entries: dict[str, dict] | list[str]) -> None:
    console.warn(
        f'{config.as_posix()} is not plain JSON (comments?), so it was left untouched. '
        f'Update these entries by hand: {json.dumps(entries)}'
    )
