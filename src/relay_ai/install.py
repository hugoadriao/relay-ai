from dataclasses import dataclass
from pathlib import Path

from relay_ai import console
from relay_ai.content import (
    install_mattpocock_skills,
    install_relay_agents,
    install_relay_skills,
    remove_if_empty,
    remove_installed,
)
from relay_ai.errors import SetupError
from relay_ai.git import (
    exclude_from_git,
    excluded_paths,
    is_git_repository,
    modified_tracked_files,
)
from relay_ai.graphify import (
    GRAPHIFY_IGNORE_FILE,
    configure_project,
    ensure_graphify,
    remove_from_graphify_ignore,
)
from relay_ai.instructions import remove_specialists_section, write_specialists_section
from relay_ai.jsonfile import is_empty_config
from relay_ai.manifest import MANIFEST_FILE, Manifest, load_manifest, save_manifest
from relay_ai.mcp import (
    add_mcp_servers,
    legacy_server_key,
    managed_server_keys,
    remove_mcp_servers,
    server_names,
)
from relay_ai.platforms import COPILOT, PLATFORMS, Platform
from relay_ai.prerequisites import prefetch_mcp_servers
from relay_ai.windows import check_path_length

AGENTS_FILE = Path('AGENTS.md')
AUDITS_DIR = Path('docs') / 'audits'
CLAUDE_FILE = Path('CLAUDE.md')
LEGACY_SKILLS_DIR = Path('.github') / 'skills'
SKILLS_DIR = Path('.agents') / 'skills'
SHARED_FILES = tuple(
    dict.fromkeys(
        [
            AGENTS_FILE,
            Path(GRAPHIFY_IGNORE_FILE),
            *[platform.instructions_file for platform in PLATFORMS],
            *[platform.mcp_config for platform in PLATFORMS],
        ]
    )
)


@dataclass(frozen=True)
class Changes:
    added: list[str]
    removed: list[str]
    updated: list[str]


def install(project: Path, platforms: list[Platform] | None, update: bool) -> Changes:
    if not project.is_dir():
        raise SetupError(f'project folder not found: {project}')
    check_path_length(project)

    previous = installed_manifest(project)
    if update and previous is None:
        raise SetupError('RelayAI is not installed in this project: run `relay-ai init` first.')
    previous = previous or Manifest()
    platforms = platforms or [p for p in PLATFORMS if p.name in previous.platforms]
    if not platforms:
        raise SetupError('choose a platform with --platform copilot|opencode|both')

    names = ', '.join(platform.label for platform in platforms)
    console.info(f'{"Updating" if update else "Setting up"} RelayAI in {project} for {names}')
    graphify = ensure_graphify()
    preexisting = [
        path
        for path in SHARED_FILES
        if (project / path).exists() and path.as_posix() not in previous.created_files
    ]
    if not (project / AGENTS_FILE).exists() and not (project / CLAUDE_FILE).exists():
        console.info(f'Creating {AGENTS_FILE} (the instructions file Copilot and OpenCode read)...')
        (project / AGENTS_FILE).touch()

    agents = []
    mcp_servers = []
    for platform in platforms:
        owned = _owned_names(previous.agents, platform.agents_dir)
        platform_agents = install_relay_agents(project, platform, owned)
        write_specialists_section(project, platform, platform_agents)
        agents += [agent.path.as_posix() for agent in platform_agents]
        mcp_servers += add_mcp_servers(project, platform, previous.mcp_servers)
    for platform in PLATFORMS:
        if platform not in platforms:
            remove_specialists_section(project, platform)

    skills_dir = project / SKILLS_DIR
    skills_dir.mkdir(parents=True, exist_ok=True)
    owned = _owned_names(previous.skills, SKILLS_DIR)
    skill_names = install_relay_skills(skills_dir, owned)
    skill_names += install_mattpocock_skills(skills_dir, owned)
    skills = [(SKILLS_DIR / name).as_posix() for name in skill_names]

    for path in [path for path in previous.agents + previous.skills if path not in agents + skills]:
        remove_installed(project / path)
    managed_servers = managed_server_keys(platforms)
    remove_mcp_servers(project, [key for key in previous.mcp_servers if key not in managed_servers])
    for path in previous.created_files:
        if path.endswith('.json') and is_empty_config(project / path):
            (project / path).unlink()
    for directory in [LEGACY_SKILLS_DIR, *[platform.agents_dir for platform in PLATFORMS]]:
        remove_if_empty(project / directory)

    ignored_dirs = [platform.agents_dir for platform in platforms] + [SKILLS_DIR, AUDITS_DIR]
    patterns = {f'{ignored_dir.as_posix()}/' for ignored_dir in ignored_dirs}
    remove_from_graphify_ignore(
        project, [pattern for pattern in previous.graphify_ignore if pattern not in patterns]
    )
    graphify_ignore = configure_project(graphify, project, platforms, ignored_dirs)

    created = [
        path for path in SHARED_FILES if path not in preexisting and (project / path).exists()
    ]
    manifest = Manifest(
        agents=agents,
        created_files=[path.as_posix() for path in created],
        graphify_ignore=[pattern for pattern in previous.graphify_ignore if pattern in patterns]
        + graphify_ignore,
        mcp_servers=[key for key in previous.mcp_servers if key in managed_servers] + mcp_servers,
        platforms=[platform.name for platform in platforms],
        skills=skills,
    )
    save_manifest(project, manifest)
    prefetch_mcp_servers(server_names(manifest.mcp_servers))

    if is_git_repository(project):
        exclude_from_git(
            project, [Path(path) for path in agents + skills] + created + [MANIFEST_FILE]
        )
        for changed in modified_tracked_files(project, preexisting):
            console.warn(
                f'{changed} is tracked by git and was changed by RelayAI; review the diff and '
                'decide whether to commit it.'
            )

    before = set(_labels(previous))
    after = set(_labels(manifest))
    return Changes(
        added=sorted(after - before),
        removed=sorted(before - after),
        updated=sorted(after & before),
    )


def installed_manifest(project: Path) -> Manifest | None:
    manifest = load_manifest(project)
    if manifest is None and is_git_repository(project):
        excluded = excluded_paths(project)
        manifest = _legacy_manifest(excluded) if excluded else None
    return _upgrade(manifest) if manifest is not None else None


def _labels(manifest: Manifest) -> list[str]:
    agents = [f'agent {Path(path).name}' for path in manifest.agents]
    return agents + [f'skill {Path(path).name}' for path in manifest.skills]


def _legacy_manifest(excluded: list[Path]) -> Manifest:
    return Manifest(
        agents=[path.as_posix() for path in excluded if path.parent == COPILOT.agents_dir],
        created_files=[path.as_posix() for path in excluded if path in SHARED_FILES],
        graphify_ignore=[f'{COPILOT.agents_dir.as_posix()}/', f'{LEGACY_SKILLS_DIR.as_posix()}/'],
        mcp_servers=['docs-langchain', 'reference-langchain'],
        skills=[path.as_posix() for path in excluded if path.parent == LEGACY_SKILLS_DIR],
    )


def _owned_names(paths: list[str], directory: Path) -> set[str]:
    return {Path(path).name for path in paths if Path(path).parent == directory}


def _upgrade(manifest: Manifest) -> Manifest:
    return Manifest(
        agents=[_with_dir(path, COPILOT.agents_dir) for path in manifest.agents],
        created_files=manifest.created_files,
        graphify_ignore=manifest.graphify_ignore,
        mcp_servers=[legacy_server_key(key) for key in manifest.mcp_servers],
        platforms=manifest.platforms or [COPILOT.name],
        skills=[_with_dir(path, LEGACY_SKILLS_DIR) for path in manifest.skills],
    )


def _with_dir(path: str, directory: Path) -> str:
    return path if '/' in path else (directory / path).as_posix()
