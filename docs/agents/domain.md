# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root.
- **The decision table in `SCOPE.md`**: the single source of truth for every architectural
  decision in this repo (imported by `CLAUDE.md`). This repo does not use `docs/adr/`: treat
  each numbered decision (`#N`) as an ADR and read the ones that touch the area you're about
  to work in.

If `GLOSSARY.md` doesn't exist, **proceed silently**. Don't flag its absence; don't suggest creating it upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates it lazily when terms actually get resolved.

## File structure

Single-context repo:

```
/
├── GLOSSARY.md      ← created lazily by /domain-modeling
├── SCOPE.md         ← decision table (#1, #2, ...)
└── src/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag decision conflicts

If your output contradicts a decision in `SCOPE.md`, surface it explicitly rather than silently overriding:

> _Contradicts #<N> (<short subject>), but worth reopening because…_

## Recording decisions

When `/domain-modeling` (or any skill) would write an ADR, add a row to the decision table in
`SCOPE.md` instead, in the same format as the existing rows (number, decision, status), and
update the status column of any decision it revises. Never create `docs/adr/`.
