---
name: auditing-langgraph
description: Audits how an application uses LangGraph and LangChain (graphs, agents, tools, state, prompts, dependencies) against the langgraph-expert's rules, and writes a findings report to docs/audits/ for planning with to-spec and to-tickets. Use only when the developer explicitly asks to audit, review or validate the application's LangGraph architecture; not while implementing, and not to review a diff (that is code-review).
argument-hint: Optional scope (a folder or one graph); the whole application by default
metadata:
  opencode/slash: "true"
---

# Auditing LangGraph

An audit is a survey, not a rescue: it records how the application uses LangGraph and
LangChain today and what should change, so the developer can plan the work. The rules come
from the `langgraph-expert` agent ("How you build", the anti-pattern list and "The standard
you hold the code to"). This skill only gives the procedure and the report format; it never
adds rules of its own.

## Run as the langgraph-expert

If you are not the `langgraph-expert` agent, you don't have its rules: delegate steps 1 to 5
to it as a subagent, passing the scope, and then do step 6 yourself from the report it
wrote.

## Boundaries

- **Read only.** Read files, query the Graphify graph and search text. The only file you
  write is the report: never edit code, never commit.
- **Never run the project's code or tests.** They can have side effects (databases, external
  APIs, LLM costs). To state a consequence, cite the measured data in the agent's rules
  instead of measuring in the project.
- **The report is always in English.** Code and identifiers are quoted as they are.

## 1. Scope and versions

- The scope is the argument (a folder or one graph) or, without one, the whole application.
  Record it in the report; what falls outside it goes to "Not covered".
- Read the installed versions of `langgraph`, `langchain` and `langchain-core` from the
  lockfile (`uv.lock`, `poetry.lock`, pinned requirements) or `pyproject.toml`. If they are
  older than LangChain v1 / LangGraph 1.x, add the structural finding
  `upgrade-langchain-v1` with its cost, and make every finding whose target pattern needs
  the newer APIs depend on it. The audit goes on with the same rules.

## 2. Locate the LangGraph code

Start from the Graphify graph and read only the files it points to:

- `graphify query "<question>"` for a scoped subgraph, for example "where is the StateGraph
  compiled and invoked", "agents built with create_agent and their tools", "where are the
  prompts loaded";
- `graphify explain "<name>"` for one node's file, line and connections;
- `graphify path "<A>" "<B>"` to see how a graph reaches a tool or a service.

Complement it with text search (`StateGraph(`, `.compile(`, `create_agent(`, `@tool`,
`BaseTool`, `context_schema`, `system_prompt`, `ainvoke(`, `astream(`): the git hooks only
update the graph on commit, so uncommitted code is missing from it. Without
`graphify-out/`, use search alone and say so in "Not covered".

## 3. Inventory

List what exists before judging it: graphs (where they are built, compiled and invoked),
nodes, agents, tools, state schemas, prompts (where they live and how they are loaded),
services (where they are created and how they reach nodes and tools), checkpointer and
store, and the FastAPI entry points that run the graphs.

## 4. Check each area

Go through the subsections of "How you build" in order: Shape of the code, Dependencies,
Execution, State, Agents and tools, Prompts, Artifacts and large data, Flow and streaming,
Tests. Compare the code with the rules and with the anti-pattern list, judging it by its
purpose.

- **One finding per wrong pattern, not per file.** Group every place the pattern occurs
  under one finding: a finding becomes one spec, its occurrences become tickets.
- **Stable ids.** Name each finding with a kebab-case slug that describes the pattern (for
  example, `user-data-in-instance-attributes`), never a number, so the same problem keeps
  the same id across audits.
- **Kind**, following the tie-break rule in "The standard you hold the code to":
  `correctness` for runtime and correctness problems (data leaking between users, blocking
  calls, a defect that reaches the model), which are fixed in the code being touched;
  `structural` for changes that need the developer's agreement and migrate incrementally.
- **Dependencies between findings.** When one finding's target pattern needs another one
  first (the composition root and the runtime context before tools receive services from
  `runtime.context`; the artifact catalog in the state before tools write to it), record it
  in "Depends on". `to-tickets` turns it into blocking edges.
- Record what was checked and follows the rules ("Conforming") and what couldn't be checked
  ("Not covered"). An area without findings still appears, so a reader can tell "checked
  and fine" from "not looked at".

## 5. Compare and write

- Look for the latest previous report, `docs/audits/langgraph-*.md`. If there is one, reuse
  its slugs for the same patterns and fill in "Since last audit": findings resolved, still
  open (with the occurrence count before and now) and new.
- Write `docs/audits/langgraph-<YYYY-MM-DD>.md` (add `-2`, `-3` if that name exists), using
  the structure in [report-template.md](report-template.md).

## 6. Hand over

1. Give the report's path and its summary, and ask which finding to plan first (suggest the
   first one in the summary's sequence).
2. For a `correctness` finding, restate the whole finding in the conversation, because
   `/to-spec` reads only the conversation, and tell the developer to run `/to-spec` and then
   `/to-tickets`.
3. For a `structural` finding, use the `grilling` skill first to settle the target pattern,
   its cost and how existing code migrates. Then restate the agreed finding in the
   conversation and tell the developer to run `/to-spec` and then `/to-tickets`.

Never run `/to-spec` or `/to-tickets` yourself: the developer decides when to plan.
