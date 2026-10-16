import argparse
import sys
from pathlib import Path

from relay_ai import console
from relay_ai.errors import SetupError
from relay_ai.install import Changes, install, installed_manifest
from relay_ai.platforms import PLATFORMS, Platform, platforms_named
from relay_ai.uninstall import uninstall

PLATFORM_CHOICES = {
    'both': [platform.name for platform in PLATFORMS],
    **{platform.name: [platform.name] for platform in PLATFORMS},
}


def main() -> None:
    parser = argparse.ArgumentParser(prog='relay-ai')
    subcommands = parser.add_subparsers(dest='command', required=True)
    init_parser = subcommands.add_parser('init', help='install RelayAI into a project')
    init_parser.add_argument('path', default=Path('.'), nargs='?', type=Path)
    init_parser.add_argument(
        '--platform', choices=list(PLATFORM_CHOICES), help='where to install (asked if omitted)'
    )
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


def _ask_platforms() -> list[Platform]:
    if not sys.stdin.isatty():
        raise SetupError('choose a platform with --platform copilot|opencode|both')

    options = [*[[platform] for platform in PLATFORMS], list(PLATFORMS)]
    print('Which platform should RelayAI be installed for?')
    for number, option in enumerate(options, start=1):
        print(f'    {number}. {" + ".join(platform.label for platform in option)}')
    try:
        answer = input(f'Choose 1-{len(options)}: ').strip()
    except EOFError as err:
        raise SetupError('choose a platform with --platform copilot|opencode|both') from err
    if not answer.isdigit() or not 1 <= int(answer) <= len(options):
        raise SetupError(f'invalid choice: {answer!r}')
    return options[int(answer) - 1]


def _init_platforms(args: argparse.Namespace, project: Path) -> list[Platform] | None:
    if args.platform:
        return platforms_named(PLATFORM_CHOICES[args.platform])
    if installed_manifest(project) is not None:
        return None
    return _ask_platforms()


def _next_steps(platforms: list[str]) -> None:
    if 'copilot' in platforms:
        console.info(
            'VS Code: run "Developer: Reload Window" so it loads the agents, skills and MCP '
            'servers (and so `graphify` is on PATH for agents).'
        )
    if 'opencode' in platforms:
        console.info('OpenCode: restart it so it loads the agents, skills and MCP servers.')


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

    if args.command == 'update':
        changes = install(project, platforms=None, update=True)
        _report_update(changes)
    else:
        install(project, platforms=_init_platforms(args, project), update=False)
        console.info('Next, run /setup-matt-pocock-skills once for this repository.')
    manifest = installed_manifest(project)
    _next_steps(manifest.platforms if manifest is not None else [])
    console.info('Done.')
