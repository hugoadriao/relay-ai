# Report template

Follow this structure in every audit, in English, keeping the section names and the order
of the fields: a stable structure lets one audit be compared with the next. Text in angle
brackets is filled in; the comments say what goes in each part and are not copied.

````markdown
# LangGraph audit: <project name>

- Date: <YYYY-MM-DD>
- Scope: <whole application | folder or graph audited>
- Versions: langgraph <x.y.z>, langchain <x.y.z>, langchain-core <x.y.z>
- Previous audit: <path to the previous report | none>

## Summary

<!-- Two or three sentences on the overall state. -->

| Kind | Findings | Occurrences |
|---|---|---|
| correctness | <n> | <n> |
| structural | <n> | <n> |

Suggested sequence:

1. `<slug>`: <one line on why it comes first>
<!-- Order: findings others depend on first, then correctness before structural, then by
     impact. -->

## Since last audit

<!-- Only when there is a previous report. -->

- Resolved: `<slug>`, ...
- Still open: `<slug>` (<occurrences before> → <occurrences now>), ...
- New: `<slug>`, ...

## Inventory

<!-- The map of the LangGraph code: what exists and where, before any judgement. -->

| Component | Kind | Location | Findings |
|---|---|---|---|
| <name> | graph / node / agent / tool / state / prompt / service / checkpointer | `<path>:<line>` | `<slug>`, ... |

## Findings

<!-- One subsection per area of "How you build", always in this order: Shape of the code,
     Dependencies, Execution, State, Agents and tools, Prompts, Artifacts and large data,
     Flow and streaming, Tests. An area without findings says "No findings" and points to
     Conforming. -->

### <Area>

#### `<slug>`: <title naming the wrong pattern>

- **Kind:** correctness | structural
- **Rule:** <the langgraph-expert rule or anti-pattern it breaks>
- **Consequence:** <the concrete effect: what breaks, for whom, when; cite the measured
  data in the agent's rules where it applies>
- **Occurrences:**

  | Component | Location | Note |
  |---|---|---|
  | <name> | `<path>:<line>` | <what is specific to this place> |

- **Target pattern:** <how it should be built, briefly, with a short code sketch when it
  helps>
- **Cost and risk:** <size of the change, tests coupled to the current structure, behaviour
  that may change>
- **Depends on:** `<slug>`, ... | none

## Conforming

<!-- Per area, what was checked and already follows the rules. -->

- **<Area>:** <what was checked and is right>

## Not covered

<!-- What was not checked and why: outside the scope, code missing from the graph, dynamic
     imports, generated code. -->

- <item>: <reason>
````
