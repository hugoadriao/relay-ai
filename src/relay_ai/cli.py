import argparse
import sys
from pathlib import Path

from relay_ai import console
from relay_ai.content import install_mattpocock_skills, install_relay_agents, install_relay_skills
from relay_ai.errors import SetupError
from relay_ai.git import (
    exclude_from_git,
    excluded_paths,
    is_git_repository,
    modified_tracked_files,
)
from relay_ai.graphify import GRAPHIFY_IGNORE_FILE, configure_project, ensure_graphify
from relay_ai.instructions import COPILOT_INSTRUCTIONS, write_specialists_section
from relay_ai.mcp import MCP_CONFIG, add_mcp_servers
from relay_ai.windows import check_path_length

AGENTS_DIR = Path('.github') / 'agents'
SHARED_FILES = (COPILOT_INSTRUCTIONS, MCP_CONFIG, Path(GRAPHIFY_IGNORE_FILE))
SKILLS_DIR = Path('.github') / 'skills'


def init(project: Path) -> None:
    if not project.is_dir():
        raise SetupError(f'project folder not found: {project}')
    check_path_length(project)

    console.info(f'Setting up RelayAI in {project}')
    graphify = ensure_graphify()
    git_repository = is_git_repository(project)
    ours = excluded_paths(project) if git_repository else []
    preexisting = [path for path in SHARED_FILES if (project / path).exists() and path not in ours]

    relay_agents = install_relay_agents(project / AGENTS_DIR)
    if relay_agents:
        console.info(f'RelayAI agents: {", ".join(agent.name for agent in relay_agents)}')
    write_specialists_section(project, relay_agents)
    add_mcp_servers(project)

    skills_dir = project / SKILLS_DIR
    skills_dir.mkdir(parents=True, exist_ok=True)
    relay_skills = install_relay_skills(skills_dir)
    if relay_skills:
        console.info(f'RelayAI skills: {", ".join(relay_skills)}')
    mattpocock_skills = install_mattpocock_skills(skills_dir)
    console.info(f'mattpocock/skills: {len(mattpocock_skills)} skills')

    configure_project(graphify, project, [AGENTS_DIR, SKILLS_DIR])

    if git_repository:
        installed = [AGENTS_DIR / agent.file_name for agent in relay_agents]
        installed += [SKILLS_DIR / skill for skill in relay_skills + mattpocock_skills]
        created = [path for path in SHARED_FILES if path not in preexisting]
        exclude_from_git(
            project, installed + [path for path in created if (project / path).exists()]
        )
        for changed in modified_tracked_files(project, preexisting):
            console.warn(
                f'{changed} is tracked by git and was changed by RelayAI; review the diff and '
                'decide whether to commit it.'
            )

    console.info(f'Done. Skills are in {skills_dir}.')
    console.info('Open a new terminal / reload VS Code so `graphify` is on PATH for agents.')
    console.info('In Copilot Chat, run /setup-matt-pocock-skills once for this repository.')


def main() -> None:
    parser = argparse.ArgumentParser(prog='relay-ai')
    subcommands = parser.add_subparsers(dest='command', required=True)
    init_parser = subcommands.add_parser('init', help='install RelayAI into a project')
    init_parser.add_argument('path', default=Path('.'), nargs='?', type=Path)
    args = parser.parse_args()

    try:
        init(args.path.resolve())
    except SetupError as err:
        console.error(str(err))
        sys.exit(1)
