import sys


def error(message: str) -> None:
    print(f'error: {message}', file=sys.stderr)


def info(message: str) -> None:
    print(f'==> {message}', flush=True)


def warn(message: str) -> None:
    print(f'warning: {message}', file=sys.stderr, flush=True)
