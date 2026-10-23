# Coverage of the change

The target is every line and every branch of the code the change adds or alters, reached through
the agreed seams. Branches count: a line report shows an `if` as covered when only one of its
paths ran.

## Measuring

Use what the project declares:

- **pytest-cov**: `pytest --cov=<package> --cov-branch --cov-report=term-missing`.
- **coverage**: `coverage run --branch -m pytest` (or `-m unittest`), then `coverage report -m`.

When it declares neither:

- **In a uv project**, run the tool in a temporary environment, which changes neither
  `pyproject.toml`, `uv.lock` nor the project's environment:
  `uv run --with pytest-cov pytest --cov=<package> --cov-branch --cov-report=term-missing`. With
  `unittest`: `uv run --with coverage coverage run --branch -m unittest`, then
  `uv run --with coverage coverage report -m`.
- **Otherwise**, don't measure: go through each branch of the changed code, check that a test
  exercises it, and say in the report that coverage was not measured.

## Reading the report against the change

`term-missing` lists the missing lines and the partial branches (`8->10`: the jump from line 8
to line 10 never happened). Cross them with the lines of the change (`git diff -U0` from where
the change started, on the source files): every missing line or branch inside the change is a
gap to close. Gaps outside the change go in the report, for the developer.

## Closing a gap

- **A behaviour the public seam's tests don't exercise yet**: add the scenario.
- **Code no public input reaches**: dead code. Point it out and remove it.
- **`# pragma: no cover`** only where the tool is wrong (`if TYPE_CHECKING:`), as
  `writing-python` says for tool directives; a gap is closed by a test or by removing dead code.
