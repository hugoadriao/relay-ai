from pathlib import Path

from relay_ai import console
from relay_ai.blocks import read_block
from relay_ai.content import remove_installed
from relay_ai.errors import SetupError
from relay_ai.git import is_git_repository, remove_exclusions
from relay_ai.graphify import GRAPHIFY_IGNORE_FILE, remove_from_graphify_ignore
from relay_ai.graphify import uninstall_from_project as uninstall_graphify
from relay_ai.install import AGENTS_DIR, SKILLS_DIR, installed_manifest
from relay_ai.instructions import (
    COPILOT_INSTRUCTIONS,
    SECTION_END,
    SECTION_START,
    remove_specialists_section,
)
from relay_ai.manifest import MANIFEST_FILE, Manifest, remove_manifest
from relay_ai.vscode import (
    EXTENSIONS_CONFIG,
    MCP_CONFIG,
    is_empty_config,
    remove_extension_recommendations,
    remove_mcp_servers,
)

EMPTY_DIRS = (AGENTS_DIR, SKILLS_DIR, Path('.github'), Path('.vscode'))


def uninstall(project: Path, assume_yes: bool, graphify: bool) -> bool:
    if not project.is_dir():
        raise SetupError(f'project folder not found: {project}')
    manifest = installed_manifest(project)
    if manifest is None and not graphify:
        raise SetupError(
            f'RelayAI is not installed in this project (no {MANIFEST_FILE.as_posix()}).'
        )

    plan = _plan(project, manifest, graphify)
    console.info('This will remove from this project:')
    for item in plan:
        print(f'    - {item}')
    print('    Nothing else is touched: your own agents, skills and settings stay as they are.')
    if not assume_yes and not _confirm():
        console.info('Nothing was removed.')
        return False

    if graphify:
        uninstall_graphify(project)
    if manifest is None:
        console.info("Graphify's setup was removed from this project.")
        return True

    for agent in manifest.agents:
        remove_installed(project / AGENTS_DIR / agent)
    for skill in manifest.skills:
        remove_installed(project / SKILLS_DIR / skill)
    remove_specialists_section(project)
    remove_mcp_servers(project, manifest.mcp_servers)
    remove_extension_recommendations(project, manifest.extensions)
    remove_from_graphify_ignore(project, manifest.graphify_ignore)
    for created in manifest.created_files:
        _delete_if_empty(project, Path(created))
    remove_manifest(project)
    if is_git_repository(project):
        remove_exclusions(project)
    for directory in EMPTY_DIRS:
        _remove_if_empty(project / directory)

    console.info('RelayAI was removed from this project.')
    return True


def _confirm() -> bool:
    try:
        answer = input('Remove these? [y/N] ')
    except EOFError:
        return False
    return answer.strip().lower() in ('y', 'yes')


def _delete_if_empty(project: Path, created: Path) -> None:
    path = project / created
    if not path.exists():
        return
    if created in (MCP_CONFIG, EXTENSIONS_CONFIG):
        empty = is_empty_config(project, created)
    else:
        empty = not path.read_text(encoding='utf-8').strip()
    if empty:
        path.unlink()


def _plan(project: Path, manifest: Manifest | None, graphify: bool) -> list[str]:
    graphify_setup = (
        "Graphify's setup in this project: its git hooks and its section of "
        f'{COPILOT_INSTRUCTIONS.as_posix()} (the graph in graphify-out/ is kept)'
    )
    if manifest is None:
        return [graphify_setup]

    plan = [f'agent {AGENTS_DIR.as_posix()}/{agent}' for agent in manifest.agents]
    plan += [f'skill {SKILLS_DIR.as_posix()}/{skill}/' for skill in manifest.skills]
    if read_block(project / COPILOT_INSTRUCTIONS, SECTION_START, SECTION_END):
        plan.append(f'the relay-ai section of {COPILOT_INSTRUCTIONS.as_posix()}')
    if manifest.mcp_servers:
        plan.append(f'MCP servers in {MCP_CONFIG.as_posix()}: {", ".join(manifest.mcp_servers)}')
    if manifest.extensions:
        recommended = ', '.join(manifest.extensions)
        plan.append(f'extension recommendations in {EXTENSIONS_CONFIG.as_posix()}: {recommended}')
    if manifest.graphify_ignore:
        lines = ', '.join(manifest.graphify_ignore)
        plan.append(f'lines added to {GRAPHIFY_IGNORE_FILE}: {lines}')
    if manifest.created_files:
        created = ', '.join(manifest.created_files)
        plan.append(f'files RelayAI created, if nothing else is left in them: {created}')
    plan.append(f'{MANIFEST_FILE.as_posix()} and the RelayAI block in .git/info/exclude')
    if graphify:
        plan.append(graphify_setup)
    return plan


def _remove_if_empty(directory: Path) -> None:
    if directory.is_dir() and not any(directory.iterdir()):
        directory.rmdir()
