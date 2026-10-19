---
name: debugging-python
description: Python debugging toolkit that makes you observe the real data at the point of failure, with a real debugger (mcp-debugger), instead of inferring it, while spending as few tokens as possible. Use whenever you debug Python code (exceptions, failing tests, wrong output, hangs, slowness), together with the diagnosing-bugs skill.
---

# Debugging Python

The `diagnosing-bugs` skill gives the process: build a feedback loop, reproduce, hypothesise,
instrument, fix, clean up. This skill gives the Python tools for each step, and one rule that
overrides everything else.

## Observe, don't infer

A hypothesis is confirmed only when you have **seen the actual value** (its type, its shape
and its content) at the point where the flow goes wrong. Reading the code and reasoning about
what a variable "must" contain is not evidence; neither is a log line from somewhere else in
the flow. Until you have observed it, call it a hypothesis, not a cause.

## Spend tokens on the bug, not on the noise

Python programs, and agent graphs above all, carry large values: LLM message lists, exchanges
between agents and tools, HTTP responses, ORM objects, DataFrames. Most of them have nothing to
do with the bug.

- **Never dump a large object.** Look at its shape first, then project only what you need.
- **Shape before values:** names and types → the few values that matter → projections such as
  `len(x)`, `list(d)`, `type(x).__name__`, `x[-1]`, `s[:200]`, one attribute of an object.
- **Stop only where it matters:** conditional breakpoints instead of stopping on every pass;
  logpoints instead of stepping through a loop.
- **Keep command output short:** run the single failing test (`pytest path::test -x -q
  --tb=short`), not the whole suite; cut long output (`| head -n 40`) and widen only if needed.

## The debugger: mcp-debugger

When the `mcp-debugger` tools are available, use the debugger to observe values. It runs
locally (no IDE needed) and drives `debugpy`. Read [debugger.md](debugger.md) for how to
start a session and use the tools sparingly. In short:

1. Start from the red-capable command of `diagnosing-bugs` Phase 1, ideally one pytest test.
2. Run that command under a temporary `debugpy` that waits for the debugger, in the
   background, without adding `debugpy` to the project's dependencies.
3. Attach to it, then put a breakpoint where your hypotheses diverge, with a condition
   whenever the line runs more than once.
4. When it stops: look at variable names and types first, then evaluate projections, and
   fetch full values only when they are small.
5. Step only through the suspicious region; otherwise continue to the next breakpoint.
6. At the end, remove your breakpoints and close the session.

**If the debugger is not available**, say so once (RelayAI configures `mcp-debugger` in the
project's MCP settings; it needs Node.js 22+). Then fall back to temporary prints of
**projections**, never of whole objects, tagged with a unique prefix such as `[DEBUG-a4f2]`
so cleanup is a single grep.

**Never run `pdb` or `breakpoint()` yourself** in a command: it waits for keyboard input and
your command hangs. If the developer wants to step through by hand, suggest where to put the
`breakpoint()`.

## Reading Python failures

- Read the traceback from the bottom up, but follow the chain: with "The above exception was
  the direct cause of..." or "During handling of the above exception...", the first exception
  printed is usually the real origin.
- `ExceptionGroup` (from `asyncio.TaskGroup`, for example) holds several sub-exceptions;
  read each one.
- `RuntimeWarning: coroutine ... was never awaited` and `Task exception was never retrieved`
  are bugs, not noise.
- The line that raised is rarely the line that produced the bad value. Follow the value
  upstream until you reach the code that created it wrong.

## By kind of bug

Read only the reference that applies:

- LangGraph graphs: [langgraph.md](langgraph.md)
- asyncio (hangs, blocked event loop, cancellation, never-awaited coroutines):
  [asyncio.md](asyncio.md)
- Performance and memory: [performance.md](performance.md)
- Environment (imports, virtual environments, versions): [environment.md](environment.md)

## Fix the cause, never the symptom

None of these is a fix; each one only hides the bug:

- a broad `try/except` that swallows the error;
- an `if x is None` (or similar check) around data that should always exist;
- a `sleep` or a retry to get past a race condition or a deterministic failure;
- pinning a dependency version without knowing what broke.

If a value arrived wrong, go upstream to the code that produced it and fix it there. Write
the fix and its regression test following the `writing-python` skill.

## Tools

Prefer what ships with Python: `pdb` (for the developer), `faulthandler`, `tracemalloc`,
`cProfile`, asyncio debug mode. When a third-party tool is clearly better (`py-spy`,
`pyinstrument`), run it on the fly with `uvx`; never add it to the project's dependencies
without asking.

## Report

When you are done, state:

- the root cause, in one sentence;
- the evidence: the observed value that proved it, and where you observed it;
- the fix, and the regression test that now passes;
- that the debug instrumentation and breakpoints were removed.
