from dataclasses import dataclass
from pathlib import Path

from relay_ai.errors import SetupError


@dataclass(frozen=True)
class Platform:
    agent_suffix: str
    agents_dir: Path
    graphify_install: tuple[str, ...]
    graphify_marker: Path
    graphify_uninstall: tuple[tuple[str, ...], ...]
    instructions_file: Path
    label: str
    mcp_config: Path
    mcp_key: str
    name: str


COPILOT = Platform(
    agent_suffix='.agent.md',
    agents_dir=Path('.github') / 'agents',
    graphify_install=('vscode', 'install'),
    graphify_marker=Path('.github') / 'copilot-instructions.md',
    graphify_uninstall=(('vscode', 'uninstall'), ('copilot', 'install')),
    instructions_file=Path('.github') / 'copilot-instructions.md',
    label='GitHub Copilot (VS Code)',
    mcp_config=Path('.vscode') / 'mcp.json',
    mcp_key='servers',
    name='copilot',
)
OPENCODE = Platform(
    agent_suffix='.md',
    agents_dir=Path('.opencode') / 'agents',
    graphify_install=('opencode', 'install'),
    graphify_marker=Path('.opencode') / 'plugins' / 'graphify.js',
    graphify_uninstall=(('opencode', 'uninstall'),),
    instructions_file=Path('AGENTS.md'),
    label='OpenCode',
    mcp_config=Path('opencode.json'),
    mcp_key='mcp',
    name='opencode',
)
PLATFORMS = (COPILOT, OPENCODE)


def platforms_named(names: list[str]) -> list[Platform]:
    unknown = set(names) - {platform.name for platform in PLATFORMS}
    if unknown:
        raise SetupError(f'unknown platform(s): {", ".join(sorted(unknown))}')
    return [platform for platform in PLATFORMS if platform.name in names]
