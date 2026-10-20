# RelayAI

Instalador por projeto (`uvx ... relay-ai init`) de agentes e skills para o GitHub Copilot
(VS Code) e o OpenCode: escopo e interrogação do desenvolvedor antes de qualquer código ser escrito
(via mattpocock/skills), com descoberta de projeto assistida por um grafo de conhecimento
local (Graphify).

@SCOPE.md

## Antes de fazer qualquer coisa

O `SCOPE.md` acima é a fonte única de verdade de toda decisão arquitetural já tomada
neste projeto. Leia a tabela de decisões inteira antes de sugerir qualquer mudança que
contradiga alguma delas — se achar que uma decisão fechada merece ser revista, pergunte
antes de simplesmente ignorá-la.

## Por onde continuar agora

As seções "Planejado" e "Em aberto" do `SCOPE.md` são o trabalho pendente mais recente:

- Validar o `langgraph-expert` no VS Code (checklist em "Planejado" no `SCOPE.md`).
- Validar a `debugging-python` num projeto real (checklist em "Planejado") e então
  confirmar nome e invocação (#28).
- Validar o `fastapi-expert` (#42, #43) e a `auditing-code` (#44) num projeto real
  (checklists em "Planejado").
- Validar a memória de exploração (#49) num projeto real e medir o ganho (checklist em
  "Planejado").
- Conteúdo próprio novo (outro especialista ou skill): grillar nome, escopo e sobreposição
  com o mattpocock/skills antes de escrever; nada deve ser inventado além do que está
  decidido sem perguntar.

## Desenvolvimento da CLI

- Código em `src/relay_ai/` (Python ≥ 3.12, ruff com 100 colunas e aspas simples).
- Conteúdo próprio em `src/relay_ai/assets/agents/` (fonte única por agente, #30) e
  `src/relay_ai/assets/skills/` (#16). As diferenças entre plataformas ficam em `platforms.py`.
- Comandos: `init`, `update` e `uninstall` (#29); `install.py` cobre `init`/`update`.
- Testar ponta a ponta: `uvx --no-cache --from . relay-ai init <pasta-de-teste> --platform both` (sem
  `--no-cache`, o uv reaproveita a build anterior enquanto a versão não muda) — nunca rode
  o `init` dentro deste repositório, ele escreve `.github/` e `graphify-out/` no destino.

## Convenções

- Nomes de skills, comandos e identificadores: sempre em inglês.
- Documentação de apoio (este arquivo, `SCOPE.md`, `README.md`): pode ficar em português.
- Toda decisão nova vai para a tabela de decisões do `SCOPE.md`, no mesmo formato das
  existentes — não deixe decisões só na conversa.
