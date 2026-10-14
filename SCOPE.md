# SCOPE.md

## Projeto

- **Nome**: RelayAI
- **Repositório**: [github.com/hugoadriao/relay-ai](https://github.com/hugoadriao/relay-ai.git)
- **Pacote / comando de instalação**: `relay-ai` (`uvx ... relay-ai init`, ver #10)

## Objetivo do projeto

Funcionar de maneira semelhante ao [mattpocock/skills](https://github.com/mattpocock/skills):
instalação fácil + skills que determinam o escopo de uma atividade e questionam o
desenvolvedor sobre como ela deve ser construída, antes de qualquer código ser escrito.

**Foco inicial**: GitHub Copilot no VS Code. O dev instala o RelayAI **dentro de um projeto
dele**: os `.md` de skills, agentes e comandos são copiados para os caminhos que o VS Code
lê, e todas as dependências (Graphify, skills do mattpocock) ficam instaladas e prontas no
mesmo passo. Suporte a outros agentes (Claude Code, Codex, Cursor, etc.) fica para depois.

## Convenções herdadas do mattpocock/skills

- Cada skill é uma pasta com um `SKILL.md` (formato comum, lido por qualquer agente
  compatível).
- **User-invoked**: reachable apenas quando o dev digita o comando. Papel: orquestrar.
- **Model-invoked**: o próprio agente pode decidir usá-la quando a tarefa pede. Papel:
  carregar uma disciplina reutilizável.
- Uma skill user-invoked pode chamar uma model-invoked, nunca o contrário, e uma
  user-invoked nunca chama outra user-invoked diretamente.

## Decisões registradas

| # | Decisão | Status |
|---|---------|--------|
| 1 | Graphify (`Graphify-Labs/graphify`) é dependência **obrigatória** da família de skills de descoberta de projeto — sem ele, essas skills não rodam. | Fechado — hoje: dependência obrigatória do `relay-ai init` (#10), que aborta sem ele |
| 2 | A descoberta do projeto é feita por **duas skills separadas**, não uma só, para preservar a convenção user-invoked / model-invoked:<br>• `survey` (user-invoked): setup inicial do repo + comando manual de atualização do grafo.<br>• `gap-watch` (model-invoked): o próprio agente aciona quando percebe, durante o trabalho normal, que algo não está representado no grafo. | Revogado por #15 (`gap-watch` removido em #12, `survey` removido em #15) |
| 3 | O resultado de `survey`/`gap-watch` **não** alimenta automaticamente uma sessão de grilling/escopo. Fica como artefato à parte (`graph.json` / `GRAPH_REPORT.md`, gerados pelo próprio Graphify), consultado sob demanda por quem precisar. | Revisto por #11: os agentes consultam o grafo **sempre** para descoberta; o que continua proibido é injetar o grafo automaticamente numa sessão de grilling |
| 4 | Gatilhos de `survey`: (a) setup inicial do repo (equivalente ao `/setup-matt-pocock-skills` de lá), (b) comando manual de atualização do grafo. | Revogado por #15: (a) passou para o `relay-ai init`, (b) é o `/graphify --update` nativo |
| 5 | Gatilho de `gap-watch`: ao detectar uma lacuna no grafo (ex.: uma consulta via `graphify query`/`graphify explain` não encontra o nó — sinal determinístico, não "achismo" do agente), o agente **pede uma confirmação rápida** ao dev antes de rodar a atualização (ex.: `graphify update .`). Não roda silenciosamente, não se limita a só sinalizar. | Revogado por #12 |
| 6 | Nomes de skills e comandos do projeto são sempre em **inglês**, seguindo a convenção do ecossistema (Graphify, Copilot, mattpocock/skills). Documentação de apoio (como este `SCOPE.md`) pode ficar em português. | Fechado |
| 7 | O manifesto do plugin segue o padrão aberto **Agent Plugins 1.0** (`agent-plugins.org`), não o formato legado do `.claude-plugin/` que o mattpocock usa. Implicações técnicas: `plugin.json` fica na raiz do plugin com `$schema` apontando para a spec v1.0.0/v1.1.0; `name` precisa ser kebab-case (minúsculas, dígitos, hífen, ponto; começa/termina alfanumérico; sem `--` nem `..`); skills ficam fixas em `skills/<nome>/SKILL.md` (sem fallback de `SKILL.md` solto na raiz); tudo específico do Copilot (slash commands, hooks, regras) fica isolado em `com.github.copilot/` dentro do plugin. Instalação continua via marketplace (`copilot plugin marketplace add <owner>/<repo>` + `copilot plugin install <nome>@<owner>`), com `marketplace.json` listando o(s) plugin(s) e `extraKnownMarketplaces`+`autoUpdate: true` para atualização automática — igual ao fluxo do mattpocock. | Revogado por #10 (instalação passou a ser por projeto, copiando arquivos) |
| 8 | **Não reimplementar o que já existe.** As skills de engenharia/produtividade vêm do [mattpocock/skills](https://github.com/mattpocock/skills); o RelayAI só cria o que não existe lá (hoje: descoberta via Graphify). A dependência era garantida por scripts de setup por máquina (`scripts/install.sh` + `install.ps1`) que instalavam os plugins via marketplace. | Princípio mantido; mecanismo substituído por #10 (scripts removidos) |
| 9 | O `README.md` tem uma seção **Credits** obrigatória, com autor, link, uso no RelayAI e licença de cada projeto de terceiros do qual dependemos. Toda nova dependência externa entra nela. | Fechado |
| 10 | **Instalação por projeto via `uvx`.** Comando: `uvx --from git+https://github.com/hugoadriao/relay-ai relay-ai init` (quando publicado no PyPI: `uvx relay-ai init`). Único pré-requisito: **uv** — o mesmo que o Graphify já exige. O RelayAI é uma CLI Python (`src/relay_ai/`, hatchling, Python ≥ 3.12); a pasta `skills/` da raiz entra no pacote. O `init`, rodado na raiz do projeto do dev: (a) garante o Graphify no PATH (`uv tool install graphifyy` + `uv tool update-shell`) — sem isso aborta antes de copiar qualquer coisa (#1); (b) copia as skills do RelayAI para `.github/skills/`; (c) baixa o mattpocock/skills da fonte original (zip da `main`) e copia as skills de `engineering/` e `productivity/` (as 27 listadas no README de lá; `deprecated/`, `in-progress/` e `misc/` ficam de fora) para `.github/skills/`, sem modificar, cada uma com o `LICENSE` MIT original; (d) configura o Graphify no projeto (#11, #12) e constrói o grafo inicial só com código (`graphify update .`, sem LLM). É idempotente: reexecutar atualiza as skills gerenciadas (substitui a pasta inteira de cada uma — edições locais nelas se perdem). Agentes (`.github/agents/`) e comandos (`.github/prompts/`) seguem o mesmo mecanismo quando existirem. Escolhido em vez de `npx skills` (só cobre skills e exigiria Node além do uv) e de scripts `.sh`/`.ps1` (duas implementações em paralelo). | Fechado |
| 11 | O Graphify roda com o **comportamento padrão** dele — o RelayAI não altera nem contorna a ferramenta. Os agentes usam o grafo **sempre** para conhecimento/descoberta, via o `.github/copilot-instructions.md` que o próprio `graphify vscode install` gera no projeto. | Fechado |
| 12 | **Atualização do grafo é do Graphify**, via `graphify hook install` (hooks git post-commit/post-checkout: reextrai só os arquivos de código alterados, sem LLM), ligado pelo `init` quando o projeto é um repositório git. Por isso o `gap-watch` foi **removido**. Lacunas aceitas: código ainda não commitado só entra no grafo no próximo commit; mudanças em docs/imagens exigem `/graphify --update` manual. | Fechado |
| 13 | As skills e agentes copiados para `.github/skills/` e `.github/agents/` ficam **fora do grafo**: o `init` acrescenta essas pastas ao `.graphifyignore` do projeto (mecanismo do próprio Graphify, sintaxe de `.gitignore`) antes de construir o grafo. Só acrescenta a linha se ela não existir e nunca reescreve o que já está no arquivo. Motivo: sem isso, num projeto de teste com um arquivo de código, 359 dos 364 nós vinham das skills e os agentes "descobririam" as skills em vez do código do dev. | Fechado |
| 14 | Os legados da instalação via marketplace (#7) foram **removidos**: `plugin.json`, `marketplace.json` e `com.github.copilot/`. | Fechado |
| 15 | A skill `survey` foi **removida**: o setup inicial é do `relay-ai init` (#10), a atualização automática é dos hooks do Graphify (#12) e o refresh manual é o `/graphify --update` / `graphify update .` nativo — mantê-la seria reimplementar o Graphify (#8, #11). Consequência: o RelayAI fica temporariamente sem conteúdo próprio, só instalando e configurando as dependências, até os itens de "Planejado" existirem. | Fechado |
| 16 | O conteúdo próprio do RelayAI fica **dentro do pacote**, em `src/relay_ai/assets/` (substitui a pasta `skills/` da raiz citada em #10): `assets/skills/<nome>/SKILL.md` → `.github/skills/<nome>/` e `assets/agents/<nome>.agent.md` → `.github/agents/` (pasta e extensão que o VS Code lê para custom agents). Cada tipo é opcional: se a pasta não existir, o `init` só pula. Skills substituem a pasta inteira ao reinstalar; agentes sobrescrevem o arquivo. | Fechado |
| 17 | Primeiro agente próprio: **`langgraph-expert`**, especialista **só em LangGraph** (Python). LangChain entra só como apoio ao que o LangGraph usa, não como escopo próprio. Entra no fluxo do mattpocock/skills na fase de **implementação**: o planejamento (`grill-me` → `to-spec` → `to-tickets`) continua com as skills do Matt, e as partes LangGraph são implementadas pelo especialista, que usa as skills de debug (`diagnosing-bugs` do Matt + as skills de debug Python do RelayAI, quando existirem). Mecanismo de roteamento: ver "Planejado". | Fechado |
| 18 | O `langgraph-expert` consulta a **documentação oficial em tempo real via MCP**: `docs-langchain` (`https://docs.langchain.com/mcp`, guias de LangChain/LangGraph/LangSmith) e `reference-langchain` (`https://reference.langchain.com/mcp`, referência de API), servidores oficiais da LangChain. O `init` os acrescenta ao `.vscode/mcp.json` do projeto (lista em `src/relay_ai/assets/mcp.json`), preservando o que já estiver no arquivo e sem sobrescrever servidores de mesmo nome. | Fechado |
| 19 | **Roteamento ticket → especialista sem modificar o Matt (#8) e sem comando próprio.** As skills do Matt leem o contexto do projeto, então o `init` informa os especialistas por instrução: o `to-tickets` acrescenta `**Specialist:** <agente>` ao corpo de cada ticket cujo núcleo é da especialidade (linha no corpo, não label — funciona em tracker local e no GitHub sem criar labels), e o `/implement`/`/implement-spec` delegam esses tickets ao agente indicado como **subagente**. Instrução é orientação ao modelo, não garantia: o primeiro teste real no VS Code valida se a delegação acontece; só se não for confiável cria-se um comando próprio de despacho. | Fechado |
| 20 | A instrução de #19 fica numa **seção própria do `.github/copilot-instructions.md`** (carregado pelo Copilot em toda conversa), delimitada por marcadores `<!-- relay-ai:start -->`/`<!-- relay-ai:end -->`: o `init` a cria ou substitui só entre os marcadores, sem tocar no resto do arquivo (como a seção do Graphify). A lista de especialistas é gerada do frontmatter (`name`, `description`) dos agentes em `assets/agents/` — nada fixo no código. | Fechado |
| 21 | Conteúdo do `langgraph-expert`: **Graph API (`StateGraph`)**, foco em projetos **FastAPI** e portanto **async de ponta a ponta** (nós `async def`, invocação do grafo sempre `ainvoke`/`astream`, nunca `invoke` síncrono dentro de código async); state em **`TypedDict` + reducers** (`Annotated`). Disciplinas sempre aplicadas: **TDD** via skill `tdd` do Matt; **checkpointer + `interrupt()`** sempre que houver humano no loop; **consultar a doc via MCP** (#18) antes de escrever código que dependa de API do LangGraph. Postura: quando detectar **anti-pattern** ou fuga das boas práticas de LangGraph/LangChain, é **enfático** — diz claramente que é um problema, explica a consequência concreta e mostra a forma correta de implementar a feature. Handoffs: **Revisar** (code-review do Matt no agente padrão), **Diagnosticar bug** (o próprio especialista com `diagnosing-bugs`) e **Especificar antes** (`/grill-me` no agente padrão). Ferramentas: `read`, `search`, `edit`, `execute`, `todos`, `vscode/askQuestions`, `docs-langchain/*`, `reference-langchain/*`. | Fechado (postura detalhada em #22) |
| 22 | **O que é anti-pattern para o `langgraph-expert`** — o agente **julga o código pelo propósito**, não por uma lista fixa. Categorias: (1) **symptomatic fix** sobre fluxo mal desenhado: `if`s, verificações e fallbacks que só existem porque o fluxo não garante seus dados (ex.: o prompt/schema do LLM não produz um campo e alguém adiciona um `if` para improvisar) — corrige-se a **causa** (schema de saída estruturada, campo de state escrito pelo nó responsável, aresta explícita), não o sintoma; (2) **dead/redundant code** (ramos mortos, validação redundante, wrappers que só repassam, lógica duplicada); (3) **over-engineering** (*speculative generality*) com recursos do LangGraph/LangChain — código que funciona, mas com mais peças do que o problema pede, quando algo mais simples resolveria; (4) **LangGraph misuse** (a lista concreta de #21: `invoke` síncrono, compilar por request, state sem reducer etc.). Critérios: Clean Code, DRY, SOLID e práticas da documentação oficial e da comunidade — **a serviço da simplicidade**: nunca criar abstrações em nome desses princípios quando o problema não pede. **Padronização**: segue os padrões que o projeto já usa; se o projeto não tem padrão ou é inconsistente, aponta e propõe um único, aplicado ao código que toca. **Terminologia**: o agente usa termos técnicos formais em inglês (*anti-pattern*, *symptomatic fix*, *dead/redundant code*, *over-engineering* / *speculative generality*), nunca gíria. | Fechado |
| 23 | **O que o `init` instala não aparece no git.** Em repositórios git, o `init` registra no **`.git/info/exclude`** (local, não versionado — nem o próprio arquivo de exclusão aparece no git; preferido ao `.gitignore`, que viraria ele mesmo uma alteração) um bloco entre `# relay-ai:start`/`# relay-ai:end`, reescrito a cada execução: (a) cada agente e cada pasta de skill instalados (RelayAI e Matt — só os nossos, nunca a pasta inteira, para não esconder agentes/skills do dev); (b) os arquivos compartilhados que o próprio `init` criou (`.github/copilot-instructions.md`, `.vscode/mcp.json`, `.graphifyignore`), lembrados entre execuções pelo próprio bloco. Os padrões levam o prefixo da subpasta quando o projeto não é a raiz do repositório. **Arquivos do Graphify** (`graphify-out/`, `.gitattributes`) **continuam visíveis**, seguindo o padrão dele (#11) de versionar o grafo. **Arquivos que já eram versionados** e foram alterados pelo `init` não podem ser escondidos: o `init` altera e **avisa** ao final, cabendo ao dev decidir se commita. Fora de repositório git, esse passo é pulado. | Fechado |
| 24 | **Caminhos longos no Windows são detectados antes de instalar.** Com `LongPathsEnabled` desligado (registro `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem`), o Graphify falha ao gravar o cache se o caminho passa de 260 caracteres — e o arquivo de cache mais longo fica ~128 caracteres abaixo da pasta do projeto (medido num caso real: projeto com 136 caracteres → 264). O `init` verifica **primeiro**, antes de qualquer instalação ou cópia: se `len(caminho do projeto) + 130 ≥ 260`, aborta explicando o problema e as duas soluções — (1) ligar os caminhos longos (comando PowerShell de administrador, abrir novo terminal) ou (2) mover/clonar o projeto para um caminho mais curto. Só no Windows e só com os caminhos longos desligados; nunca altera a configuração do sistema por conta própria. | Fechado |

## Layout atual do repositório

```
relay-ai/
├── pyproject.toml           # pacote Python da CLI (hatchling) — ver #10
├── src/relay_ai/            # CLI `relay-ai init`
│   └── assets/              # conteúdo próprio (#16)
│       ├── agents/langgraph-expert.agent.md   # #17, #21
│       ├── skills/<nome>/SKILL.md   # ainda não existe
│       └── mcp.json                 # servidores MCP dos agentes (#18)
├── README.md
├── SCOPE.md
└── CLAUDE.md                # carregado automaticamente pelo Claude Code; importa este arquivo
```

O que o `init` gera no projeto do dev:

```
<projeto>/
├── .github/
│   ├── agents/<agente>.agent.md     # agentes do RelayAI (#16)
│   ├── skills/<skill>/SKILL.md      # RelayAI + mattpocock/skills (com LICENSE)
│   └── copilot-instructions.md      # seção do Graphify (#11) + seção relay-ai (#20)
├── .vscode/mcp.json                 # servidores MCP dos agentes (#18)
├── .graphifyignore                  # com `.github/agents/` e `.github/skills/` (#13)
└── graphify-out/                    # grafo gerado pelo Graphify
```

**Nota:** `CLAUDE.md` existe para orientar o *desenvolvimento* deste projeto no Claude
Code — não é um artefato que o RelayAI entrega para quem instala no Copilot. Não confundir
com a decisão de "fora de escopo: suporte a agentes além do GitHub Copilot", que é sobre o
produto final, não sobre a ferramenta usada para construí-lo.

## Planejado (anunciado, ainda não grillado)

- **Agente especialista em FastAPI** (`.agent.md`).
- **`langgraph-expert`** (#17–#21) — escrito; falta validar no VS Code (abaixo).
- **Skills de debug Python.**

Pontos a grillar antes de escrever:

- Validar no VS Code o `langgraph-expert`: (a) o `/to-tickets` marca `**Specialist:**` e
  o `/implement`/`/implement-spec` delegam ao especialista (#19); (b) os handoffs
  funcionam, inclusive `/grill-me` como `prompt`; (c) os servidores MCP sobem e o agente
  os consulta; (d) ferramentas e skills (`tdd`, `diagnosing-bugs`) disponíveis nele.
- Nomes (em inglês, #6), escopo de cada agente e quais `tools`/`handoffs` o frontmatter
  declara.
- Se as skills de debug são user-invoked ou model-invoked.
- Sobreposição com o mattpocock/skills (#8): ele já instala `diagnosing-bugs`
  (model-invoked, debug genérico) e `tdd`. As skills de debug Python devem complementar
  essas (o que é específico de Python), não duplicar.
- Se os agentes usam explicitamente o grafo do Graphify ou se basta o
  `copilot-instructions.md` (#11).

## Em aberto (próximos pontos a grillar)

- Se existirá uma skill própria de "grilling" ou se o `grill-me`/`grilling` do
  mattpocock/skills (instalado pelo `init`) cobre isso.
- Fixar o mattpocock/skills num `sha` (estabilidade) ou seguir a `main` (como está hoje).
- Publicar no PyPI (para `uvx relay-ai init`) e quando.
- Adicionar um arquivo `LICENSE` ao repositório (o pacote declara MIT, mas o arquivo não
  existe).
- Onde fica `docs/`, se precisar existir.

## Fora de escopo (por enquanto)

- Suporte a agentes além do GitHub Copilot.
- Qualquer coisa que dependa do Graphify Cloud (o projeto usa só o Graphify local/CLI).
