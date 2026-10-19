import shutil
from pathlib import Path

from relay_ai import console
from relay_ai.errors import SetupError
from relay_ai.git import is_git_repository
from relay_ai.platforms import Platform
from relay_ai.process import capture, run
from relay_ai.textfile import line_ending, read_text, write_text

GRAPHIFY_GRAPH_FILE = Path('graphify-out') / 'graph.json'
GRAPHIFY_IGNORE_FILE = '.graphifyignore'
GRAPHIFY_PACKAGE = 'graphifyy'
UV_INSTALL_URL = 'https://docs.astral.sh/uv/getting-started/installation/'


def configure_project(
    executable: str, project: Path, platforms: list[Platform], ignored_dirs: list[Path]
) -> list[str]:
    patterns = [f'{ignored_dir.as_posix()}/' for ignored_dir in ignored_dirs]
    added = [pattern for pattern in patterns if _add_to_graphify_ignore(project, pattern)]

    for platform in platforms:
        console.info(f'Configuring Graphify for {platform.label}...')
        run([executable, *platform.graphify_install], cwd=project)

    if is_git_repository(project):
        console.info('Installing Graphify git hooks (graph updates on every commit)...')
        run([executable, 'hook', 'install'], cwd=project)
    else:
        console.warn(
            'Not a git repository: skipping `graphify hook install`, so the graph will not '
            'update automatically. Run it after `git init`.'
        )
    return added


def ensure_graphify() -> str:
    executable = shutil.which('graphify')
    if executable is not None:
        console.info(f'Graphify found at {executable}')
        return executable

    uv = shutil.which('uv')
    if uv is None:
        raise SetupError(f'uv is required to install Graphify: {UV_INSTALL_URL}')

    console.info('Installing Graphify...')
    run([uv, 'tool', 'install', GRAPHIFY_PACKAGE])
    bin_dir = capture([uv, 'tool', 'dir', '--bin'])
    executable = shutil.which('graphify', path=bin_dir)
    if executable is None:
        raise SetupError(f'Graphify was installed but no executable was found in {bin_dir}')

    console.info('Adding the uv tools directory to PATH so agents can call `graphify`...')
    run([uv, 'tool', 'update-shell'])
    return executable


def remove_from_graphify_ignore(project: Path, patterns: list[str]) -> None:
    ignore_file = project / GRAPHIFY_IGNORE_FILE
    if not ignore_file.exists():
        return
    content = read_text(ignore_file)
    lines = content.splitlines(keepends=True)
    kept = [line for line in lines if line.rstrip('\r\n') not in patterns]
    write_text(ignore_file, ''.join(kept), line_ending(content))


def uninstall_from_project(project: Path, platforms: list[Platform]) -> None:
    executable = shutil.which('graphify')
    if executable is None:
        console.warn('Graphify not found on PATH: its project setup was left in place.')
        return

    for platform in platforms:
        console.info(f'Removing Graphify from {platform.label} in this project...')
        for command in platform.graphify_uninstall:
            run([executable, *command], cwd=project)
    if is_git_repository(project):
        console.info('Removing Graphify git hooks...')
        run([executable, 'hook', 'uninstall'], cwd=project)


def _add_to_graphify_ignore(project: Path, pattern: str) -> bool:
    ignore_file = project / GRAPHIFY_IGNORE_FILE
    content = read_text(ignore_file)
    if pattern in content.splitlines():
        return False

    console.info(f'Excluding {pattern} from the graph ({GRAPHIFY_IGNORE_FILE})...')
    separator = '\n' if content and not content.endswith('\n') else ''
    write_text(ignore_file, f'{content}{separator}{pattern}\n', line_ending(content))
    return True
