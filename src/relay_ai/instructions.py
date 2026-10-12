from pathlib import Path

from relay_ai import console
from relay_ai.content import Agent

COPILOT_INSTRUCTIONS = Path('.github') / 'copilot-instructions.md'
SECTION_END = '<!-- relay-ai:end -->'
SECTION_START = '<!-- relay-ai:start -->'
SECTION_TEMPLATE = """{start}
## Specialist agents (RelayAI)

This project has specialist agents for specific technologies:

{agents}

When breaking work into tickets (for example with `/to-tickets`), add the line
`**Specialist:** <agent-name>` to the body of every ticket whose core work falls under one of
these specialties.

When implementing a ticket (for example with `/implement` or `/implement-spec`) whose body has
a `**Specialist:**` line, delegate its implementation to that agent as a subagent.
{end}
"""


def write_specialists_section(project: Path, agents: list[Agent]) -> None:
    if not agents:
        return

    instructions_file = project / COPILOT_INSTRUCTIONS
    console.info(f'Registering specialist agents in {COPILOT_INSTRUCTIONS.as_posix()}...')
    agent_lines = '\n'.join(f'- `{agent.name}`: {agent.description}' for agent in agents)
    section = SECTION_TEMPLATE.format(agents=agent_lines, end=SECTION_END, start=SECTION_START)

    content = _read(instructions_file)
    start = content.find(SECTION_START)
    end = content.find(SECTION_END)
    if start != -1 and end > start:
        tail = content[end + len(SECTION_END) :].removeprefix('\r\n').removeprefix('\n')
        content = f'{content[:start]}{section}{tail}'
    elif content:
        separator = '\n' if content.endswith('\n') else '\n\n'
        content = f'{content}{separator}{section}'
    else:
        content = section

    instructions_file.parent.mkdir(parents=True, exist_ok=True)
    with instructions_file.open('w', encoding='utf-8', newline='') as file:
        file.write(content)


def _read(path: Path) -> str:
    if not path.exists():
        return ''
    with path.open(encoding='utf-8', newline='') as file:
        return file.read()
