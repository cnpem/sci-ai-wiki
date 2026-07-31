# Wiki Research Chat

Chat local e somente leitura para consultar uma wiki com Antigravity,
OpenCode + Ollama ou Codex. A interface não mostra terminal e não escreve na
wiki.

## Testar a branch `dev`

O caminho recomendado é `uv`:

```bash
git clone --branch dev https://github.com/cnpem/sci-ai-wiki.git
cd sci-ai-wiki/wiki-agent-ui
uv sync --frozen
cp .env.example .env
```

Edite `WIKI_PATH` no `.env` e execute:

```bash
uv run python app.py
```

Acesse <http://127.0.0.1:8000>. Se escolher Antigravity, o próprio site guia
o login oficial. Para confirmar a instalação, rode `uv run pytest -q`.

Poetry também é recomendado e `pip` continua disponível como fallback. Os
comandos equivalentes estão na seção de instalação.

## Fase 1 — instalar

Requisitos básicos: Python 3.11 ou mais recente, um gerenciador de dependências
e pelo menos um dos motores:

- Antigravity CLI instalado; o login pode ser feito pelo site; ou
- OpenCode e Ollama instalados, com o modelo configurado já disponível; ou
- Codex CLI instalado e autenticado com `codex login`.

Use preferencialmente:

1. **uv** — opção mais direta e rápida; cria o `.venv` e pode instalar um
   Python compatível automaticamente.
2. **Poetry 2.x** — recomendado para quem já usa o fluxo Poetry e seu
   lockfile.
3. **pip** — fallback universal, mantido para ambientes tradicionais.

`pyproject.toml` é a fonte principal das dependências. `uv.lock` e
`poetry.lock` garantem instalações reproduzíveis em seus respectivos fluxos;
`requirements.txt` mantém a compatibilidade com `pip`.

### Instalar uv

macOS ou Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

No macOS, também é possível usar Homebrew:

```bash
brew install uv
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

Consulte a [instalação oficial do uv](https://docs.astral.sh/uv/getting-started/installation/).

### Instalar Poetry

macOS, Linux ou Windows com WSL:

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry --version
```

Windows PowerShell:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
poetry --version
```

Outra opção multiplataforma é `pipx install poetry`. Consulte a
[instalação oficial do Poetry](https://python-poetry.org/docs/#installation).

### Instalar Antigravity CLI

macOS ou Linux:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
agy --version
```

Windows PowerShell:

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
agy --version
```

O instalador oficial coloca o executável em `~/.local/bin/agy` no macOS/Linux
e na pasta local do usuário no Windows. Se `agy` ainda não for encontrado,
feche e reabra o terminal. Consulte a [instalação oficial do Antigravity
CLI](https://antigravity.google/docs/cli-install).

Não é preciso executar um comando de login separado: no primeiro `agy`, o
Antigravity abre o navegador e pede a conta Google. Neste projeto, o botão
**Conectar com Google** inicia exatamente esse fluxo.

### Instalar e autenticar Codex CLI

Instalador recomendado no macOS ou Linux:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex --version
```

Alternativa com Node.js/npm, inclusive no Windows:

```bash
npm install -g @openai/codex
codex --version
```

Para usar a assinatura/conta ChatGPT do próprio usuário:

```bash
codex login
codex login status
```

`codex login` abre o navegador. Escolha **Sign in with ChatGPT**, conclua o
login e volte ao terminal. Para sair, use `codex logout`. Veja o
[quickstart oficial do Codex CLI](https://developers.openai.com/codex/cli/) e
as [opções oficiais de autenticação](https://developers.openai.com/codex/auth/).

Também é possível usar uma chave da OpenAI Platform, com cobrança separada da
assinatura ChatGPT:

```bash
export OPENAI_API_KEY="sua-chave"
printenv OPENAI_API_KEY | codex login --with-api-key
```

No Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "sua-chave"
$env:OPENAI_API_KEY | codex login --with-api-key
```

Não coloque a chave no `.env` deste projeto e não a compartilhe. O app usa a
sessão que o Codex CLI salvou localmente.

### Instalar as dependências

Escolha apenas um dos fluxos abaixo.

#### Opção recomendada: uv

```bash
uv sync --frozen
cp .env.example .env
```

No Windows PowerShell, substitua o último comando por:

```powershell
Copy-Item .env.example .env
```

Não é necessário ativar o ambiente virtual. `uv run` executa cada comando no
ambiente correto e verifica se ele continua sincronizado com o lockfile.

#### Opção recomendada: Poetry

```bash
poetry install
cp .env.example .env
```

No Windows PowerShell, use `Copy-Item .env.example .env`. Execute o app e os
testes com `poetry run`.

#### Fallback: pip

macOS ou Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite `.env`:

```dotenv
WIKI_PATH=/caminho/para/a/pasta/graph
AGY_BIN=agy
AGY_TIMEOUT_SECONDS=300
OPENCODE_BIN=opencode
OPENCODE_MODEL=ollama/gemma4:31b
OPENCODE_TIMEOUT_SECONDS=600
CODEX_BIN=codex
CODEX_MODEL=
CODEX_TIMEOUT_SECONDS=600
```

`CODEX_MODEL` vazio usa o modelo padrão disponível para a conta do usuário.

Critério de sucesso: `WIKI_PATH` contém `GEMINI.md`, `.agents/skills/` e
`wiki/`; `GET /api/health` informa `"ready": true`.

## Fase 2 — executar

Com `uv`:

```bash
uv run python app.py
```

Com Poetry:

```bash
poetry run python app.py
```

Com o ambiente `pip` ativado:

```bash
python app.py
```

Abra <http://127.0.0.1:8000>.

### Primeiro acesso com Antigravity

1. Selecione **Antigravity** e clique em **Conectar**.
2. Clique em **Conectar com Google**. O site abre o `agy` oficial uma única vez
   no terminal do sistema; o próprio `agy` abre o login do Google no navegador.
3. Escolha a conta, conclua as telas oficiais do Antigravity e volte ao site.
4. Clique em **Já concluí o login**.

O site acrescenta apenas a pasta definida em `WIKI_PATH` às pastas confiáveis e
a permissão `read_file(WIKI_PATH)` às configurações do Antigravity. As demais
configurações são preservadas. Se o sistema não permitir abrir o terminal, o
modal mostra um único comando com botão **Copiar**.

O OAuth é inteiramente controlado pelo `agy`: a sessão fica no gerenciador de
credenciais do sistema e o site nunca recebe senha, cookie ou token. O fluxo
segue a [autenticação oficial do Antigravity
CLI](https://antigravity.google/docs/cli/install).

Critério de sucesso: a página mostra o total de páginas, o status
`páginas · Antigravity` e aceita uma pergunta.

## Fase 3 — verificar

Com `uv`:

```bash
uv run pytest -q
```

Com Poetry, use `poetry run pytest -q`. Com o ambiente `pip` ativado, use
`pytest -q`.

Os testes cobrem indexação local, bloqueio de caminhos, onboarding do
Antigravity, preservação das configurações, anexos PDF e conversas simuladas.
Eles não abrem o terminal e não gastam cota do Antigravity.

## Como funciona

1. O FastAPI executa `agy --print` dentro de `WIKI_PATH`.
2. Alternativamente, executa `opencode run` com `ollama/gemma4:31b`.
3. Com Codex, executa `codex exec --ephemeral --sandbox read-only --json`.
4. Os motores leem `GEMINI.md` e a skill `llm-wiki-query`.
5. As sessões usam agentes de planejamento e permissões somente leitura. No
   OpenCode, edição, terminal, web e subagentes são negados em runtime. No
   Codex, a configuração pessoal é ignorada e a execução é efêmera, sem
   persistir a conversa da CLI.
6. Eventos reais do processo viram etapas de atividade na conversa.
7. A resposta é renderizada como Markdown e LaTeX (`$...$`, `$$...$$`,
   `\(...\)` e `\[...\]`) com uma cópia local do KaTeX.
8. Links `[[page_id]]` e chips abrem a página correspondente em um viewer
   Markdown lateral, que pode ser redimensionado arrastando o divisor.
9. Durante a consulta, o campo continua editável para preparar a próxima
   pergunta; apenas o envio permanece bloqueado até a resposta terminar.
10. O botão `+` anexa até 5 PDFs à conversa. O servidor extrai o texto
   localmente, seleciona somente os trechos relevantes para a pergunta e os
   entrega ao motor escolhido. As respostas citam páginas como
   `[PDF: arquivo.pdf, p. 12]`.

## PDFs temporários

- Limite de 20 MB e 150 páginas por PDF.
- O conteúdo extraído fica apenas na memória do servidor; não é copiado para a
  wiki nem salvo como página.
- Os anexos são removidos ao clicar no `×`, ao iniciar uma nova conversa ou
  após 2 horas sem uso.
- PDFs escaneados sem camada de texto exigem OCR antes do upload.
- Os mesmos anexos funcionam com Antigravity, OpenCode + Ollama e Codex.

O navegador nunca recebe credenciais do Antigravity. A permissão concedida ao
`agy` é somente `read_file` para a raiz configurada.

## Usar outra wiki

Altere somente `WIKI_PATH` no `.env`. O caminho deve apontar para a raiz que
contém:

```text
minha-wiki/
├── GEMINI.md
├── .agents/skills/llm-wiki-query/SKILL.md
└── wiki/
    ├── index.md
    ├── concepts/
    └── papers/
```

As páginas podem estar em qualquer subpasta de `wiki/`, desde que sejam
arquivos Markdown.

## Usar em outro PC

1. Clone a branch `dev` e disponibilize a pasta da wiki, sem copiar o arquivo
   `.env`.
2. Instale `uv` ou Poetry (recomendados), ou use Python + `pip`; instale também
   pelo menos um dos três motores.
3. Crie o `.env` local e configure `WIKI_PATH`.
4. O colega autentica o motor com a própria conta:
   - Antigravity: abra o site e use **Conectar com Google**.
   - Codex com assinatura ChatGPT: execute `codex login`.
   - Codex com API: `printenv OPENAI_API_KEY | codex login --with-api-key`.
   - OpenCode + Ollama: não exige conta externa; o modelo roda localmente.
5. Instale e execute com um dos três fluxos documentados acima.

Nunca copie `~/.codex/auth.json`, chaves de API ou arquivos de login. Cada
usuário deve criar a própria sessão local.

O botão de login do Antigravity só funciona quando a página é aberta no próprio
computador em `127.0.0.1`. Esse limite impede que alguém na rede faça o servidor
abrir programas na máquina hospedeira.

Para acesso por outros dispositivos da mesma rede, rode:

```bash
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Com Poetry, troque `uv run` por `poetry run`. Com o ambiente `pip` ativado,
execute o comando a partir de `uvicorn`.

Isso expõe o chat na rede local sem autenticação. Use apenas em uma rede
confiável; para internet pública, adicione autenticação e HTTPS.
