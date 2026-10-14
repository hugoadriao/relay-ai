# Debugging performance and memory

Measure first, fix second. A guess about what is slow is usually wrong.

## Time

- Baseline: time the reproduction (`time.perf_counter()` around the suspect call, or the
  test duration) so you can show the fix made it faster.
- Profile, keeping the output short:
  `python -m cProfile -s cumulative script.py | head -n 30`.
- For a readable call tree: `uvx pyinstrument script.py`.
- For a process that is already running (a server, a stuck worker):
  `uvx py-spy top --pid <pid>` or `uvx py-spy dump --pid <pid>`.

## Memory

Compare two `tracemalloc` snapshots and print only the top entries:

```python
import tracemalloc

tracemalloc.start()
before = tracemalloc.take_snapshot()
run_suspect_code()
after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, 'lineno')[:10]:
    print('[DEBUG-a4f2]', stat)
```

## Common causes

- N+1 queries or one request per item inside a loop.
- Recomputing or reloading something that could be built once (a compiled graph, a model
  client, a regex, a parsed file).
- Sync I/O inside async code, serialising work that should run concurrently.
- Unbounded caches or lists that keep growing across requests.
