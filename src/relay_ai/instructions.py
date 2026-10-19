from pathlib import Path

from relay_ai import console
from relay_ai.blocks import read_block, remove_block, upsert_block
from relay_ai.content import Agent
from relay_ai.platforms import Platform

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

## Python code style (RelayAI)

Python code in this project is written and reviewed following the `writing-python` skill
(`.agents/skills/writing-python/SKILL.md`), unless the project's own configuration or coding
standard says otherwise.
{end}
"""


def has_specialists_section(project: Path, platform: Platform) -> bool:
    return bool(read_block(project / platform.instructions_file, SECTION_START, SECTION_END))


def remove_specialists_section(project: Path, platform: Platform) -> bool:
    return remove_block(project / platform.instructions_file, SECTION_START, SECTION_END)


def write_specialists_section(project: Path, platform: Platform, agents: list[Agent]) -> None:
    if not agents:
        remove_specialists_section(project, platform)
        return

    instructions = platform.instructions_file.as_posix()
    console.info(f'Registering specialist agents in {instructions}...')
    agent_lines = '\n'.join(f'- `{agent.name}`: {agent.description}' for agent in agents)
    section = SECTION_TEMPLATE.format(agents=agent_lines, end=SECTION_END, start=SECTION_START)
    upsert_block(project / platform.instructions_file, SECTION_START, SECTION_END, section)
