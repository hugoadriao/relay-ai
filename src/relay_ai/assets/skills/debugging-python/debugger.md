# The debugger: mcp-debugger

`mcp-debugger` is a local MCP server that drives real debuggers through the Debug Adapter
Protocol; for Python it uses `debugpy`. It runs on this machine, needs no IDE and sends
nothing out. Check each tool's parameters before calling it, and always pass absolute paths.

## Tools

| Purpose | Tools |
|---|---|
| Session | `create_debug_session`, `attach_to_process`, `start_debugging`, `close_debug_session`, `list_debug_sessions` |
| Moving | `continue_execution`, `step_over`, `step_into`, `step_out`, `pause_execution`, `wait_for_stop` |
| Breakpoints | `set_breakpoint` (accepts a `condition`, or a `logMessage` for a logpoint), `list_breakpoints`, `remove_breakpoint`, `clear_breakpoints` |
| Inspection | `get_stack_trace`, `get_scopes`, `get_variables`, `get_local_variables`, `evaluate_expression`, `get_source_context`, `get_output` |

## Starting a session on a test

`debugpy` is not part of the project, so run the target under a temporary one that waits
for the debugger. In a uv project, run this **in the background** (it blocks until you
attach):

```bash
uv run --with debugpy python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m pytest tests/test_orders.py::test_total -x -q
```

Then `create_debug_session` for Python and `attach_to_process` to `127.0.0.1:5678`. Set your
breakpoints right after attaching, before you continue. If the project doesn't use uv, ask
the developer before installing `debugpy` in its environment.

`"verified": false` right after `set_breakpoint` is normal: `debugpy` binds a breakpoint
when its module is loaded.

## Using it sparingly

1. **Breakpoint placement.** Stop where your hypotheses diverge: the first line where a
   wrong value could already be visible, not the line that raised.
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
     `response.status_code`.
5. **Stepping.** `step_over` through the suspicious region, `step_into` only the call you
   suspect, `step_out` as soon as you know the answer, `continue_execution` to jump to the
   next breakpoint, `wait_for_stop` after starting or continuing.
6. **Cleanup.** `clear_breakpoints` and `close_debug_session` when done, and stop the
   background process if it is still running.

Secret values are redacted by the debugger; don't turn redaction off.
