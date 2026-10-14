import shutil
from pathlib import Path

from relay_ai import console
from relay_ai.blocks import read_block, remove_block, upsert_block
from relay_ai.errors import SetupError
from relay_ai.process import capture

EXCLUDE_END = '# relay-ai:end'
EXCLUDE_START = '# relay-ai:start'
EXCLUDE_TEMPLATE = """{start}
# Installed by RelayAI (local to this clone; `relay-ai update` rewrites this block)
{patterns}
{end}
"""


def exclude_from_git(project: Path, paths: list[Path]) -> None:
    exclude_file = _exclude_file(project)
    prefix = _prefix(project)
    patterns = '\n'.join(_pattern(project, prefix, path) for path in paths)

    console.info(f'Hiding {len(paths)} RelayAI paths from git (.git/info/exclude)...')
    block = EXCLUDE_TEMPLATE.format(end=EXCLUDE_END, patterns=patterns, start=EXCLUDE_START)
    upsert_block(exclude_file, EXCLUDE_START, EXCLUDE_END, block)


def excluded_paths(project: Path) -> list[Path]:
    prefix = _prefix(project)
    lines = read_block(_exclude_file(project), EXCLUDE_START, EXCLUDE_END)
    patterns = [line for line in lines if line.startswith(f'/{prefix}')]
    return [Path(pattern.removeprefix(f'/{prefix}').rstrip('/')) for pattern in patterns]


def is_git_repository(project: Path) -> bool:
    if shutil.which('git') is None:
        return False
    try:
        return capture([_git(), 'rev-parse', '--is-inside-work-tree'], cwd=project) == 'true'
    except SetupError:
        return False


def modified_tracked_files(project: Path, paths: list[Path]) -> list[str]:
    if not paths:
        return []
    output = capture([_git(), 'ls-files', '--modified', '--', *map(str, paths)], cwd=project)
    return output.splitlines()


def remove_exclusions(project: Path) -> None:
    remove_block(_exclude_file(project), EXCLUDE_START, EXCLUDE_END)


def _exclude_file(project: Path) -> Path:
    return project / capture([_git(), 'rev-parse', '--git-path', 'info/exclude'], cwd=project)


def _git() -> str:
    git = shutil.which('git')
    if git is None:
        raise SetupError('git not found')
    return git


def _pattern(project: Path, prefix: str, path: Path) -> str:
    suffix = '/' if (project / path).is_dir() else ''
    return f'/{prefix}{path.as_posix()}{suffix}'


def _prefix(project: Path) -> str:
    return capture([_git(), 'rev-parse', '--show-prefix'], cwd=project)
