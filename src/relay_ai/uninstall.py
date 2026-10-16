from pathlib import Path

from relay_ai import console
from relay_ai.content import remove_if_empty, remove_installed
from relay_ai.errors import SetupError
from relay_ai.git import is_git_repository, remove_exclusions
from relay_ai.graphify import GRAPHIFY_IGNORE_FILE, remove_from_graphify_ignore
from relay_ai.graphify import uninstall_from_project as uninstall_graphify
from relay_ai.install import LEGACY_SKILLS_DIR, SKILLS_DIR, installed_manifest
from relay_ai.instructions import has_specialists_section, remove_specialists_section
from relay_ai.jsonfile import is_empty_config
from relay_ai.manifest import MANIFEST_FILE, Manifest, remove_manifest
from relay_ai.mcp import remove_mcp_servers
from relay_ai.platforms import PLATFORMS, Platform

EMPTY_DIRS = (
    *[platform.agents_dir for platform in PLATFORMS],
    SKILLS_DIR,
    LEGACY_SKILLS_DIR,
    SKILLS_DIR.parent,
    Path('.opencode'),
    Path('.github'),
    Path('.vscode'),
)


def uninstall(project: Path, assume_yes: bool, graphify: bool) -> bool:
    if not project.is_dir():
        raise SetupError(f'project folder not found: {project}')
    manifest = installed_manifest(project)
    if manifest is None and not graphify:
        raise SetupError(
            f'RelayAI is not installed in this project (no {MANIFEST_FILE.as_posix()}).'
        )

    graphify_platforms = _graphify_platforms(project, manifest) if graphify else []
    plan = _plan(project, manifest, graphify_platforms)
    console.info('This will remove from this project:')
    for item in plan:
        print(f'    - {item}')
    print('    Nothing else is touched: your own agents, skills and settings stay as they are.')
    if not assume_yes and not _confirm():
        console.info('Nothing was removed.')
        return False

    if graphify:
        uninstall_graphify(project, graphify_platforms)
    if manifest is None:
        console.info("Graphify's setup was removed from this project.")
        return True

    for path in manifest.agents + manifest.skills:
        remove_installed(project / path)
    for platform in PLATFORMS:
        remove_specialists_section(project, platform)
    remove_mcp_servers(project, manifest.mcp_servers)
    remove_from_graphify_ignore(project, manifest.graphify_ignore)
    for created in manifest.created_files:
        _delete_if_empty(project / created)
    remove_manifest(project)
    if is_git_repository(project):
        remove_exclusions(project)
    for directory in EMPTY_DIRS:
        remove_if_empty(project / directory)

    console.info('RelayAI was removed from this project.')
    return True


def _confirm() -> bool:
    try:
        answer = input('Remove these? [y/N] ')
    except EOFError:
        return False
    return answer.strip().lower() in ('y', 'yes')


def _delete_if_empty(path: Path) -> None:
    if not path.exists():
        return
    if path.suffix == '.json':
        empty = is_empty_config(path)
    else:
        empty = not path.read_text(encoding='utf-8').strip()
    if empty:
        path.unlink()


def _graphify_platforms(project: Path, manifest: Manifest | None) -> list[Platform]:
    if manifest is not None:
        return [platform for platform in PLATFORMS if platform.name in manifest.platforms]
    return [platform for platform in PLATFORMS if (project / platform.graphify_marker).exists()]


def _plan(project: Path, manifest: Manifest | None, graphify: list[Platform]) -> list[str]:
    plan = []
    if manifest is not None:
        plan += [f'agent {path}' for path in manifest.agents]
        plan += [f'skill {path}/' for path in manifest.skills]
        for platform in PLATFORMS:
            if has_specialists_section(project, platform):
                plan.append(f'the relay-ai section of {platform.instructions_file.as_posix()}')
        if manifest.mcp_servers:
            servers = ', '.join(key.replace('#', ': ') for key in manifest.mcp_servers)
            plan.append(f'MCP servers RelayAI added ({servers})')
        if manifest.graphify_ignore:
            lines = ', '.join(manifest.graphify_ignore)
            plan.append(f'lines added to {GRAPHIFY_IGNORE_FILE}: {lines}')
        if manifest.created_files:
            created = ', '.join(manifest.created_files)
            plan.append(f'files RelayAI created, if nothing else is left in them: {created}')
        plan.append(f'{MANIFEST_FILE.as_posix()} and the RelayAI block in .git/info/exclude')
    for platform in graphify:
        plan.append(
            f"Graphify's setup for {platform.label} and its git hooks "
            '(the graph in graphify-out/ is kept)'
        )
    return plan
