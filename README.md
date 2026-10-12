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
   implementation skills route specialist work to them), and adds the MCP servers they
   need to `.vscode/mcp.json` (existing entries are kept).
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

Re-running `init` updates everything it installed. It replaces each skill folder and agent
file RelayAI manages, so local edits to those are lost.

To refresh the knowledge graph by hand, use Graphify's own commands: `graphify update .`
for code, `/graphify --update` in Copilot Chat for docs and images.

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

Coming next from RelayAI itself: a FastAPI specialist agent and Python debugging skills.

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
| [uv](https://github.com/astral-sh/uv) | [Astral](https://github.com/astral-sh) | Runs the RelayAI installer and installs Graphify. | MIT / Apache-2.0 |

If you find RelayAI useful, please star and support these projects too.
