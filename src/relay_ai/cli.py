import argparse
import sys
from pathlib import Path

from relay_ai import console
from relay_ai.errors import SetupError
from relay_ai.install import SKILLS_DIR, Changes, install
from relay_ai.uninstall import uninstall


def main() -> None:
    parser = argparse.ArgumentParser(prog='relay-ai')
    subcommands = parser.add_subparsers(dest='command', required=True)
    init_parser = subcommands.add_parser('init', help='install RelayAI into a project')
    init_parser.add_argument('path', default=Path('.'), nargs='?', type=Path)
    update_parser = subcommands.add_parser('update', help='update RelayAI in a project')
    update_parser.add_argument('path', default=Path('.'), nargs='?', type=Path)
    uninstall_parser = subcommands.add_parser('uninstall', help='remove RelayAI from a project')
    uninstall_parser.add_argument('path', default=Path('.'), nargs='?', type=Path)
    uninstall_parser.add_argument(
        '--graphify', action='store_true', help="also remove Graphify's setup from the project"
    )
    uninstall_parser.add_argument(
        '-y', '--yes', action='store_true', help='remove without asking for confirmation'
    )
    args = parser.parse_args()

    try:
        _run(args)
    except SetupError as err:
        console.error(str(err))
        sys.exit(1)


def _report_update(changes: Changes) -> None:
    console.info(f'Updated: {len(changes.updated)} | added: {len(changes.added)}')
    for label in changes.added:
        print(f'    + {label}')
    for label in changes.removed:
        print(f'    - {label} (no longer part of RelayAI)')
    console.info('Graphify is not upgraded by RelayAI. To upgrade it: uv tool upgrade graphifyy')


def _run(args: argparse.Namespace) -> None:
    project = args.path.resolve()
    if args.command == 'uninstall':
        removed = uninstall(project, assume_yes=args.yes, graphify=args.graphify)
        if removed and not args.graphify:
            console.info(
                'Graphify is still set up in this project (git hooks, graphify-out/). '
                'To remove its setup too: relay-ai uninstall --graphify'
            )
        return

    changes = install(project, update=args.command == 'update')
    if args.command == 'update':
        _report_update(changes)
    console.info(f'Done. Skills are in {project / SKILLS_DIR}.')
    console.info('Open a new terminal / reload VS Code so `graphify` is on PATH for agents.')
    if args.command == 'init':
        console.info('In Copilot Chat, run /setup-matt-pocock-skills once for this repository.')
