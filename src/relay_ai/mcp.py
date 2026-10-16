import json
from pathlib import Path

from relay_ai import console
from relay_ai.content import asset
from relay_ai.jsonfile import SCHEMA_KEY, load_json, save_json, warn_not_plain_json
from relay_ai.platforms import COPILOT, OPENCODE, PLATFORMS, Platform

KEY_SEPARATOR = '#'
OPENCODE_SCHEMA = 'https://opencode.ai/config.json'


def add_mcp_servers(project: Path, platform: Platform) -> list[str]:
    servers = {name: _render(platform, server) for name, server in _managed_servers().items()}
    if not servers:
        return []

    config_file = project / platform.mcp_config
    config = load_json(config_file)
    if config is None:
        warn_not_plain_json(platform.mcp_config, servers)
        return []

    if not config and platform is OPENCODE:
        config[SCHEMA_KEY] = OPENCODE_SCHEMA
    project_servers = config.setdefault(platform.mcp_key, {})
    missing = {name: server for name, server in servers.items() if name not in project_servers}
    if not missing:
        return []

    console.info(f'Adding MCP servers to {platform.mcp_config.as_posix()}: {", ".join(missing)}')
    project_servers.update(missing)
    save_json(config_file, config)
    return [server_key(platform, name) for name in missing]


def legacy_server_key(key: str) -> str:
    return key if KEY_SEPARATOR in key else server_key(COPILOT, key)


def managed_server_keys(platforms: list[Platform]) -> set[str]:
    return {server_key(platform, name) for platform in platforms for name in _managed_servers()}


def remove_mcp_servers(project: Path, keys: list[str]) -> None:
    for platform in PLATFORMS:
        names = [name for name in (_split(key, platform) for key in keys) if name]
        config_file = project / platform.mcp_config
        if not names or not config_file.exists():
            continue
        config = load_json(config_file)
        if config is None:
            warn_not_plain_json(platform.mcp_config, names)
            continue
        for name in names:
            config.get(platform.mcp_key, {}).pop(name, None)
        save_json(config_file, config)


def server_key(platform: Platform, name: str) -> str:
    return f'{platform.mcp_config.as_posix()}{KEY_SEPARATOR}{name}'


def _managed_servers() -> dict[str, dict]:
    source = asset('mcp.json')
    if not source.is_file():
        return {}
    return json.loads(source.read_text(encoding='utf-8'))['servers']


def _render(platform: Platform, server: dict) -> dict:
    if platform is COPILOT:
        if 'url' in server:
            return {'type': 'http', 'url': server['url']}
        return {'args': server['command'][1:], 'command': server['command'][0], 'type': 'stdio'}
    if 'url' in server:
        return {'enabled': True, 'type': 'remote', 'url': server['url']}
    return {'command': server['command'], 'enabled': True, 'type': 'local'}


def _split(key: str, platform: Platform) -> str | None:
    config, _, name = key.rpartition(KEY_SEPARATOR)
    return name if config == platform.mcp_config.as_posix() else None
