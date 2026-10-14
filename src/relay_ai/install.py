from dataclasses import dataclass
from pathlib import Path

from relay_ai import console
from relay_ai.content import (
    AGENT_SUFFIX,
    install_mattpocock_skills,
    install_relay_agents,
    install_relay_skills,
    remove_installed,
)
from relay_ai.errors import SetupError
from relay_ai.git import (
    exclude_from_git,
    excluded_paths,
    is_git_repository,
    modified_tracked_files,
)
from relay_ai.graphify import GRAPHIFY_IGNORE_FILE, configure_project, ensure_graphify
from relay_ai.instructions import COPILOT_INSTRUCTIONS, write_specialists_section
from relay_ai.manifest import MANIFEST_FILE, Manifest, load_manifest, save_manifest
from relay_ai.vscode import (
    EXTENSIONS_CONFIG,
    MCP_CONFIG,
    add_extension_recommendations,
    add_mcp_servers,
    managed_extensions,
    managed_mcp_servers,
)
from relay_ai.windows import check_path_length

AGENTS_DIR = Path('.github') / 'agents'
SHARED_FILES = (COPILOT_INSTRUCTIONS, EXTENSIONS_CONFIG, MCP_CONFIG, Path(GRAPHIFY_IGNORE_FILE))
SKILLS_DIR = Path('.github') / 'skills'


@dataclass(frozen=True)
class Changes:
    added: list[str]
    removed: list[str]
    updated: list[str]


def install(project: Path, update: bool) -> Changes:
    if not project.is_dir():
        raise SetupError(f'project folder not found: {project}')
    check_path_length(project)

    previous = installed_manifest(project)
    if update and previous is None:
        raise SetupError('RelayAI is not installed in this project: run `relay-ai init` first.')
    previous = previous or Manifest()

    console.info(f'{"Updating" if update else "Setting up"} RelayAI in {project}')
    graphify = ensure_graphify()
    preexisting = [
        path
        for path in SHARED_FILES
        if (project / path).exists() and path.as_posix() not in previous.created_files
    ]

    agents = install_relay_agents(project / AGENTS_DIR, set(previous.agents))
    write_specialists_section(project, agents)
    mcp_servers = add_mcp_servers(project)
    extensions = add_extension_recommendations(project)

    skills_dir = project / SKILLS_DIR
    skills_dir.mkdir(parents=True, exist_ok=True)
    skills = install_relay_skills(skills_dir, set(previous.skills))
    skills += install_mattpocock_skills(skills_dir, set(previous.skills))
    agent_files = [agent.file_name for agent in agents]
    stale = [SKILLS_DIR / skill for skill in previous.skills if skill not in skills]
    stale += [AGENTS_DIR / agent for agent in previous.agents if agent not in agent_files]
    for path in stale:
        remove_installed(project / path)

    graphify_ignore = configure_project(graphify, project, [AGENTS_DIR, SKILLS_DIR])

    created = [
        path for path in SHARED_FILES if path not in preexisting and (project / path).exists()
    ]
    manifest = Manifest(
        agents=agent_files,
        created_files=[path.as_posix() for path in created],
        extensions=previous.extensions + extensions,
        graphify_ignore=previous.graphify_ignore + graphify_ignore,
        mcp_servers=previous.mcp_servers + mcp_servers,
        skills=skills,
    )
    save_manifest(project, manifest)

    if is_git_repository(project):
        installed = [AGENTS_DIR / agent for agent in agent_files]
        installed += [SKILLS_DIR / skill for skill in skills]
        exclude_from_git(project, installed + created + [MANIFEST_FILE])
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
    if manifest is not None or not is_git_repository(project):
        return manifest

    excluded = excluded_paths(project)
    if not excluded:
        return None
    return _legacy_manifest(project, excluded)


def _labels(manifest: Manifest) -> list[str]:
    agents = [f'agent {agent.removesuffix(AGENT_SUFFIX)}' for agent in manifest.agents]
    return agents + [f'skill {skill}' for skill in manifest.skills]


def _legacy_manifest(project: Path, excluded: list[Path]) -> Manifest:
    ignore_file = project / GRAPHIFY_IGNORE_FILE
    graphify_ignore = (
        ignore_file.read_text(encoding='utf-8').splitlines() if ignore_file.exists() else []
    )
    patterns = [f'{AGENTS_DIR.as_posix()}/', f'{SKILLS_DIR.as_posix()}/']
    return Manifest(
        agents=[path.name for path in excluded if path.parent == AGENTS_DIR],
        created_files=[path.as_posix() for path in excluded if path in SHARED_FILES],
        extensions=managed_extensions(),
        graphify_ignore=[pattern for pattern in patterns if pattern in graphify_ignore],
        mcp_servers=managed_mcp_servers(),
        skills=[path.name for path in excluded if path.parent == SKILLS_DIR],
    )
