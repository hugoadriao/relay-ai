# Debugging the environment

When the code looks right but the program doesn't behave like it, check what is actually
running before changing any code.

## Which Python, which packages

- Interpreter in use: `python -c "import sys; print(sys.executable, sys.version)"`. In a uv
  project, run things through `uv run` so they use the project's environment.
- VS Code may use a different interpreter than the terminal: compare the interpreter selected
  in VS Code with the one above.
- Which module was actually imported, and its version:
  `python -c "import pkg; print(pkg.__file__, getattr(pkg, '__version__', '?'))"`.
- Installed versions and why they are there: `uv pip show <pkg>`, `uv tree --package <pkg>`.

## Common causes

- **Shadowing:** a local file or folder named like a stdlib or installed module (`json.py`,
  `logging/`, `langgraph.py`) is imported instead of the real one. `pkg.__file__` reveals it.
- Wrong virtual environment, or a package installed in another one.
- A dependency upgraded with a breaking change: compare the installed version with the one in
  the lockfile and check the changelog before pinning anything.
- `PYTHONPATH` or an editable install pointing at an old copy of the code.
- Stale `__pycache__` after moving files around: delete it and re-run.
- Missing environment variable or `.env` not loaded: print whether it is set, never its value.
