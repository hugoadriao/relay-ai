# Catalog template

Structure of `docs/agents/debugging.md`. Keep the section names; fill in only the modes that
have worked in this project. Text in angle brackets is filled in; the comments say what goes
in each part and are not copied.

````markdown
# Debugging environment

<!-- Written by the debugging agent after a mode worked end to end. Read before every
     debugging session. English only; names, never secret values. -->

## Sources

<!-- Every file a recipe was derived from, with its fingerprint (`git hash-object <file>`).
     When a fingerprint no longer matches, re-check the steps derived from that file. -->

| File | Fingerprint | Used by |
|---|---|---|
| `<path>` | `<hash>` | launch / attach |

## Launch

- Verified: <YYYY-MM-DD>
- Interpreter: <how the environment is prepared, e.g. the uv commands, and the interpreter path>
- Python: <version here and in the image>
- Services: <service: published port, from `docs/agents/debugging.compose.yaml`>
- Environment variables: <NAME: the file its value comes from, and any host name to replace>
- Start: <how the target is started under the debugger>
- Cleanup: <what to undo afterwards>

## Attach

- Verified: <YYYY-MM-DD>
- Service: <compose service and how the app runs in it>
- debugpy: <how it gets into the container>
- Start: <the command that runs the target under debugpy, and where its output goes>
- Port: <the published loopback port>
- Paths: <localRoot → remoteRoot, or container paths>
- Cleanup: <what to undo afterwards>

## Problems and solutions

<!-- Each problem solved in this project during a debugging session, with its cause and
     solution. -->
````
