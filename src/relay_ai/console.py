import sys

from relay_ai.windows import stdin_is_console


def confirm(question: str, default: bool) -> bool:
    options = '[Y/n]' if default else '[y/N]'
    try:
        answer = input(f'{question} {options} ').strip().lower()
    except EOFError:
        print()
        return False
    return answer in ('y', 'yes') or (default and not answer)


def error(message: str) -> None:
    print(f'error: {message}', file=sys.stderr)


def info(message: str) -> None:
    print(f'==> {message}', flush=True)


def is_interactive() -> bool:
    return sys.stdin.isatty() and stdin_is_console()


def warn(message: str) -> None:
    print(f'warning: {message}', file=sys.stderr, flush=True)
