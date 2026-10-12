import argparse
import sys
from pathlib import Path

from relay_ai import console
from relay_ai.content import install_mattpocock_skills, install_relay_agents, install_relay_skills
from relay_ai.errors import SetupError
from relay_ai.graphify import configure_project, ensure_graphify
from relay_ai.instructions import write_specialists_section
from relay_ai.mcp import add_mcp_servers

AGENTS_DIR = Path('.github') / 'agents'
SKILLS_DIR = Path('.github') / 'skills'


def init(project: Path) -> None:
    if not project.is_dir():
        raise SetupError(f'project folder not found: {project}')

    console.info(f'Setting up RelayAI in {project}')
    graphify = ensure_graphify()

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
