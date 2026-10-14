# Debugging LangGraph graphs

A graph run produces a lot of traffic (messages between agents and tools) that is mostly
unrelated to the bug. Find the guilty node first, cheaply; open the debugger only inside it.

## 1. Find the node: stream only the updates

`stream_mode="updates"` yields, after each node, only what that node changed. Print the node
name and the shape of its update, not the update itself:

```python
async for chunk in graph.astream(inputs, config, stream_mode='updates'):
    for node, update in chunk.items():
        print(
            '[DEBUG-a4f2]',
            node,
            {key: type(value).__name__ for key, value in (update or {}).items()},
        )
```

The first node whose update is missing a key, or has the wrong type, is where to look.
Narrow further by printing one projected value (`len(update["messages"])`,
`update["intent"]`) for that node only.

## 2. Inspect the state between steps

With a checkpointer, every step is saved. Walk the history and project each snapshot:

```python
async for snapshot in graph.aget_state_history(config):
    print('[DEBUG-a4f2]', snapshot.next, sorted(snapshot.values))
```

`snapshot.next` tells which node runs next; `snapshot.values` is the state at that point.
Project the fields you need instead of printing `snapshot.values`.

## 3. Stop inside the node

Once you know the node, put a breakpoint inside its function (see [debugger.md](debugger.md))
with a condition that matches the failing state, and observe the inputs it received and the
update it returns.

## What usually goes wrong

- A field the node expects was never written: the node responsible for it (or the LLM's
  output schema) is the bug, not the node that fails.
- Two writers on a field without a reducer: one update silently overwrote the other.
- A conditional edge routed on a value with an unexpected type or casing.
- Sync `invoke` / blocking I/O inside an async node: see [asyncio.md](asyncio.md).

Check API details against the LangGraph docs (`docs-langchain` / `reference-langchain` MCP
servers) for the version installed in the project.
