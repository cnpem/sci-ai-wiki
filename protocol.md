# LLM Wiki — Tutorial para Iniciantes
### Como Construir sua Base de Conhecimento de Pesquisa com Inteligência Artificial, Passo a Passo

---

Bem-vindo! Este tutorial vai te guiar pela configuração do seu próprio **LLM Wiki** — uma base de conhecimento pessoal onde um assistente de IA te ajuda a organizar, conectar e explorar sua pesquisa. Nenhum conhecimento de programação é necessário.

Ao final deste tutorial, você terá uma pasta de wiki funcionando no seu computador, pronta para começar a ingerir artigos de pesquisa.

---

## O Que Você Vai Ter no Final

Após seguir esses passos, a pasta do seu projeto vai ficar assim:

```
minha-wiki-de-pesquisa/
├── AGENTS.md               ← Instruções para a IA
├── raw/                    ← Onde VOCÊ coloca seus PDFs e anotações
│   ├── papers/
│   ├── notes/
│   ├── books/
│   ├── code/
│   └── repos/
└── wiki/                   ← Onde a IA escreve tudo
    ├── index.md
    ├── log.md
    ├── overview.md
    ├── schema.md
    ├── papers/
    ├── concepts/
    ├── models/
    ├── authors/
    └── reviews/
```

**A regra de ouro:** Você adiciona coisas em `raw/`. A IA escreve em `wiki/`. Nunca deixe esses papéis se inverterem.

---

## Antes de Começar

Você precisa de:
- **Um assistente de IA** que consiga ler e escrever arquivos no seu computador. Exemplos: Claude Code, Gemini Antigravity, ou qualquer configuração de IA agêntica.
- **Alguns artigos de pesquisa** em formato PDF (mesmo 1 já é suficiente para começar).
- **10 minutos** para concluir esta configuração.

É isso. Você não precisa saber programar.

---

## Passo 1 — Carregue as Instruções de Configuração no seu Assistente de IA

Antes de pedir qualquer coisa à IA, você precisa dar a ela as instruções de configuração. A IA não tem ideia do que é um LLM Wiki por padrão — o `prompt.md` é o roteiro que ela precisa seguir.

**Veja como fazer:**

1. Abra o arquivo `prompt.md` (ele está na mesma pasta que este tutorial)
2. Selecione todo o texto e copie (`Cmd+A`, depois `Cmd+C` no Mac)
3. Abra seu assistente de IA e **cole o texto copiado como sua primeira mensagem**
4. Envie

A IA agora saberá exatamente o que fazer. Ela iniciará a entrevista (Passo 2) automaticamente.

✅ **Concluído quando:** Você colou o `prompt.md` na IA e ela confirmou que está pronta para configurar sua wiki.

---

## Passo 2 — Responda às Perguntas da IA

Após receber as instruções, a IA vai te fazer 5 perguntas. Elas ajudam a configurar a wiki para a sua pesquisa específica. Responda com calma — respostas aproximadas estão ótimas.

**As 5 perguntas:**

1. **Qual é o seu tema de pesquisa?**
   *Exemplo: "Estudo aprendizado de máquina para predição de estrutura de proteínas."*

2. **Qual é a sua hipótese ou pergunta central de pesquisa?**
   *Exemplo: "Estou explorando se redes neurais de grafos conseguem superar métodos tradicionais para predição de dobramento de proteínas."*
   *Dica: Mesmo uma resposta incerta e aproximada está ótima. Você pode atualizar depois.*

3. **Quais são as 3–5 grandes questões abertas que você está tentando responder?**
   *Exemplo: "Conseguimos reduzir o custo computacional? A equivariância importa? Como lidar com regiões desordenadas?"*

4. **Você precisa de categorias de pastas extras além dos padrões?**
   *Os padrões são: Papers, Concepts, Models, Authors, Reviews.*
   *Você pode adicionar: `datasets/`, `experiments/`, `methods/`, `clinical_trials/`.*
   *Se não tiver certeza, diga "não, os padrões estão ótimos."*

5. **Há campos especiais que você quer rastrear para cada artigo?**
   *Exemplo para ML: "Quero rastrear se o código está disponível e qual benchmark foi usado."*
   *Se não souber, diga "use os padrões."*

✅ **Concluído quando:** Você respondeu todas as 5 perguntas e a IA confirmou que entendeu suas respostas.

---

## Passo 3 — Confirme o Plano

A IA vai te mostrar um resumo do que está prestes a criar, parecido com isto:

> **Aqui está o que vou criar:**
> ```
> minha-wiki-de-pesquisa/
> ├── raw/   (seus PDFs ficam aqui)
> └── wiki/  (a IA escreve aqui)
>     └── index.md, log.md, overview.md, schema.md
> ```
> Wiki configurada para: **[seu tema de pesquisa]**
> Posso prosseguir?

Leia rapidamente e responda **"Sim, pode continuar"** (ou peça para alterar algo antes de começar).

✅ **Concluído quando:** Você confirmou e a IA começou a criar os arquivos.

---

## Passo 4 — A IA Cria os Arquivos da sua Wiki

Agora a IA vai criar vários arquivos automaticamente. Você não precisa fazer nada — apenas aguarde.

Aqui está o que é criado e o que cada arquivo faz:

| Arquivo | O que faz |
|---------|-----------|
| `AGENTS.md` | O manual de instruções da IA — ela lê isso a cada sessão |
| `wiki/overview.md` | Sua hipótese e perguntas de pesquisa |
| `wiki/schema.md` | O formato (modelo) para cada tipo de página da wiki |
| `wiki/index.md` | Uma lista mestre de todas as páginas da wiki (começa vazia) |
| `wiki/log.md` | Um histórico de tudo que a IA fez |

✅ **Concluído quando:** A IA diz que todos os arquivos foram criados e mostra a saída de verificação.

---

## Passo 5 — Coloque seu Primeiro PDF em `raw/papers/`

Agora é a sua vez. Encontre um artigo de pesquisa que você quer adicionar à wiki (qualquer PDF serve).

Copie ou mova esse PDF para a pasta `raw/papers/` dentro do seu projeto.

**Exemplo:** Se seu projeto está em `Documentos/minha-wiki-de-pesquisa/`, coloque o PDF em:
```
Documentos/minha-wiki-de-pesquisa/raw/papers/meu-primeiro-artigo.pdf
```

✅ **Concluído quando:** Seu PDF está dentro de `raw/papers/`.

---

## Passo 6 — Ingira seu Primeiro Artigo

Agora diga à IA para ler e processar o artigo:

> "Ingira raw/papers/meu-primeiro-artigo.pdf"

A IA vai:
1. Extrair o texto do PDF
2. Ler o artigo completo
3. Te dar um breve resumo do que encontrou
4. Perguntar o que você quer que ela enfatize
5. Criar páginas da wiki para o artigo, seus conceitos-chave, modelos e autores
6. Atualizar o índice e o log

**Durante a discussão (passo 4), você pode dizer coisas como:**
- "Este artigo é importante porque contradiz o que eu pensava sobre X"
- "Foque na matemática, não nos experimentos"
- "Este é o baseline que estou tentando superar — anote suas limitações"
- "Pode continuar" (se você não tiver preferências específicas)

✅ **Concluído quando:** A IA diz que a ingestão está completa e você consegue ver novos arquivos em `wiki/papers/`, `wiki/concepts/`, etc.

---

## Passo 7 — Explore o Que Foi Criado

Abra a pasta `wiki/` e dê uma olhada. Você deve ver:

- Um novo arquivo em `wiki/papers/` com o título do artigo
- Possivelmente novos arquivos em `wiki/concepts/` e `wiki/models/`
- Uma entrada em `wiki/index.md` listando o artigo
- Uma nova entrada no final de `wiki/log.md`

Você pode abrir qualquer um desses arquivos em um editor de texto para lê-los. Se você usa o [Obsidian](https://obsidian.md) (gratuito), pode abrir a pasta `wiki/` como um vault para ver os `[[links]]` entre páginas como um grafo.

✅ **Concluído quando:** Você olhou para pelo menos uma página da wiki e viu o conteúdo estruturado que a IA criou.

---

## Pronto! 🎉

Sua wiki está funcionando. Veja o que fazer a seguir:

### Continue expandindo
Após cada artigo que você ler, coloque o PDF em `raw/papers/` e diga "Ingira [nome do arquivo]". A wiki fica mais rica a cada artigo.

### Faça perguntas para ela
A qualquer momento, pergunte ao seu assistente de IA uma questão de pesquisa como:
- "O que a wiki diz sobre mecanismos de atenção?"
- "Compare os dois modelos que já ingerimos"
- "Quais são as lacunas na minha cobertura do tópico X?"

### Faça uma verificação de saúde
Após cada 10–15 artigos, diga: **"Faça um lint da wiki"** — a IA vai verificar links quebrados, páginas faltando e lacunas, e sugerir o que ler a seguir.

### Escreva uma revisão de literatura
Quando estiver pronto para escrever, diga: **"Escreva uma revisão sobre [tópico]"** — a IA sintetiza tudo que a wiki sabe em uma narrativa estruturada.

---

## Cartão de Referência Rápida

| O que você quer fazer | O que dizer |
|---|---|
| Adicionar um artigo | `"Ingira raw/papers/nome-do-arquivo.pdf"` |
| Fazer uma pergunta de pesquisa | Pergunte naturalmente |
| Verificar a saúde da wiki | `"Faça um lint da wiki"` |
| Escrever uma revisão de literatura | `"Escreva uma revisão sobre [tópico]"` |
| Ver tudo na wiki | Abra `wiki/index.md` |
| Ver o que a IA fez | Abra `wiki/log.md` |

---

## Solução de Problemas

**"A IA não criou as pastas"**
Verifique se seu assistente de IA tem permissão para criar arquivos e pastas no seu computador.

**"Não consigo encontrar os arquivos que a IA criou"**
Verifique se você disse à IA o caminho correto para a pasta do seu projeto. Tente perguntar: "Onde você criou os arquivos da wiki?"

**"Uma página da wiki parece errada ou incompleta"**
Você pode pedir à IA para corrigir: "Por favor, atualize a página do artigo [nome] para incluir [informação faltando]."

**"Quero adicionar pastas para minha área (ex: `datasets/`)"**
Diga: "Adicione uma pasta `datasets/` à estrutura da wiki e atualize o AGENTS.md para incluí-la."

---

## Dicas para o Sucesso a Longo Prazo

- **Ingira um artigo de cada vez.** Processar muitos de uma vez produz páginas rasas e de baixa qualidade.
- **Converse com a IA durante a ingestão.** Diga o que o artigo significa para sua pesquisa. É aqui que seu próprio pensamento é incorporado.
- **Faça um lint a cada 2–3 semanas.** Ele detecta problemas antes que se acumulem.
- **Atualize o `wiki/overview.md` conforme seu pensamento evolui.** A IA usa isso como sua bússola.
- **Não se preocupe com PDFs perfeitos.** Scans bagunçados, preprints e formatações imperfeitas funcionam bem.

---

*Este protocolo funciona para qualquer área de pesquisa. Uma vez que você tenha adaptado o schema ao seu domínio e construído mais de 20 artigos, você terá um artefato intelectual genuinamente poderoso — um grafo composto do seu campo que fica mais inteligente a cada sessão.*