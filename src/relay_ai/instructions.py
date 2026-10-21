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

## Exploration memory (RelayAI)

When `graphify-out/graph.json` exists, use Graphify's work memory, so that each task starts from
what earlier sessions learned about this code and leaves what it learned for the next ones:

1. Before the first exploration of the code in a task, run `graphify reflect --if-stale` and read
   `graphify-out/reflections/LESSONS.md`: start from its preferred sources, skip its known dead
   ends and apply its corrections. The code may have changed since a lesson was recorded: check
   in the code what a lesson points to before relying on it, and re-check every node that
   `graphify explain` marks as changed since its lesson.
2. After each graph query (`graphify query`, `path` or `explain`), once you have checked its
   answer in the code, record it with `graphify save-result`: `--question`, `--answer` with
   `file:line` references, `--type` (`query`, `path_query` or `explain`), `--nodes` with the
   labels of the nodes the answer cites, and one `--outcome`. When a label belongs to more than
   one node, cite that node by its id instead, so the lesson stays with it. Method labels carry
   no class name (`.get()`, `.__init__()`) and `graphify query` lists only the nodes in its
   subgraph, so before citing a method or a function with a common name (`main()`, `run()`),
   run `graphify explain "<label>"`: when it answers "Ambiguous", it lists each node's file and
   id. The outcomes:
   - `useful`: the cited nodes answered the question;
   - `corrected`, with `--correction` saying where the answer really is (`file:line` or
     symbol): the graph pointed to the wrong place and the answer came from a search or a file
     read;
   - `dead_end`: the answer doesn't exist in the code (for example, the feature doesn't exist).

   When the answer has quotes or several lines, write it to a temporary file outside the
   project and pass `--answer-file` instead of `--answer`.
3. Write the question, the answer and the correction in English, whatever the language of the
   conversation.
4. Put these rules in the prompt of every subagent that explores code, and ask it to report
   back how many memories it recorded, by outcome.
5. At the end of the task, the agent talking to the developer tells them in one line how many
   memories were recorded, by outcome, its subagents' included.
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
