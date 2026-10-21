---
name: auditing-code
description: Audits a whole application against the rules of RelayAI's specialist agents, one framework at a time (LangGraph and LangChain with the langgraph-expert, FastAPI with the fastapi-expert), and writes one findings report per framework to docs/audits/ for planning with to-spec and to-tickets. Use only when the developer explicitly asks to audit, review or validate how the application uses these frameworks; not while implementing, and not to review a diff (that is code-review).
argument-hint: Optional profile (langgraph, fastapi) and scope (a folder); every framework the project uses by default
metadata:
  opencode/slash: "true"
---

# Auditing code

An audit is a survey, not a rescue: it records how the application uses a framework today
and what should change, so the developer can plan the work. The rules come from the
framework's specialist agent ("How you build", the anti-pattern list and "The standard you
hold the code to"). This skill only gives the procedure and the report format; it never
adds rules of its own.

What changes from one framework to another is in its **profile**: the specialist agent, the
packages that activate it, the versions to read and the minimum one, where to look, what
the inventory lists, what code the framework owns and the report's name.

- [profiles/langgraph.md](profiles/langgraph.md): LangGraph and LangChain
- [profiles/fastapi.md](profiles/fastapi.md): FastAPI

## Choose the profiles

- If the argument names a profile (`langgraph`, `fastapi`), audit that one.
- Otherwise read the project's dependencies (`pyproject.toml` or the lockfile) and audit
  every profile whose packages are there, one after another, each with its own report.
- Read the profile before step 1: every step below uses it.

## Run as the specialist

Each profile is audited by its specialist agent. If you are not that agent, you don't have
its rules: delegate steps 1 to 5 to it as a subagent, passing the profile, the scope and the
"Exploration memory (RelayAI)" rules from the project's instructions
(`.github/copilot-instructions.md` or `AGENTS.md`), and then do step 6 yourself from the
reports.

## Boundaries

- **Read only.** Read files, query the Graphify graph and search text. The only files you
  write are the reports and Graphify's work memory (step 2): the memories in
  `graphify-out/memory/` and the lessons `graphify reflect` derives from them; at the hand
  over, also an ADR the developer agreed to (step 6). Never edit code, never commit.
- **Never run the project's code or tests.** They can have side effects (databases, external
  APIs, LLM costs). To state a consequence, cite the measured data in the agent's rules
  instead of measuring in the project.
- **The reports are always in English.** Code and identifiers are quoted as they are.

## 1. Scope and versions

- The scope is the argument (a folder) or, without one, the whole application. Record it in
  the report; what falls outside it goes to "Not covered".
- Read the installed versions of the profile's packages from the lockfile (`uv.lock`,
  `poetry.lock`, pinned requirements) or `pyproject.toml`. If they are older than the
  profile's minimum, add the profile's upgrade finding with its cost, and make every finding
  whose target pattern needs the newer APIs depend on it. The audit goes on with the same
  rules.

## 2. Locate the code

Start from the Graphify graph and read only the files it points to:

- `graphify query "<question>"` for a scoped subgraph, with questions like the profile's;
- `graphify explain "<name>"` for one node's file, line and connections;
- `graphify path "<A>" "<B>"` to see how two parts of the code connect.

Complement it with text search for the profile's patterns: the git hooks only update the
graph on commit, so uncommitted code is missing from it. Without `graphify-out/`, use search
alone and say so in "Not covered".

Follow the "Exploration memory (RelayAI)" rules in the project's instructions: read the
lessons before the first query, and record every query once you have checked it in the code,
so the tasks planned from the report start from what the audit located.

## 3. Inventory

List what exists before judging it, with the kinds of component the profile names, and
where each one lives.

## 4. Check each area

Go through the subsections of the specialist's "How you build", in order, comparing the
code with the rules and with the anti-pattern list, and judging it by its purpose.

- **One finding per wrong pattern, not per file.** Group every place the pattern occurs
  under one finding: a finding becomes one spec, its occurrences become tickets.
- **Stable ids.** Name each finding with a kebab-case slug that describes the pattern (for
  example, `user-data-in-instance-attributes`), never a number, so the same problem keeps
  the same id across audits.
- **Kind**, following the tie-break rule in "The standard you hold the code to":
  `correctness` for runtime, correctness and security problems, which are fixed in the code
  being touched; `structural` for changes that need the developer's agreement and migrate
  incrementally.
- **Dependencies between findings.** When one finding's target pattern needs another one
  first, record it in "Depends on". `to-tickets` turns it into blocking edges.
- **The boundary between frameworks.** A finding where two frameworks meet goes to the
  report of the profile that owns that code (each profile says what it owns), never to both.
  When the other profile is audited too, mention the finding there under "Not covered" with
  the other report's path.
- **Decisions already made.** Read the ADRs in `docs/adr/` that touch the area, as the
  specialist does before proposing a structural change. A structural deviation from the
  specialist's rules that an ADR accepted is not a finding: record it under "Conforming" as
  "accepted by ADR-NNNN", so each audit doesn't reopen what the team already decided. Make it
  a finding only when the friction is real enough to reopen the decision, marked
  "contradicts ADR-NNNN" with the reason. A `correctness` problem stays a finding even when an
  ADR accepted it, marked the same way.
- Record what was checked and follows the rules ("Conforming") and what couldn't be checked
  ("Not covered"). An area without findings still appears, so a reader can tell "checked
  and fine" from "not looked at".

## 5. Compare and write

- Look for the latest previous report of the profile, `docs/audits/<prefix>-*.md`. If there
  is one, reuse its slugs for the same patterns and fill in "Since last audit": findings
  resolved, accepted by an ADR since then, still open (with the occurrence count before and
  now) and new.
- Write `docs/audits/<prefix>-<YYYY-MM-DD>.md` (add `-2`, `-3` if that name exists), using
  the structure in [report-template.md](report-template.md).

## 6. Hand over

1. Give each report's path and its summary, and ask which finding to plan first (suggest
   the first one in a summary's sequence).
2. For a `correctness` finding, restate the whole finding in the conversation, because
   `/to-spec` reads only the conversation, and tell the developer to run `/to-spec` and then
   `/to-tickets`.
3. For a `structural` finding, use the `grilling` skill first to settle the target pattern,
   its cost and how existing code migrates. Once it is agreed, offer to record it as an ADR
   with the `domain-modeling` skill, as the specialist's "The standard you hold the code to"
   says for an accepted structural change (in English, and only if the developer agrees).
   Then restate the agreed finding in the conversation and tell the developer to run
   `/to-spec` and then `/to-tickets`.

Never run `/to-spec` or `/to-tickets` yourself: the developer decides when to plan.
