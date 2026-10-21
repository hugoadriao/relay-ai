# Report template

Follow this structure in every audit, in English, keeping the section names and the order
of the fields: a stable structure lets one audit be compared with the next. Text in angle
brackets is filled in; the comments say what goes in each part and are not copied.

````markdown
# <Framework> audit: <project name>

- Date: <YYYY-MM-DD>
- Scope: <whole application | folder audited>
- Versions: <each of the profile's packages and its version>
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
- Accepted by an ADR: `<slug>` (ADR-NNNN), ...
- Still open: `<slug>` (<occurrences before> → <occurrences now>), ...
- New: `<slug>`, ...

## Inventory

<!-- The map of the code: what exists and where, before any judgement. -->

| Component | Kind | Location | Findings |
|---|---|---|---|
| <name> | <one of the kinds in the profile's inventory> | `<path>:<line>` | `<slug>`, ... |

## Findings

<!-- One subsection per area of the specialist's "How you build", always in its order.
     An area without findings says "No findings" and points to Conforming. -->

### <Area>

#### `<slug>`: <title naming the wrong pattern>

- **Kind:** correctness | structural
- **Rule:** <the specialist's rule or anti-pattern it breaks>
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
- **ADR:** none | contradicts ADR-NNNN (<title>): <why it is worth reopening>

## Conforming

<!-- Per area, what was checked and already follows the rules, and the deviations from the
     specialist's rules that an ADR accepted. -->

- **<Area>:** <what was checked and is right>
- **<Area>:** <the deviation>, accepted by ADR-NNNN (<title>)

## Not covered

<!-- What was not checked and why: outside the scope, code missing from the graph, dynamic
     imports, generated code, findings that belong to another profile's report. -->

- <item>: <reason>
````
