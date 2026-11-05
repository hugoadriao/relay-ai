import re
import shutil
from pathlib import Path

from relay_ai import console
from relay_ai.errors import SetupError
from relay_ai.git import is_git_repository
from relay_ai.platforms import Platform
from relay_ai.process import capture, run
from relay_ai.textfile import line_ending, read_text, write_text

GRAPHIFY_OUT_DIR = Path('graphify-out')
GRAPHIFY_DERIVED_FILES = (
    GRAPHIFY_OUT_DIR / '.graphify_learning.json',
    GRAPHIFY_OUT_DIR / 'reflections' / 'LESSONS.md',
)
GRAPHIFY_GRAPH_FILE = GRAPHIFY_OUT_DIR / 'graph.json'
GRAPHIFY_IGNORE_FILE = '.graphifyignore'
GRAPHIFY_MINIMUM_VERSION = (0, 9, 94)
GRAPHIFY_PACKAGE = 'graphifyy'
GRAPHIFY_UPGRADE_COMMAND = f'uv tool install {GRAPHIFY_PACKAGE}@latest'
GRAPHIFY_VERSION_PATTERN = re.compile(r'graphify (\d+)\.(\d+)\.(\d+)')
OUTDATED_MESSAGE = (
    'Graphify {found} is older than {minimum}, the version RelayAI recommends: older versions '
    'write an OpenCode plugin that OpenCode 2 fails to load. {fix}'
)
UV_INSTALL_URL = 'https://docs.astral.sh/uv/getting-started/installation/'

type Version = tuple[int, int, int]


def check_graphify_version(executable: str) -> str | None:
    version = _read_version(executable)
    label = f'Graphify {_format_version(version)}' if version is not None else 'Graphify'
    console.info(f'{label} found at {executable}')
    warning = _version_warning(executable, version)
    if warning is not None:
        console.warn(warning)
    return warning


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


def _format_version(version: Version) -> str:
    return '.'.join(str(part) for part in version)


def _installed_by_uv(executable: str) -> bool:
    uv = shutil.which('uv')
    if uv is None:
        return False
    try:
        bin_dir = capture([uv, 'tool', 'dir', '--bin'])
        tool_dir = capture([uv, 'tool', 'dir'])
    except SetupError:
        return False
    in_bin_dir = Path(executable).parent.resolve() == Path(bin_dir).resolve()
    return in_bin_dir and (Path(tool_dir) / GRAPHIFY_PACKAGE).is_dir()


def _read_version(executable: str) -> Version | None:
    try:
        output = capture([executable, '--version'])
    except SetupError:
        return None
    match = GRAPHIFY_VERSION_PATTERN.fullmatch(output)
    if match is None:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def _version_warning(executable: str, version: Version | None) -> str | None:
    minimum = _format_version(GRAPHIFY_MINIMUM_VERSION)
    if version is None:
        return (
            f'Could not read the Graphify version from `{executable} --version`; RelayAI '
            f'recommends Graphify {minimum} or newer.'
        )
    if version >= GRAPHIFY_MINIMUM_VERSION:
        return None
    if _installed_by_uv(executable):
        fix = f'To upgrade it: {GRAPHIFY_UPGRADE_COMMAND}'
    else:
        fix = (
            f'RelayAI could not confirm it was installed with uv ({executable}), so upgrade it '
            f'the way you installed it, for example pipx upgrade {GRAPHIFY_PACKAGE} or pip '
            f'install --upgrade {GRAPHIFY_PACKAGE}.'
        )
    return OUTDATED_MESSAGE.format(found=_format_version(version), fix=fix, minimum=minimum)
