# Wiki Research Chat

Chat local e somente leitura para consultar uma wiki com Antigravity,
OpenCode + Ollama ou Codex. A interface não mostra terminal e não escreve na
wiki.

## Testar a branch `dev`

```bash
git clone --branch dev https://github.com/cnpem/sci-ai-wiki.git
cd sci-ai-wiki/wiki-agent-ui
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `WIKI_PATH` no `.env`, autentique pelo menos um motor conforme as seções
abaixo e execute:

```bash
python app.py
```

Acesse <http://127.0.0.1:8000>. Para confirmar a instalação, rode
`pytest -q`.

## Fase 1 — instalar

Requisitos básicos: Python 3.11 ou mais recente e pelo menos um dos motores:

- Antigravity CLI instalado, com uma sessão do `agy` autenticada; ou
- OpenCode e Ollama instalados, com o modelo configurado já disponível; ou
- Codex CLI instalado e autenticado com `codex login`.

### macOS ou Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
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

O modo headless precisa de permissão de leitura para essa pasta em
`~/.gemini/antigravity-cli/settings.json`:

```json
{
  "permissions": {
    "allow": ["read_file(/caminho/para/a/pasta/graph)"]
  }
}
```

Critério de sucesso: `WIKI_PATH` contém `GEMINI.md`, `.agents/skills/` e
`wiki/`; `GET /api/health` informa `"ready": true`.

## Fase 2 — executar

```bash
python app.py
```

Abra <http://127.0.0.1:8000>.

Critério de sucesso: a página mostra o total de páginas e aceita uma pergunta.

## Fase 3 — verificar

```bash
pytest -q
```

Os testes cobrem indexação local, bloqueio de caminhos, estado do agente,
anexos PDF e conversas simuladas. Eles não gastam cota do Antigravity.

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

1. Copie `wiki-agent-ui` e a pasta da wiki, sem copiar o arquivo `.env`.
2. Instale Python e pelo menos um dos três motores.
3. Crie o `.env` local e configure `WIKI_PATH`.
4. O colega autentica o motor com a própria conta:
   - Antigravity: execute `agy` e conclua o login.
   - Codex com assinatura ChatGPT: execute `codex login`.
   - Codex com API: `printenv OPENAI_API_KEY | codex login --with-api-key`.
   - OpenCode + Ollama: não exige conta externa; o modelo roda localmente.
5. Execute `python app.py`.

Nunca copie `~/.codex/auth.json`, chaves de API ou arquivos de login. Cada
usuário deve criar a própria sessão local.

Para acesso por outros dispositivos da mesma rede, rode:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Isso expõe o chat na rede local sem autenticação. Use apenas em uma rede
confiável; para internet pública, adicione autenticação e HTTPS.
