---
name: testing-python
description: Python testing toolkit for the tdd skill — the test tools the project declares (pytest, pytest-mock, unittest.mock, unittest), mocks only at external boundaries, every line and branch of the change covered, hermetic tests that never depend on environment variables or .env files, and tests that pay only for what they verify. Use whenever you write, update or review Python tests, together with the tdd skill.
---

# Testing Python

The `tdd` skill gives the process: agree the seams, then red → green, one slice at a time, with
tests that check behaviour through public interfaces. This skill gives the Python tools for that
loop and the rules this project adds; where it departs from `tdd`, it says so. Test code is
Python like any other: write it following the `writing-python` skill.

## Precedence

1. **The project's own testing setup wins**: a documented testing standard (`CONTRIBUTING.md`,
   `AGENTS.md`) and the pytest configuration (`[tool.pytest.ini_options]` or `pytest.ini`:
   markers, `asyncio_mode`, `testpaths`). Follow it, and point out where it conflicts with this
   skill.
2. **This skill** covers what the project doesn't set.
3. **Undocumented habits of the existing tests** come last.

## Tools: what the project declares

A tool is available when the project declares it as a direct dependency
(`[dependency-groups]`, `[project.optional-dependencies]`, `[tool.uv] dev-dependencies`,
`requirements*.txt`): that is what CI installs. A package that is only importable, because
another one depends on it, doesn't count. Use the highest tier the project has:

1. **pytest + pytest-mock**: mocks through the `mocker` fixture. It is `unittest.mock` applied
   by a fixture: the same objects, and every patch is undone at the end of the test.
2. **pytest + `unittest.mock`**: `patch` as a context manager or decorator.
3. **`unittest` + `unittest.mock`**.

Work with the tools the project has: adding a test dependency is the developer's call, not
part of the task.

pytest doesn't inject fixtures into `unittest.TestCase` methods, so `mocker` never reaches
them. In a pytest project whose tests are `TestCase` classes, new test files follow pytest; the
existing classes are a deviation to point out (see [Verify](#verify)), and a test you add inside
one of them follows that class, with `unittest.mock`.

Before writing an async test, read [async.md](async.md).

## What the tests cover

- **Behaviour through the public interface**, named for the behaviour
  (`test_member_pays_discounted_price`), as in `tdd`. Private functions and methods, and
  `__init__`, run through the public ones.
- **Cover everything.** This departs from `tdd`'s "You can't test everything". The seams are
  still agreed with the developer, and they decide *where* the tests go. Coverage decides *how
  much*: every line and every branch of the code your change adds or alters, reached through
  those seams. See [coverage.md](coverage.md).
- **An uncovered line inside a private helper** is one of two things: a behaviour the tests of
  the public seam don't exercise yet (add that scenario), or dead code no public input reaches
  (point it out and remove it). A test that calls the private helper directly hides the second.
- **When updating a test file**, keep the scenarios that still hold, delete the ones that test
  removed behaviour, and add the ones the new branches need.

## How the tests are written

- **Layout**: follow the project's. With no tests yet, a `tests/` folder at the root that
  mirrors the package (`src/shop/billing/invoice.py` → `tests/billing/test_invoice.py`).
- **Functions by default.** Group them in a class per seam only when one file covers more than
  one seam; inside a class, methods follow the order in `writing-python`.
- **Arrange, act, assert** as three blocks separated by a blank line, without markers.
- **`parametrize`** (`subTest` in `unittest`) when cases differ only in their data.
- **Fixtures through the `conftest.py` hierarchy.** Before creating one, read every
  `conftest.py` from the test's folder up to the root, and reuse what fits, from the nearest
  level. A new fixture goes at the level of the tests that share it: the test file, its folder's
  `conftest.py`, a subsystem's, or the root's. Each fixture is defined once, at the highest
  level that needs it.

## Mocks: only at external boundaries

Mock what lies outside the code under test: other services, LLMs, HTTP, the database when the
project has no test database, the clock, randomness, third-party libraries. The project's own
code runs for real.

- **Inject before patching.** Where the code receives the dependency (a parameter, a
  constructor, a LangGraph `Context`, FastAPI's `dependency_overrides`), hand the mock in there.
  Patch by module path only when the code creates the client itself, and patch the name where
  it is used (`shop.billing.httpx`), not where it is defined.
- **Keep the real signature**: `create_autospec(Client, instance=True)`,
  `patch(..., autospec=True)` or `mocker.create_autospec(...)`. A plain `MagicMock` accepts any
  call, so the test keeps passing after the real API changed.
- **Awaited collaborators are `AsyncMock`s, checked with `assert_awaited*`.** `assert_called*`
  also passes when the coroutine was created and never awaited.
- **Check a call when the call is the behaviour**: an email sent, a payment charged, a record
  written to another system. A mock that only supplies data is checked through the result. Call
  counts and call order are checked only when they are the behaviour.
- **Patch only what the test needs**: an unused patch is dead code.
- **Database**: the project's test database fixture when it has one (in-memory SQLite,
  testcontainers, a transaction rolled back after each test); otherwise mock at the repository
  or session boundary. Building test database infrastructure is a change to agree with the
  developer first.
- **Clock and randomness**: the time-control library the project declares; otherwise inject the
  clock or the generator, or patch it where it is used.

## Hermetic: tests own their configuration

Every test is *hermetic*: it passes with the `.env` empty or missing, and it never passes
because the developer's `.env` is filled in. Each test sets the configuration values it uses,
fictitious ones, and the suite switches the real environment off around every test.

The developer's `.env`, `settings.ini` and any other configuration file hold their secrets:
take variable names from the settings model, `.env.example` or the code, and never read, print,
move, rename or edit those files.

A requirement such as "the application refuses to start without `API_KEY`" is tested too: the
test removes the variable, checks the failure, and passes.

Before a test touches configuration, before creating a suite's first `conftest.py`, and when the
application reads its configuration at import time, read [environment.md](environment.md).

## Cost: each test pays only for what it verifies

Whatever a test spends on something it doesn't verify is *accidental cost*, and the test is
written without it. For example: a password hash that takes 0.5 s by design, run for the 100
users a test creates; a real `sleep`, timeout or retry backoff; more data than the behaviour
needs; a real network call; a heavy model or file loaded for a test that doesn't look at it.
These illustrate, they don't limit: the question is always what the test verifies, and what
else it pays for.

Remove accidental cost in this order:

1. **The smallest volume that shows the behaviour**: one user, not a hundred. When the quantity
   is the behaviour, keep it and make the expensive part of each item cheap.
2. **A cheaper setting the project offers for tests**, such as a faster password hasher in the
   test settings (Django's documentation recommends exactly this).
3. **A fast implementation injected at the seam.**
4. **A fake or a patch at the boundary** with the external library (the hashing library, the
   clock).

If none of these exists, point out the missing seam and propose it; adding it changes
application code, so do it only with the developer's agreement.

A requirement that is expensive by nature ("passwords are stored with the configured algorithm
and cost") gets one test of its own, at the real cost. Mark it as slow only if the project
already has a marker for that.

## Verify

1. **Before changing anything, run the whole suite** and note the failures that already exist:
   they are reported as pre-existing, neither blamed on your change nor silently fixed.
2. **During the loop, run only the test at hand** (`pytest path/to/test_file.py::test_name -q`).
3. **After writing**, run `ruff check --fix` and `ruff format` on the test files too
   (`writing-python`), and measure the coverage of the change ([coverage.md](coverage.md)).
4. **Run the whole suite again**, with `--durations=10` (pytest; `unittest` has it since Python
   3.12). Done when it has no failure that wasn't there in step 1. A test you wrote among the
   slowest has its accidental cost removed, or the reason it is slow goes in the report.
5. **Point out the tests outside these rules**, in the files you touched and in the suite:
   `TestCase` classes in a pytest project, tests that need the `.env`, accidental cost, private
   helpers tested directly. Bring them up to these rules only with the developer's agreement, in
   a commit separate from your change.

## Report

At the end, in a few lines:

- the tests added or changed;
- the coverage of the change, or "not measured" and why;
- the suite before and after, with the failures that already existed;
- the slow tests and the tests outside these rules that you pointed out.
