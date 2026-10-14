import sys
from pathlib import Path

from relay_ai.errors import SetupError

FILESYSTEM_KEY = r'SYSTEM\CurrentControlSet\Control\FileSystem'
GRAPHIFY_CACHE_SUFFIX_LENGTH = 130
MAX_PATH = 260
TOO_LONG_MESSAGE = """\
this project's path is too long for the Windows 260-character path limit, and long paths
are disabled on this machine. Graphify writes cache files up to {suffix} characters below
the project folder: with this project's path ({length} characters) they would reach
{total}, and building the graph would fail.

Fix it in one of these ways, then run `relay-ai init` again:

  1. Enable long paths (needs administrator rights). In PowerShell run as administrator:

       New-ItemProperty -Path 'HKLM:\\{key}' -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force

     Then open a new terminal (restart Windows if the error persists).

  2. Move or clone the project to a shorter path, such as C:\\dev\\{name}."""


def check_path_length(project: Path) -> None:
    if sys.platform != 'win32' or _long_paths_enabled():
        return

    length = len(str(project))
    total = length + GRAPHIFY_CACHE_SUFFIX_LENGTH
    if total < MAX_PATH:
        return

    raise SetupError(
        TOO_LONG_MESSAGE.format(
            key=FILESYSTEM_KEY,
            length=length,
            name=project.name,
            suffix=GRAPHIFY_CACHE_SUFFIX_LENGTH,
            total=total,
        )
    )


def _long_paths_enabled() -> bool:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, FILESYSTEM_KEY) as key:
            value, _ = winreg.QueryValueEx(key, 'LongPathsEnabled')
    except OSError:
        return False
    return value == 1
