# Profile: LangGraph and LangChain

- **Specialist:** `langgraph-expert`.
- **Activated by:** `langgraph`, `langchain` or `langchain-core` in the project's
  dependencies.
- **Report:** `docs/audits/langgraph-<YYYY-MM-DD>.md`, titled "LangGraph audit".
- **Owns:** the graphs, nodes, state, tools, prompts, the `context_schema` and the graph
  factory. The FastAPI app, its lifespan and the endpoints that run the graphs belong to the
  `fastapi` profile.

## Versions

Read `langgraph`, `langchain` and `langchain-core`. The rules assume LangChain v1 and
LangGraph 1.x: if the project is older, add the structural finding `upgrade-langchain-v1`.

## Where to look

Questions for `graphify query`: "where is the StateGraph compiled and invoked", "agents
built with create_agent and their tools", "where are the prompts loaded", "where are the
services the graph uses created".

Text search: `StateGraph(`, `.compile(`, `create_agent(`, `@tool`, `BaseTool`,
`context_schema`, `system_prompt`, `ainvoke(`, `astream(`.

## Inventory

Graphs (where they are built, compiled and invoked), nodes, agents, tools, state schemas,
prompts (where they live and how they are loaded), services (where they are created and how
they reach nodes and tools), checkpointer and store. List the FastAPI entry points that run
the graphs only as references: they belong to the `fastapi` profile.
