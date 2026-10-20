import json
from pathlib import Path

from relay_ai import console
from relay_ai.content import asset, install_archive_skill
from relay_ai.errors import SetupError
from relay_ai.jsonfile import SCHEMA_KEY, load_json, save_json, warn_not_plain_json
from relay_ai.platforms import COPILOT, OPENCODE, PLATFORMS, Platform

KEY_SEPARATOR = '#'
OPENCODE_SCHEMA = 'https://opencode.ai/config.json'


def add_mcp_servers(project: Path, platform: Platform, owned: list[str]) -> list[str]:
    servers = {name: _render(platform, server) for name, server in managed_servers().items()}
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
    outdated = {
        name: server
        for name, server in servers.items()
        if server_key(platform, name) in owned and project_servers.get(name) not in (None, server)
    }
    if not missing and not outdated:
        return []

    config_name = platform.mcp_config.as_posix()
    if missing:
        console.info(f'Adding MCP servers to {config_name}: {", ".join(missing)}')
    if outdated:
        console.info(f'Updating MCP servers in {config_name}: {", ".join(outdated)}')
    project_servers.update(missing | outdated)
    save_json(config_file, config)
    return [server_key(platform, name) for name in missing]


def install_server_skills(target: Path, owned: set[str]) -> list[str]:
    installed = []
    for server in managed_servers().values():
        skill = server.get('skill')
        if skill is None:
            continue
        console.info(f'Downloading the {skill["name"]} skill ({skill["archive"]})...')
        try:
            if install_archive_skill(
                archive_url=skill['archive'],
                name=skill['name'],
                owned=owned,
                skill_path=skill['path'],
                target=target,
            ):
                installed.append(skill['name'])
        except SetupError as err:
            console.warn(
                f'{err}: the {skill["name"]} skill was not installed or updated. The debugger '
                'still works without it; run `relay-ai update` once GitHub is reachable.'
            )
            if skill['name'] in owned and (target / skill['name']).is_dir():
                installed.append(skill['name'])
    return installed


def legacy_server_key(key: str) -> str:
    return key if KEY_SEPARATOR in key else server_key(COPILOT, key)


def managed_server_keys(platforms: list[Platform]) -> set[str]:
    return {server_key(platform, name) for platform in platforms for name in managed_servers()}


def managed_servers() -> dict[str, dict]:
    source = asset('mcp.json')
    if not source.is_file():
        return {}
    servers = json.loads(source.read_text(encoding='utf-8'))['servers']
    return {
        name: _with_version(server, server.get('version', '')) for name, server in servers.items()
    }


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


def server_names(keys: list[str]) -> set[str]:
    return {key.rpartition(KEY_SEPARATOR)[2] for key in keys}


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


def _with_version(value: object, version: str) -> object:
    if isinstance(value, str):
        return value.replace('{version}', version)
    if isinstance(value, list):
        return [_with_version(item, version) for item in value]
    if isinstance(value, dict):
        return {key: _with_version(item, version) for key, item in value.items()}
    return value
