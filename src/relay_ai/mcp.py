import json
from pathlib import Path

from relay_ai import console
from relay_ai.content import asset

MCP_CONFIG = Path('.vscode') / 'mcp.json'


def add_mcp_servers(project: Path) -> None:
    source = asset('mcp.json')
    if not source.is_file():
        return

    servers = json.loads(source.read_text(encoding='utf-8'))['servers']
    config_file = project / MCP_CONFIG
    try:
        config = json.loads(config_file.read_text(encoding='utf-8')) if config_file.exists() else {}
    except json.JSONDecodeError:
        console.warn(
            f'{MCP_CONFIG.as_posix()} is not plain JSON (comments?), so it was left untouched. '
            f'Add these servers by hand: {json.dumps(servers)}'
        )
        return

    project_servers = config.setdefault('servers', {})
    missing = {name: server for name, server in servers.items() if name not in project_servers}
    if not missing:
        return

    console.info(f'Adding MCP servers to {MCP_CONFIG.as_posix()}: {", ".join(missing)}')
    project_servers.update(missing)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(f'{json.dumps(config, indent=2)}\n', encoding='utf-8')
