import re
import shutil

from relay_ai import console
from relay_ai.mcp import managed_servers
from relay_ai.process import capture, succeeds

MINIMUM_NODE_MAJOR = 22
NODE_GUIDE = 'https://github.com/hugoadriao/relay-ai#prerequisites'
NODE_MISSING_MESSAGE = """\
Node.js {minimum} or newer is needed by RelayAI's debugger (mcp-debugger) ({found}).
RelayAI was installed and the debugger is configured, but it won't start until Node.js is
installed. Quick options:

  Windows:  winget install OpenJS.NodeJS.LTS
  macOS:    brew install node
  Linux:    use your package manager, or https://nodejs.org/en/download

Step by step: {guide}
Then run `relay-ai update` to download the debugger."""
NPM_PING_TIMEOUT = 60
PREFETCH_TIMEOUT = 300
REGISTRY_UNREACHABLE_MESSAGE = """\
{name} was not downloaded: {reason}. It is configured, but it won't start until it is in
npm's cache. If your network blocks the npm registry, do one of these:

  - point npm to your company's registry mirror (npm config set registry <url>) and run
    `relay-ai update`;
  - ask IT to allow registry.npmjs.org;
  - from a network that reaches the registry, run once: {command}

Once it is cached, it starts without contacting the registry. Until then, the agents debug
with temporary prints instead."""


def prefetch_mcp_servers(names: set[str]) -> None:
    prefetches = {
        name: server['prefetch']
        for name, server in managed_servers().items()
        if name in names and 'prefetch' in server
    }
    if not prefetches:
        return

    problem = _node_problem()
    if problem is not None:
        console.warn(problem)
        return

    console.info('Checking access to the npm registry...')
    ping = [shutil.which('npm'), 'ping', '--fetch-retries=0', '--fetch-timeout=10000']
    if not succeeds(ping, NPM_PING_TIMEOUT):
        for name, command in prefetches.items():
            console.warn(_unreachable(name, 'the npm registry did not answer', command))
        return

    for name, command in prefetches.items():
        console.info(f"Downloading {name} into npm's cache (this can take a few minutes)...")
        if succeeds([shutil.which(command[0]), *command[1:]], PREFETCH_TIMEOUT):
            console.info(f'{name} is cached: it starts without contacting the npm registry.')
        else:
            console.warn(_unreachable(name, 'the download failed or timed out', command))


def _node_message(found: str) -> str:
    return NODE_MISSING_MESSAGE.format(found=found, guide=NODE_GUIDE, minimum=MINIMUM_NODE_MAJOR)


def _node_problem() -> str | None:
    node = shutil.which('node')
    if node is None:
        return _node_message('not found')
    version = capture([node, '--version'])
    match = re.match(r'v(\d+)\.', version)
    if match is None or int(match.group(1)) < MINIMUM_NODE_MAJOR:
        return _node_message(f'found {version}')
    if shutil.which('npm') is None or shutil.which('npx') is None:
        return _node_message(f'found {version}, but not npm and npx')
    return None


def _unreachable(name: str, reason: str, command: list[str]) -> str:
    return REGISTRY_UNREACHABLE_MESSAGE.format(command=' '.join(command), name=name, reason=reason)
