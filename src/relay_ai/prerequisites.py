import re
import shutil

from relay_ai.errors import SetupError
from relay_ai.process import capture

MINIMUM_NODE_MAJOR = 22
NODE_GUIDE = 'https://github.com/hugoadriao/relay-ai#prerequisites'
NODE_MISSING_MESSAGE = """\
Node.js {minimum} or newer is required ({found}). RelayAI's debugger (mcp-debugger) runs on it.
Install it and run this command again. Quick options:

  Windows:  winget install OpenJS.NodeJS.LTS
  macOS:    brew install node
  Linux:    use your package manager, or https://nodejs.org/en/download

Step by step: {guide}"""


def check_node() -> None:
    node = shutil.which('node')
    if node is None:
        _missing('not found')
    version = capture([node, '--version'])
    match = re.match(r'v(\d+)\.', version)
    if match is None or int(match.group(1)) < MINIMUM_NODE_MAJOR:
        _missing(f'found {version}')


def _missing(found: str) -> None:
    raise SetupError(
        NODE_MISSING_MESSAGE.format(found=found, guide=NODE_GUIDE, minimum=MINIMUM_NODE_MAJOR)
    )
