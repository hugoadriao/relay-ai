import subprocess
from pathlib import Path

from relay_ai.errors import SetupError


def capture(command: list[str], cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(command, capture_output=True, check=True, cwd=cwd, text=True)
    except (OSError, subprocess.CalledProcessError) as err:
        raise SetupError(f"'{' '.join(command)}' failed") from err
    return result.stdout.strip()


def run(command: list[str], cwd: Path | None = None) -> None:
    try:
        subprocess.run(command, check=True, cwd=cwd)
    except (OSError, subprocess.CalledProcessError) as err:
        raise SetupError(f"'{' '.join(command)}' failed") from err


def succeeds(command: list[str], timeout: int) -> bool:
    try:
        result = subprocess.run(
            command, capture_output=True, check=False, stdin=subprocess.DEVNULL, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0
