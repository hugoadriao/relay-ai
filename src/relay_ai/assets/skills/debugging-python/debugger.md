# The debugger through DebugMCP

DebugMCP gives you VS Code's own debugger as `debugmcp` tools. Python runs through VS Code's
Python extension (debugpy).

## Tools

| Purpose | Tools |
|---|---|
| Session | `start_debugging`, `stop_debugging`, `restart_debugging` |
| Moving | `continue_execution`, `step_over`, `step_into`, `step_out`, `pause_execution` |
| Breakpoints | `add_breakpoint` (accepts a `condition`), `add_logpoint`, `remove_breakpoint`, `clear_all_breakpoints`, `list_breakpoints` |
| Inspection | `list_variable_names` (names and types only), `get_variables_values` (only the names you ask for), `evaluate_expression` |

Check each tool's parameters before calling it. To start a session, prefer running the single
failing pytest test; if starting needs a VS Code launch configuration that the project doesn't
have, ask the developer before creating `.vscode/launch.json`.

## Using it sparingly

1. **Breakpoint placement.** Stop where your hypotheses diverge: the first line where a
   wrong value could already be visible, not the line that raised.
2. **Conditions.** If the line runs many times (a loop, a graph node, a request handler), add
   a condition that matches only the failing case, for example
   `not state.get("intent")` or `order.total < 0`.
3. **Logpoints for loops.** To see how a value evolves across iterations, add a logpoint that
   prints a projection (`{i} {len(batch)}`) instead of stepping through each pass.
4. **At a stop:**
   - call `list_variable_names` first: names and types cost few tokens;
   - use `evaluate_expression` to project large values: `len(messages)`,
     `type(messages[-1]).__name__`, `messages[-1].content[:200]`, `sorted(state)`,
     `response.status_code`;
   - call `get_variables_values` only for variables you know are small.
5. **Stepping.** `step_over` through the suspicious region, `step_into` only the call you
   suspect, `step_out` as soon as you know the answer, `continue_execution` to jump to the
   next breakpoint.
6. **Cleanup.** `clear_all_breakpoints` and `stop_debugging` when done.

Secret values are redacted by DebugMCP; don't try to get around it.
