# Using the debugger sparingly

The official `mcp-debugger` skill explains the tools: the session golden path, launch and
attach, breakpoints by `statement`, `function` or line, path mappings, output and restarts.
Read it before your first session; this file only covers how to spend few tokens with them.
How to start the target in this project is in [launch-and-attach.md](launch-and-attach.md).

1. **Breakpoint placement.** Stop where your hypotheses diverge: the first line where a
   wrong value could already be visible, not the line that raised. Prefer `statement` or
   `function` breakpoints when the mode allows them, so a moved line doesn't break them.
2. **Conditions.** If the line runs many times (a loop, a graph node, a request handler), add
   a condition that matches only the failing case, for example
   `not state.get("intent")` or `order.total < 0`.
3. **Logpoints for loops.** To see how a value evolves across iterations, set a logpoint
   (`logMessage`) that prints a projection, such as `{i} {len(batch)}`, instead of stepping
   through each pass, and read it with `get_output`.
4. **At a stop:**
   - `get_stack_trace` once, to confirm where you are; read only the top frames;
   - look at names and types before values (`get_scopes`, then `get_variables` for one
     scope); avoid `get_local_variables` when the frame holds large objects;
   - use `evaluate_expression` to project large values: `len(messages)`,
     `type(messages[-1]).__name__`, `messages[-1].content[:200]`, `sorted(state)`,
     `response.status_code`;
   - call only pure functions from `evaluate_expression`: anything with side effects
     (writing to a database, HTTP or LLM calls) runs for real in the target.
5. **Stepping.** `step_over` through the suspicious region, `step_into` only the call you
   suspect, `step_out` as soon as you know the answer, `continue_execution` to jump to the
   next breakpoint.
6. **Waiting for a stop.** There is no tool that waits. `start_debugging` returns `paused`
   when a breakpoint is hit within its readiness window; after `continue_execution`, check
   `list_debug_sessions` until the state is `paused`, at growing intervals, and read new
   output with `get_output` and its `since` cursor instead of re-reading everything.
7. **Cleanup.** `clear_breakpoints` and `close_debug_session` when done; the rest is in
   [launch-and-attach.md](launch-and-attach.md).

Secret values are redacted by the debugger; don't turn redaction off.
