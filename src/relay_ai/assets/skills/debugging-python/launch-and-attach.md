# Launch and attach

How to get the target running under the debugger in this project. The official
`mcp-debugger` skill explains the tools themselves.

## 1. Ask the developer which mode

Ask every time, before preparing anything, and use the mode they choose:

- **Launch:** the debugger starts the target on this machine, with the project's own
  interpreter. Services the app needs (database, queues) run in containers and are exposed
  to this machine.
- **Attach:** the target runs where the app already runs, usually a container, under a
  `debugpy` that listens on a port; the debugger connects to it.

## 2. Read the catalog

The catalog is `docs/agents/debugging.md` (structure in
[catalog-template.md](catalog-template.md)): one recipe per mode, the files each recipe was
derived from, and the problems already solved in this project.

- **The chosen mode has a recipe:** compare the fingerprint of each source file
  (`git hash-object <file>`) with the recorded one. Unchanged: follow the recipe. Changed:
  re-check only the steps derived from that file (step 3 below), then go on. When a
  recorded step fails, find out why and fix that step.
- **No recipe for the mode** (or no catalog): discover the environment (step 3) and build
  the recipe as you go.

## 3. Discover the environment (read only)

1. **Compose.** Look for `compose.yaml`, `compose.yml`, `docker-compose.yml` or
   `docker-compose.yaml`, and an override next to it. Read the effective configuration with
   `docker compose config --no-interpolate --no-env-resolution`: without both options the
   output carries the values of the `.env` and `env_file` files, which hold secrets. Use
   `docker compose ps` to see what is running.
2. **Dockerfile.** For each service you need, open the Dockerfile its `build` section
   points to: the base image and its Python version, the system packages it installs, how
   it installs dependencies (`uv`, `pip`), `WORKDIR`, and `CMD`/`ENTRYPOINT`.
3. **Project.** Does it use uv (`uv.lock`, `[tool.uv]`)? Which Python does it expect
   (`.python-version`, `requires-python`)?

What each mode needs from this:

- **Attach:** the service and its command (a reloader such as `uvicorn --reload` restarts
  the app whenever a file changes in the directories it watches, the working directory by
  default); the bind mounts and the `working_dir`, which give the path mapping (the host
  side is `localRoot`, the container side is `remoteRoot`); whether the image has `pip` or
  `uv`; the ports already published.
- **Launch:** the Python version of the image, to compare with this machine's; system
  packages the image installs that this machine may lack; the services the app depends on
  (`depends_on`) and the names of the environment variables that point to them (a service
  host name such as `db` becomes `localhost` with the published port); the names of the
  other environment variables the app reads, and the file each comes from.

## 4. The override file

Never edit the project's compose files. Ports go in a separate file,
`docs/agents/debugging.compose.yaml`, passed with `-f` after the project's files:

```bash
docker compose -f compose.yaml -f docs/agents/debugging.compose.yaml up -d <services>
```

- Compose appends the override's ports to the service's own.
- With `-f`, Compose no longer loads the project's `compose.override.yaml` by itself: when
  the project has one, list it too, before the debugging file.
- Never name the file `compose.override.yaml`: Compose loads that name automatically, in
  every `docker compose up` the developer runs.
- Publish ports only on the host's loopback (`127.0.0.1:5432:5432`). A database on other
  interfaces is open to the network, and anyone who reaches a `debugpy` port can run code
  in the debugged process.
- Ask the developer before starting or stopping services.

## 5. Attach

1. **`debugpy` without changing the container's environment:**
   `python -m pip install --target /tmp/debugpy debugpy`, then run the target with
   `PYTHONPATH=/tmp/debugpy`. If the image has uv, `uv run --with debugpy` does the same.
2. **Start the target under `debugpy`**, preferably an existing test or the smallest command
   that reproduces the problem, in the background, listening on `0.0.0.0:5678` inside the
   container (needed for connections from outside it), with that port published on the
   host's loopback through the override file. Redirect the target's output to a file in
   the container: a process started in the background doesn't send it to the debugger.
3. **Paths:** breakpoints use the container's paths (as `get_stack_trace` shows them), a
   `function` breakpoint, or the path mapping from the bind mount.
4. **Reloaders:** never create or delete files inside a directory a reloader watches: every
   change restarts the app. Temporary files go to `/tmp`.

## 6. Launch

1. **Interpreter:** in a uv project, `uv sync`, then `uv pip install debugpy`: it goes into
   `.venv` only, without touching `pyproject.toml` or `uv.lock`, and the next `uv sync`
   removes it. The session's `executablePath` is that interpreter (`.venv/bin/python`, or
   `.venv\Scripts\python.exe` on Windows). Without uv, ask the developer before installing
   `debugpy` in the project's environment.
2. **Python version:** if this machine's interpreter differs from the image's Python minor
   version, tell the developer before going on: behaviour can differ.
3. **Services:** expose the ones the app needs through the override file, and start them.
4. **Environment:** set the variables the app reads, with service host names turned into
   `localhost` and the published ports, taking the values from the project's own files at
   run time.

## 7. Clean up: restore what you found

- `clear_breakpoints` and `close_debug_session`; stop the target process you started.
- Stop only the services you started; leave running the ones that already were.
- Launch: `uv sync` to remove `debugpy` from `.venv`.
- Attach: delete `/tmp/debugpy` and the temporary files you created in the container.
- The catalog and the override file stay, for the next session.

## 8. Record the recipe

Once the mode has worked end to end (the debugger stopped at a breakpoint in the target),
write or update its recipe in `docs/agents/debugging.md`, following
[catalog-template.md](catalog-template.md), and tell the developer what you recorded: the
file is visible in git, so they review it and decide whether to commit it. If the mode
didn't work, don't record a recipe.

- Write it in English.
- Record names, never values: environment variable names and the file each value comes
  from, never a secret.
- Record the fingerprint (`git hash-object <file>`) of every file the recipe was derived
  from.
- Add to "Problems and solutions" any problem you solved on the way, with its solution, so
  the next session doesn't rediscover it.
