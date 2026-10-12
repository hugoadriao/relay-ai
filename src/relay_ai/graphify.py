import shutil
from pathlib import Path

from relay_ai import console
from relay_ai.errors import SetupError
from relay_ai.process import capture, run

GRAPHIFY_IGNORE_FILE = '.graphifyignore'
GRAPHIFY_PACKAGE = 'graphifyy'
UV_INSTALL_URL = 'https://docs.astral.sh/uv/getting-started/installation/'


def configure_project(executable: str, project: Path, ignored_dirs: list[Path]) -> None:
    for ignored_dir in ignored_dirs:
        _add_to_graphify_ignore(project, f'{ignored_dir.as_posix()}/')

    console.info('Configuring Graphify for VS Code Copilot Chat...')
    run([executable, 'vscode', 'install'], cwd=project)

    if _is_git_repository(project):
        console.info('Installing Graphify git hooks (graph updates on every commit)...')
        run([executable, 'hook', 'install'], cwd=project)
    else:
        console.warn(
            'Not a git repository: skipping `graphify hook install`, so the graph will not '
            'update automatically. Run it after `git init`.'
        )

    console.info('Building the initial code graph...')
    run([executable, 'update', '.'], cwd=project)


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


def _add_to_graphify_ignore(project: Path, pattern: str) -> None:
    ignore_file = project / GRAPHIFY_IGNORE_FILE
    content = ignore_file.read_text(encoding='utf-8') if ignore_file.exists() else ''
    if pattern in content.splitlines():
        return

    console.info(f'Excluding {pattern} from the graph ({GRAPHIFY_IGNORE_FILE})...')
    separator = '\n' if content and not content.endswith('\n') else ''
    with ignore_file.open('a', encoding='utf-8', newline='') as file:
        file.write(f'{separator}{pattern}\n')


def _is_git_repository(project: Path) -> bool:
    git = shutil.which('git')
    if git is None:
        return False
    try:
        return capture([git, 'rev-parse', '--is-inside-work-tree'], cwd=project) == 'true'
    except SetupError:
        return False
