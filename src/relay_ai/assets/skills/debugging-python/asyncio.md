# Debugging asyncio

## Turn on asyncio debug mode

Run the reproduction with `python -X dev` (or `PYTHONASYNCIODEBUG=1`). Debug mode:

- logs every callback that blocks the event loop longer than 100 ms, with where it ran: the
  usual cause is sync I/O (`requests`, a sync DB driver, `time.sleep`, a sync `invoke`)
  inside async code;
- reports coroutines that were never awaited, with the traceback of where they were created.

## The program hangs

Find out where it is stuck before guessing:

- `faulthandler.dump_traceback_later(30)` at startup dumps every thread's stack if the
  program is still running after 30 seconds;
- `uvx py-spy dump --pid <pid>` prints the current stack of a running process without
  stopping it.

To see pending tasks, print a projection of each one:

```python
for task in asyncio.all_tasks():
    print('[DEBUG-a4f2]', task.get_name(), task.get_coro().__qualname__, task.done())
```

## Common causes

- Blocking call inside async code (see debug mode above).
- A coroutine called without `await`: it never runs.
- `asyncio.CancelledError` swallowed by a broad `except`: cancellation and timeouts stop
  working.
- A task created with `asyncio.create_task` and never awaited or kept: its exception is lost
  ("Task exception was never retrieved").
- An object bound to one event loop used from another: "attached to a different loop", often
  from test fixtures with a different loop scope than the code under test.
- Deadlock: two tasks awaiting each other, or a lock acquired twice.
