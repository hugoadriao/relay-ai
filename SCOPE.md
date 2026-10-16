# SCOPE.md

## Projeto

- **Nome**: RelayAI
- **Repositório**: [github.com/hugoadriao/relay-ai](https://github.com/hugoadriao/relay-ai.git)
- **Pacote / comando de instalação**: `relay-ai` (`uvx ... relay-ai init`, ver #10)

## Objetivo do projeto

Funcionar de maneira semelhante ao [mattpocock/skills](https://github.com/mattpocock/skills):
instalação fácil + skills que determinam o escopo de uma atividade e questionam o
desenvolvedor sobre como ela deve ser construída, antes de qualquer código ser escrito.

**Foco**: GitHub Copilot no VS Code e OpenCode (#30). O dev instala o RelayAI **dentro de um projeto
dele**: os `.md` de skills, agentes e comandos são copiados para os caminhos que o VS Code
lê, e todas as dependências (Graphify, skills do mattpocock) ficam instaladas e prontas no
mesmo passo. Suporte a outras ferramentas (Claude Code, Codex, Cursor, etc.) fica para depois.

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
| 10 | **Instalação por projeto via `uvx`.** Comando: `uvx --from git+https://github.com/hugoadriao/relay-ai relay-ai init` (quando publicado no PyPI: `uvx relay-ai init`). Único pré-requisito: **uv** — o mesmo que o Graphify já exige. O RelayAI é uma CLI Python (`src/relay_ai/`, hatchling, Python ≥ 3.12); a pasta `skills/` da raiz entra no pacote. O `init`, rodado na raiz do projeto do dev: (a) garante o Graphify no PATH (`uv tool install graphifyy` + `uv tool update-shell`) — sem isso aborta antes de copiar qualquer coisa (#1); (b) copia as skills do RelayAI para `.github/skills/`; (c) baixa o mattpocock/skills da fonte original (zip da `main`) e copia as skills de `engineering/` e `productivity/` (as 27 listadas no README de lá; `deprecated/`, `in-progress/` e `misc/` ficam de fora) para `.github/skills/`, sem modificar, cada uma com o `LICENSE` MIT original; (d) configura o Graphify no projeto (#11, #12) e constrói o grafo inicial só com código (`graphify update .`, sem LLM). É idempotente: reexecutar atualiza as skills gerenciadas (substitui a pasta inteira de cada uma — edições locais nelas se perdem). Agentes (`.github/agents/`) e comandos (`.github/prompts/`) seguem o mesmo mecanismo quando existirem. Escolhido em vez de `npx skills` (só cobre skills e exigiria Node além do uv) e de scripts `.sh`/`.ps1` (duas implementações em paralelo). | Fechado — skills agora em `.agents/skills/` (#30) e Node 22+ também é pré-requisito (#31) |
| 11 | O Graphify roda com o **comportamento padrão** dele — o RelayAI não altera nem contorna a ferramenta. Os agentes usam o grafo **sempre** para conhecimento/descoberta, via o `.github/copilot-instructions.md` que o próprio `graphify vscode install` gera no projeto. | Fechado |
| 12 | **Atualização do grafo é do Graphify**, via `graphify hook install` (hooks git post-commit/post-checkout: reextrai só os arquivos de código alterados, sem LLM), ligado pelo `init` quando o projeto é um repositório git. Por isso o `gap-watch` foi **removido**. Lacunas aceitas: código ainda não commitado só entra no grafo no próximo commit; mudanças em docs/imagens exigem `/graphify --update` manual. | Fechado |
| 13 | As skills e agentes copiados para `.github/skills/` e `.github/agents/` ficam **fora do grafo**: o `init` acrescenta essas pastas ao `.graphifyignore` do projeto (mecanismo do próprio Graphify, sintaxe de `.gitignore`) antes de construir o grafo. Só acrescenta a linha se ela não existir e nunca reescreve o que já está no arquivo. Motivo: sem isso, num projeto de teste com um arquivo de código, 359 dos 364 nós vinham das skills e os agentes "descobririam" as skills em vez do código do dev. | Fechado — pastas agora: `.agents/skills/` e a pasta de agentes de cada plataforma (#30) |
| 14 | Os legados da instalação via marketplace (#7) foram **removidos**: `plugin.json`, `marketplace.json` e `com.github.copilot/`. | Fechado |
| 15 | A skill `survey` foi **removida**: o setup inicial é do `relay-ai init` (#10), a atualização automática é dos hooks do Graphify (#12) e o refresh manual é o `/graphify --update` / `graphify update .` nativo — mantê-la seria reimplementar o Graphify (#8, #11). Consequência: o RelayAI fica temporariamente sem conteúdo próprio, só instalando e configurando as dependências, até os itens de "Planejado" existirem. | Fechado |
| 16 | O conteúdo próprio do RelayAI fica **dentro do pacote**, em `src/relay_ai/assets/` (substitui a pasta `skills/` da raiz citada em #10): `assets/skills/<nome>/SKILL.md` → `.github/skills/<nome>/` e `assets/agents/<nome>.agent.md` → `.github/agents/` (pasta e extensão que o VS Code lê para custom agents). Cada tipo é opcional: se a pasta não existir, o `init` só pula. Skills substituem a pasta inteira ao reinstalar; agentes sobrescrevem o arquivo. | Revisto por #30: skills vão para `.agents/skills/`; agentes têm fonte única `assets/agents/<nome>.md` renderizada por plataforma |
| 17 | Primeiro agente próprio: **`langgraph-expert`**, especialista **só em LangGraph** (Python). LangChain entra só como apoio ao que o LangGraph usa, não como escopo próprio. Entra no fluxo do mattpocock/skills na fase de **implementação**: o planejamento (`grill-me` → `to-spec` → `to-tickets`) continua com as skills do Matt, e as partes LangGraph são implementadas pelo especialista, que usa as skills de debug (`diagnosing-bugs` do Matt + as skills de debug Python do RelayAI, quando existirem). Mecanismo de roteamento: ver "Planejado". | Fechado |
| 18 | O `langgraph-expert` consulta a **documentação oficial em tempo real via MCP**: `docs-langchain` (`https://docs.langchain.com/mcp`, guias de LangChain/LangGraph/LangSmith) e `reference-langchain` (`https://reference.langchain.com/mcp`, referência de API), servidores oficiais da LangChain. O `init` os acrescenta ao `.vscode/mcp.json` do projeto (lista em `src/relay_ai/assets/mcp.json`), preservando o que já estiver no arquivo e sem sobrescrever servidores de mesmo nome. | Fechado |
| 19 | **Roteamento ticket → especialista sem modificar o Matt (#8) e sem comando próprio.** As skills do Matt leem o contexto do projeto, então o `init` informa os especialistas por instrução: o `to-tickets` acrescenta `**Specialist:** <agente>` ao corpo de cada ticket cujo núcleo é da especialidade (linha no corpo, não label — funciona em tracker local e no GitHub sem criar labels), e o `/implement`/`/implement-spec` delegam esses tickets ao agente indicado como **subagente**. Instrução é orientação ao modelo, não garantia: o primeiro teste real no VS Code valida se a delegação acontece; só se não for confiável cria-se um comando próprio de despacho. | Fechado |
| 20 | A instrução de #19 fica numa **seção própria do `.github/copilot-instructions.md`** (carregado pelo Copilot em toda conversa), delimitada por marcadores `<!-- relay-ai:start -->`/`<!-- relay-ai:end -->`: o `init` a cria ou substitui só entre os marcadores, sem tocar no resto do arquivo (como a seção do Graphify). A lista de especialistas é gerada do frontmatter (`name`, `description`) dos agentes em `assets/agents/` — nada fixo no código. | Fechado — no OpenCode a mesma seção vai para o `AGENTS.md` (#30) |
| 21 | Conteúdo do `langgraph-expert`: **Graph API (`StateGraph`)**, foco em projetos **FastAPI** e portanto **async de ponta a ponta** (nós `async def`, invocação do grafo sempre `ainvoke`/`astream`, nunca `invoke` síncrono dentro de código async); state em **`TypedDict` + reducers** (`Annotated`). Disciplinas sempre aplicadas: **TDD** via skill `tdd` do Matt; **checkpointer + `interrupt()`** sempre que houver humano no loop; **consultar a doc via MCP** (#18) antes de escrever código que dependa de API do LangGraph. Postura: quando detectar **anti-pattern** ou fuga das boas práticas de LangGraph/LangChain, é **enfático** — diz claramente que é um problema, explica a consequência concreta e mostra a forma correta de implementar a feature. Handoffs: **Revisar** (code-review do Matt no agente padrão), **Diagnosticar bug** (o próprio especialista com `diagnosing-bugs`) e **Especificar antes** (`/grill-me` no agente padrão). Ferramentas: `read`, `search`, `edit`, `execute`, `todos`, `vscode/askQuestions`, `docs-langchain/*`, `reference-langchain/*`. | Fechado (postura detalhada em #22) |
| 22 | **O que é anti-pattern para o `langgraph-expert`** — o agente **julga o código pelo propósito**, não por uma lista fixa. Categorias: (1) **symptomatic fix** sobre fluxo mal desenhado: `if`s, verificações e fallbacks que só existem porque o fluxo não garante seus dados (ex.: o prompt/schema do LLM não produz um campo e alguém adiciona um `if` para improvisar) — corrige-se a **causa** (schema de saída estruturada, campo de state escrito pelo nó responsável, aresta explícita), não o sintoma; (2) **dead/redundant code** (ramos mortos, validação redundante, wrappers que só repassam, lógica duplicada); (3) **over-engineering** (*speculative generality*) com recursos do LangGraph/LangChain — código que funciona, mas com mais peças do que o problema pede, quando algo mais simples resolveria; (4) **LangGraph misuse** (a lista concreta de #21: `invoke` síncrono, compilar por request, state sem reducer etc.). Critérios: Clean Code, DRY, SOLID e práticas da documentação oficial e da comunidade — **a serviço da simplicidade**: nunca criar abstrações em nome desses princípios quando o problema não pede. **Padronização**: segue os padrões que o projeto já usa; se o projeto não tem padrão ou é inconsistente, aponta e propõe um único, aplicado ao código que toca. **Terminologia**: o agente usa termos técnicos formais em inglês (*anti-pattern*, *symptomatic fix*, *dead/redundant code*, *over-engineering* / *speculative generality*), nunca gíria. | Fechado |
| 23 | **O que o `init` instala não aparece no git.** Em repositórios git, o `init` registra no **`.git/info/exclude`** (local, não versionado — nem o próprio arquivo de exclusão aparece no git; preferido ao `.gitignore`, que viraria ele mesmo uma alteração) um bloco entre `# relay-ai:start`/`# relay-ai:end`, reescrito a cada execução: (a) cada agente e cada pasta de skill instalados (RelayAI e Matt — só os nossos, nunca a pasta inteira, para não esconder agentes/skills do dev); (b) os arquivos compartilhados que o próprio `init` criou (`.github/copilot-instructions.md`, `.vscode/mcp.json`, `.graphifyignore`), lembrados entre execuções pelo próprio bloco. Os padrões levam o prefixo da subpasta quando o projeto não é a raiz do repositório. **Arquivos do Graphify** (`graphify-out/`, `.gitattributes`) **continuam visíveis**, seguindo o padrão dele (#11) de versionar o grafo. **Arquivos que já eram versionados** e foram alterados pelo `init` não podem ser escondidos: o `init` altera e **avisa** ao final, cabendo ao dev decidir se commita. Fora de repositório git, esse passo é pulado. | Fechado |
| 24 | **Caminhos longos no Windows são detectados antes de instalar.** Com `LongPathsEnabled` desligado (registro `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem`), o Graphify falha ao gravar o cache se o caminho passa de 260 caracteres — e o arquivo de cache mais longo fica ~128 caracteres abaixo da pasta do projeto (medido num caso real: projeto com 136 caracteres → 264). O `init` verifica **primeiro**, antes de qualquer instalação ou cópia: se `len(caminho do projeto) + 130 ≥ 260`, aborta explicando o problema e as duas soluções — (1) ligar os caminhos longos (comando PowerShell de administrador, abrir novo terminal) ou (2) mover/clonar o projeto para um caminho mais curto. Só no Windows e só com os caminhos longos desligados; nunca altera a configuração do sistema por conta própria. | Fechado |
| 25 | **Sem skill de grilling própria.** O `grill-me`/`grilling` do mattpocock/skills, instalado pelo `init`, cobre o papel (#8). | Fechado |
| 26 | O mattpocock/skills é instalado da **`main`**, sem fixar `sha`: a `main` é a branch que contém o que já foi revisado e validado lá, e cada `init` traz a versão mais recente. | Fechado |
| 27 | Debugger via extensão do VS Code (DebugMCP). | Revogado por #31; código e instruções removidos (o RelayAI ainda não tinha usuários) |
| 28 | Skill **`debugging-python`**: caixa de ferramentas Python que **complementa** o `diagnosing-bugs` do Matt (que dá o processo), sem processo próprio. Regra central: **observar, não inferir** — uma hipótese só é confirmada vendo o valor real (tipo, forma, conteúdo) no ponto da falha. **Economia de tokens**: nunca despejar objetos grandes (listas de mensagens, trocas entre agentes/tools); forma antes de valor; projeções (`len`, chaves, tipo, fatias); breakpoints condicionais e logpoints; saída de comandos curta. Debugger via mcp-debugger (#31); sem ele, prints temporários **de projeções** com prefixo `[DEBUG-xxxx]`; o agente **nunca** roda `pdb`/`breakpoint()` (travaria esperando teclado) — só sugere ao dev. Corrige a causa, nunca o sintoma (mesmo princípio de #22): proíbe `try/except` que engole, `if x is None` em dado que deveria existir, `sleep`/retry para corrida, fixar versão sem entender. Ferramentas: stdlib primeiro; terceiros (`py-spy`, `pyinstrument`) só via `uvx`, sem entrar nas dependências do projeto sem perguntar. Estrutura: `SKILL.md` enxuto + referências lidas sob demanda (`debugger.md`, `langgraph.md`, `asyncio.md`, `performance.md`, `environment.md`). Nome e invocação: `debugging-python`, **model-invoked** (provisórios, a confirmar após o teste real). O `langgraph-expert` usa a skill na seção de debug. | Fechado — debugger trocado para mcp-debugger (#31) |
| 29 | **Comandos `update` e `uninstall`** além do `init`, para o ciclo de vida ficar explícito. **Manifesto** `.github/relay-ai.json` (escondido do git por #23) registra exatamente o que o RelayAI instalou ou acrescentou: agentes, skills, servidores MCP e extensões que **ele** adicionou (não os que já existiam), linhas do `.graphifyignore` e arquivos que **ele** criou. Instalações antigas sem manifesto são reconhecidas pelo bloco do `.git/info/exclude`. **Propriedade**: `init`/`update` só substituem agentes e skills que o próprio RelayAI instalou — se o dev tem um com o mesmo nome, o dele é preservado e o `init` avisa (antes, era sobrescrito em silêncio). **`update`**: exige instalação prévia; reinstala, **remove** agentes/skills que deixaram de fazer parte do RelayAI e mostra um resumo (atualizados/adicionados/removidos); **não** atualiza o Graphify (é global, outros projetos usam) — só mostra `uv tool upgrade graphifyy`. **`uninstall`**: lista o que vai remover e pede confirmação (`--yes` pula); remove só o que está no manifesto — a seção `relay-ai` do `copilot-instructions.md`, as entradas acrescentadas nos JSON e no `.graphifyignore`, os arquivos criados se ficarem vazios, pastas vazias, o manifesto e o bloco do exclude; conteúdo do dev fica intacto. O **Graphify** é mantido por padrão (o grafo pode ser do time); `--graphify` remove o setup dele no projeto com os comandos dele (`graphify hook uninstall`, `graphify vscode uninstall` seguido de `graphify copilot install`, porque o `vscode uninstall` também apaga a skill global que outros projetos usam) e funciona mesmo depois do RelayAI já removido; `graphify-out/` e o Graphify da máquina nunca são apagados. Ao editar arquivos do dev, o RelayAI **preserva a quebra de linha original** (LF/CRLF), para não gerar diferenças falsas no git. Versão do pacote: `0.2.0`. | Fechado |
| 30 | **Plataformas: GitHub Copilot (VS Code) e OpenCode** — reabre o "fora de escopo" anterior (só Copilot), motivado por restrições do VS Code em ambiente de cliente. Princípio: **padrão aberto onde ele existe, adaptador por plataforma onde não existe**. Padrões: **[Agent Skills](https://agentskills.io)** (formato `SKILL.md`), com as skills instaladas uma vez só em **`.agents/skills/`** (lido por VS Code, OpenCode e outros), e **[AGENTS.md](https://agents.md)** (instruções). Sem padrão, adaptados por plataforma: **agentes** (fonte única `assets/agents/<nome>.md` com frontmatter comum `name`/`description` + blocos `copilot:`/`opencode:`, renderizada em `.github/agents/<nome>.agent.md` ou `.opencode/agents/<nome>.md`; o pacote ganha a dependência `pyyaml`), **configuração de MCP** (formato neutro em `assets/mcp.json`, traduzido para `.vscode/mcp.json` `servers` stdio/http ou `opencode.json` `mcp` local/remote) e **integração do Graphify** (`graphify vscode install` ou `graphify opencode install`; `opencode uninstall` não toca em nada global). Roteamento (#19/#20): seção `relay-ai` no `copilot-instructions.md` (Copilot) e no `AGENTS.md` (OpenCode, onde subagentes também são chamados pela `description` ou por `@nome`). O `init` **pergunta** a plataforma (Copilot, OpenCode ou ambos) ou aceita `--platform copilot`/`opencode`/`both`; fora de terminal interativo, exige a flag. O manifesto guarda as plataformas; `update`/`uninstall` seguem ele; rodar `init` com outra plataforma troca, removendo o que era da plataforma abandonada. Migração: o `update` move as skills de `.github/skills/` para `.agents/skills/`, converte manifestos antigos e apaga arquivos de configuração que criou e ficaram vazios. Versão `0.3.0`. | Fechado |
| 31 | **Debugger: [mcp-debugger](https://github.com/debugmcp/mcp-debugger)** (MIT), no lugar da decisão #27: roda **sem IDE**, então serve às duas plataformas, e não depende de extensão do VS Code. Configurado como servidor **stdio** via `npx -y @debugmcp/mcp-debugger@0.25.1 stdio`, com **versão fixada** (atualização só depois de revisão). **Auditoria da 0.25.1** (pacote do npm inspecionado sem executar): sem telemetria (a palavra só aparece como categoria DAP que ele filtra); sem conexões de saída (rede só para `127.0.0.1` e o debugpy local; o transporte HTTP do winston vem empacotado mas não é usado, os logs vão só para console e arquivo); em stdio nem abre porta; o único tráfego é o `npx` baixar o pacote. Python: o `debugpy` **não** entra nas dependências do projeto — o alvo roda com `uv run --with debugpy python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m pytest ...` (modo attach), o que também cobre rodar um teste pytest. **Node.js 22+ é pré-requisito obrigatório**: o `init` **aborta** sem ele (como sem o uv), com comandos de instalação por sistema; o README tem um guia de instalação junto dos pré-requisitos. | Fechado |
| 32 | **`AGENTS.md` garantido para o setup do Matt.** Se o projeto não tem `AGENTS.md` nem `CLAUDE.md`, o `init` cria um `AGENTS.md` vazio: o `/setup-matt-pocock-skills` edita o arquivo que existe em vez de perguntar, e grava a configuração onde Copilot e OpenCode leem (o Copilot só lê `CLAUDE.md` com `chat.useClaudeMdFile` ligado). Não é preciso skill/agente de setup próprio: as outras perguntas do setup do Matt (tracker, labels, docs) são decisões genuínas do projeto. O `AGENTS.md` criado fica **escondido do git** como os demais arquivos que o `init` cria (#23); o `uninstall` só o apaga se ficar vazio. | Fechado |
| 33 | Depois do `init`/`update`, o dev é orientado a **recarregar o editor** (VS Code: **Developer: Reload Window**; OpenCode: reiniciar) — no teste real, a recomendação de extensão e os agentes só apareceram depois do reload. Está na mensagem final do comando e no README. | Fechado |

## Layout atual do repositório

```
relay-ai/
├── pyproject.toml           # pacote Python da CLI (hatchling) — ver #10
├── src/relay_ai/            # CLI `relay-ai init`
│   └── assets/              # conteúdo próprio (#16)
│       ├── agents/langgraph-expert.md   # fonte única, renderizada por plataforma (#30)
│       ├── skills/debugging-python/     # #28 (SKILL.md + referências)
│       └── mcp.json                     # servidores MCP, formato neutro (#18, #31)
├── README.md
├── SCOPE.md
└── CLAUDE.md                # carregado automaticamente pelo Claude Code; importa este arquivo
```

O que o `init` gera no projeto do dev:

```
<projeto>/
├── .agents/skills/<skill>/SKILL.md  # RelayAI + mattpocock/skills, todas as plataformas (#30)
├── AGENTS.md                        # criado se não houver (#32); seção relay-ai no OpenCode
├── .github/
│   ├── agents/<agente>.agent.md     # Copilot (#30)
│   ├── copilot-instructions.md      # Copilot: seção do Graphify + seção relay-ai (#20)
│   └── relay-ai.json                # manifesto (#29)
├── .vscode/mcp.json                 # Copilot: servidores MCP (#18, #31)
├── .opencode/agents/<agente>.md     # OpenCode (#30)
├── opencode.json                    # OpenCode: servidores MCP (#30, #31)
├── .graphifyignore                  # pastas de agentes e skills (#13)
└── graphify-out/                    # grafo gerado pelo Graphify
```

**Nota:** `CLAUDE.md` existe para orientar o *desenvolvimento* deste projeto no Claude
Code — não é um artefato que o RelayAI entrega para quem instala no Copilot. Não confundir
com a decisão de "fora de escopo: suporte a agentes além do GitHub Copilot", que é sobre o
produto final, não sobre a ferramenta usada para construí-lo.

## Planejado (anunciado, ainda não grillado)

- **Agente especialista em FastAPI** (`.agent.md`).
- **`langgraph-expert`** (#17–#21) — escrito; falta validar no VS Code (abaixo).
- **`debugging-python`** (#27, #28) — escrita; falta validar num projeto real.

Pontos a grillar antes de escrever:

- Validar no VS Code o `langgraph-expert`: (a) o `/to-tickets` marca `**Specialist:**` e
  o `/implement`/`/implement-spec` delegam ao especialista (#19); (b) os handoffs
  funcionam, inclusive `/grill-me` como `prompt`; (c) os servidores MCP sobem e o agente
  os consulta; (d) ferramentas e skills (`tdd`, `diagnosing-bugs`) disponíveis nele. No
  primeiro teste (Copilot em ambiente de cliente) só o uso do grafo pôde ser validado: os
  MCP foram bloqueados e o agente caiu para a doc oficial direto. Repetir no OpenCode.
- Validar a `debugging-python` num projeto real: (a) a skill é carregada sozinha ao depurar
  (model-invoked); (b) o fluxo attach do mcp-debugger com `uv run --with debugpy` funciona
  nas duas plataformas (inclusive `npx` como comando stdio no Windows); (c) o agente prefere
  projeções a despejar valores. Depois do teste, confirmar nome e invocação (#28).
- Validar no OpenCode: o agente como subagente e via `@langgraph-expert`, as skills em
  `.agents/skills/`, o `opencode.json` aceito e a integração do Graphify.
- Nomes (em inglês, #6), escopo de cada agente e quais `tools`/`handoffs` o frontmatter
  declara.
- Se os agentes usam explicitamente o grafo do Graphify ou se basta o
  `copilot-instructions.md` (#11).

## Em aberto (próximos pontos a grillar)

- Publicar no PyPI (para `uvx relay-ai init`) e quando.
- Adicionar um arquivo `LICENSE` ao repositório (o pacote declara MIT, mas o arquivo não
  existe).
- Onde fica `docs/`, se precisar existir.

## Fora de escopo (por enquanto)

- Suporte a ferramentas além do GitHub Copilot e do OpenCode (#30).
- Qualquer coisa que dependa do Graphify Cloud (o projeto usa só o Graphify local/CLI).
