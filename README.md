# RelayAI

Skills for GitHub Copilot that scope your work and interrogate you about it before any
code gets written — plus project-aware discovery powered by a local knowledge graph
([Graphify](https://github.com/Graphify-Labs/graphify)).

RelayAI doesn't reinvent what already exists: it builds on top of other open-source
projects and adds what's missing between them. See [Credits](#credits).

## Installation (GitHub Copilot in VS Code)

Prerequisite: [uv](https://docs.astral.sh/uv/getting-started/installation/) — the same
tool Graphify needs.

From the root of your project:

```bash
uvx --from git+https://github.com/hugoadriao/relay-ai relay-ai init
```

Then reload VS Code (so `graphify` is on the agents' PATH) and, once, in Copilot Chat:

```
/setup-matt-pocock-skills
```

### What `relay-ai init` does

1. Installs the Graphify CLI if it's missing (`uv tool install graphifyy`) and puts it on
   your PATH (`uv tool update-shell`).
2. Copies RelayAI's own agents into `.github/agents/` and skills into `.github/skills/`
   (see [What's in it](#whats-in-it)), lists the specialist agents in a
   `relay-ai` section of `.github/copilot-instructions.md` (so ticket-writing and
   implementation skills route specialist work to them), adds the MCP servers they
   need to `.vscode/mcp.json` and recommends the VS Code extensions they rely on in
   `.vscode/extensions.json` — VS Code then offers to install them (existing entries are
   kept in both files).
3. Downloads [mattpocock/skills](https://github.com/mattpocock/skills) and copies its
   engineering and productivity skills into `.github/skills/`, unmodified, each with its
   original MIT `LICENSE`.
4. Sets Graphify up exactly as it's designed to work:
   - adds `.github/agents/` and `.github/skills/` to `.graphifyignore`, so the graph
     describes your code, not the installed agents and skills (existing lines in the file
     are kept);
   - `graphify vscode install` — writes `.github/copilot-instructions.md`, so Copilot
     always checks the knowledge graph before answering questions about your code;
   - `graphify hook install` — git hooks that update the graph on every commit and
     branch checkout (skipped if the project isn't a git repository);
   - `graphify update .` — builds the initial code graph (no LLM needed).

5. Keeps what it installed out of git: the agents and skills, plus the config files it
   created, are listed in `.git/info/exclude` (local to your clone, so not even that list
   shows up in git). Graphify's own files (`graphify-out/`, `.gitattributes`) stay visible,
   because Graphify is designed for the graph to be committed and shared. If `init` had to
   change a file your repository already tracks (e.g. an existing
   `.github/copilot-instructions.md`), it tells you, so you can review that diff.
6. Records everything it installed or added in `.github/relay-ai.json`, so `update` and
   `uninstall` touch only what is RelayAI's.

`init` never overwrites your own agents and skills: if one of yours has the same name as
one RelayAI installs, yours is kept and `init` tells you.

To refresh the knowledge graph by hand, use Graphify's own commands: `graphify update .`
for code, `/graphify --update` in Copilot Chat for docs and images.

## Updating

From the root of your project:

```bash
uvx --from git+https://github.com/hugoadriao/relay-ai relay-ai update
```

`update` fetches the latest RelayAI and refreshes everything it manages: its agents and
skills, mattpocock/skills, the `relay-ai` section of `.github/copilot-instructions.md`, the
VS Code config entries, the git excludes and the graph. It removes agents and skills that
are no longer part of RelayAI, and ends with a summary of what was updated, added and
removed.

Local edits to the agents and skills RelayAI installed are overwritten, so put your own
customisations in agents and skills with other names.

Graphify isn't upgraded by `update`, because it's installed machine-wide and other projects
may use it. Upgrade it when you want with:

```bash
uv tool upgrade graphifyy
```

DebugMCP is a VS Code extension and updates with your other extensions. If `uvx` ever seems
to run an old RelayAI, add `--refresh` to the command to bypass its cache.

## Uninstalling

From the root of your project:

```bash
uvx --from git+https://github.com/hugoadriao/relay-ai relay-ai uninstall
```

It lists exactly what it will remove and asks for confirmation (`--yes` skips the
question). It removes only what `.github/relay-ai.json` says RelayAI installed or added:

- its agents and skills (and mattpocock/skills), not yours;
- its section of `.github/copilot-instructions.md`, keeping the rest of the file;
- the MCP servers, extension recommendations and `.graphifyignore` lines it added, keeping
  the entries you had;
- the files it created, if nothing else is left in them, and its block in
  `.git/info/exclude`.

Graphify's setup in the project (git hooks, its section of
`.github/copilot-instructions.md`, `graphify-out/`) is kept, because your team may share
the graph. To remove the hooks and its section too, add `--graphify` (it also works after
RelayAI was already uninstalled):

```bash
uvx --from git+https://github.com/hugoadriao/relay-ai relay-ai uninstall --graphify
```

The graph in `graphify-out/` is never deleted; remove that folder yourself if you don't want
it. Graphify itself stays installed on your machine for other projects; remove it with
`uv tool uninstall graphifyy`.

## Troubleshooting

**Windows: "this project's path is too long".** With Windows long paths disabled, files
deeper than 260 characters can't be written, and Graphify's cache files sit about 130
characters below your project folder. `init` checks this before installing anything.
Either enable long paths, in PowerShell run as administrator:

```powershell
New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force
```

and open a new terminal, or move the project to a shorter path (e.g. `C:\dev\<project>`).

## What's in it

- Engineering and productivity skills (`grill-me`, `tdd`, `to-spec`, `code-review`,
  `diagnosing-bugs`, …) from [mattpocock/skills](https://github.com/mattpocock/skills).
  See its README for the full list.
- Project discovery through Graphify's knowledge graph, kept up to date by its git hooks.

- **`langgraph-expert`** (RelayAI) — a LangGraph specialist agent for async
  Python/FastAPI projects. Pick it in the Copilot Chat agent picker, or let `/implement`
  and `/implement-spec` delegate LangGraph tickets to it (tickets get a
  `**Specialist:** langgraph-expert` line from `/to-tickets`). It checks the live LangGraph
  docs before using an API, works test-first, and calls out hacky workarounds plainly
  — flows patched with `if`s, unnecessary code, over-engineering, LangGraph misuse — with
  a simpler way to build the feature.

- **`debugging-python`** (RelayAI) — a Python debugging skill the agent loads on its own
  when debugging, alongside `diagnosing-bugs`. It makes the agent observe the real values at
  the point of failure with VS Code's debugger (through DebugMCP: install it when VS Code
  recommends it) instead of guessing, while keeping token use low: shape before values,
  projections instead of dumping large objects, conditional breakpoints.

Coming next from RelayAI itself: a FastAPI specialist agent.

See `SCOPE.md` for the full decision log behind this project.

## Credits

RelayAI exists because of the work of other developers. We use their projects as they
are, straight from their original sources, without modifying them. All credit for them
goes to their authors, and bugs or ideas about them belong upstream.

| Project | Author | What RelayAI uses it for | License |
|---|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | [Matt Pocock](https://github.com/mattpocock) | All the engineering and productivity skills (scoping, grilling, TDD, specs, reviews…). It's also the model RelayAI's own structure and conventions are based on. | MIT |
| [Graphify](https://github.com/Graphify-Labs/graphify) | [Graphify Labs](https://github.com/Graphify-Labs) | The local knowledge graph behind project discovery, and its automatic updates. | MIT / Apache-2.0 |
| [LangChain docs MCP servers](https://docs.langchain.com/use-these-docs) | [LangChain](https://github.com/langchain-ai) | Live LangGraph/LangChain documentation and API reference for the `langgraph-expert` agent. | hosted service |
| [DebugMCP](https://github.com/microsoft/DebugMCP) | [Microsoft DevLabs](https://github.com/microsoft) | Gives the agent VS Code's debugger (breakpoints, stepping, variable inspection) for the `debugging-python` skill. | MIT |
| [uv](https://github.com/astral-sh/uv) | [Astral](https://github.com/astral-sh) | Runs the RelayAI installer and installs Graphify. | MIT / Apache-2.0 |

If you find RelayAI useful, please star and support these projects too.
