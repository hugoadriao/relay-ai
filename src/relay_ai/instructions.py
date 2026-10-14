from pathlib import Path

from relay_ai import console
from relay_ai.blocks import remove_block, upsert_block
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


def remove_specialists_section(project: Path) -> bool:
    return remove_block(project / COPILOT_INSTRUCTIONS, SECTION_START, SECTION_END)


def write_specialists_section(project: Path, agents: list[Agent]) -> None:
    if not agents:
        remove_specialists_section(project)
        return

    console.info(f'Registering specialist agents in {COPILOT_INSTRUCTIONS.as_posix()}...')
    agent_lines = '\n'.join(f'- `{agent.name}`: {agent.description}' for agent in agents)
    section = SECTION_TEMPLATE.format(agents=agent_lines, end=SECTION_END, start=SECTION_START)
    upsert_block(project / COPILOT_INSTRUCTIONS, SECTION_START, SECTION_END, section)
