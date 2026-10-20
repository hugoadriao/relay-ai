# Profile: FastAPI

- **Specialist:** `fastapi-expert`.
- **Activated by:** `fastapi` in the project's dependencies.
- **Report:** `docs/audits/fastapi-<YYYY-MM-DD>.md`, titled "FastAPI audit".
- **Owns:** the app and its lifespan, settings, dependencies, routers and path operations,
  exception handlers, middleware and CORS, WebSocket and SSE endpoints, building the graph's
  `Context` from the request, conversation management and the app's tests. The graph itself
  (nodes, state, tools, the graph factory) belongs to the `langgraph` profile.

## Versions

Read `fastapi`, `starlette` and `pydantic`. FastAPI ships its official agent skill since
0.134.0, and the specialist's rules build on it: if the project is older, add the
structural finding `upgrade-fastapi`.

## Where to look

Questions for `graphify query`: "where is the FastAPI app created and what its lifespan
creates", "routers and their path operations", "WebSocket and streaming endpoints", "which
dependencies provide services", "where exceptions are mapped to responses".

Text search: `FastAPI(`, `lifespan`, `on_event(`, `APIRouter(`, `include_router(`,
`.websocket(`, `WebSocket`, `EventSourceResponse`, `StreamingResponse`, `Depends(`,
`app.state`, `exception_handler`, `add_middleware`, `BaseSettings`, `HTTPException`.

## Inventory

The app and its lifespan (what it creates and closes), settings, routers and path
operations, WebSocket and SSE endpoints (with the messages they exchange), dependencies
(what each provides), exception handlers, middleware and CORS, conversation and connection
management (where its state lives), and the app's tests.
