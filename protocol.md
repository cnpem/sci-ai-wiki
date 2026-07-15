# LLM Wiki — Beginner Tutorial
### How to Build Your Personal AI-Powered Research Knowledge Base, Step by Step

---

Welcome! This tutorial will walk you through setting up your own **LLM Wiki** — a personal knowledge base where an AI assistant helps you organize, connect, and explore your research. No coding experience required.

By the end of this tutorial you will have a working wiki folder on your computer, ready to start ingesting research papers.

---

## What You'll End Up With

After following these steps, your project folder will look like this:

```
my-research-wiki/
├── AGENTS.md               ← Instructions for the AI
├── raw/                    ← Where YOU put your PDFs and notes
│   ├── papers/
│   ├── notes/
│   ├── books/
│   ├── code/
│   └── repos/
└── wiki/                   ← Where the AI writes everything
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

**The golden rule:** You add things to `raw/`. The AI writes to `wiki/`. 

---

## Before You Start

You need:
- **An AI assistant** that can read and write files on your computer. Examples: Claude Code, Gemini Antigravity, or any agentic AI setup.
- **A few research papers** in PDF format (even 1 is enough to start).
- **10 minutes** to complete this setup.

To download Antigravity:
https://antigravity.google/

You have already received the antigravity link for downloading. When done, open it. It will work just as VSCode or any other VSCode-like code editor. You will see a chat window and a file browser. Open the folder you want your SciAIWiki to be set up in. The folder will open and you should drag or upload the prompt.md and .agents folder there (Just put the .zip folder in there or the contents of it after unzipping it).

You should see the .agents folder, and the graph.html file in the left file browser and the chat window on the right. Now you can follow to the next step.
---

## Step 1 — Trigger the Setup Skill

The wiki setup is handled by the `llm-wiki-setup` skill, which lives at `.agents/skills/llm-wiki-setup/SKILL.md`. Your AI assistant reads this skill and knows exactly what to do.

**Here's how:**

1. Open your AI assistant in the root of your wiki project (the folder that contains `.agents/`)
2. Make sure your AI has access to the project files (e.g., just ask what files do you see and it should answer the files that show on the left.)
3. Say: **"I want to set up my wiki"** (or "initialize my wiki", "set up my research wiki" — any natural phrasing works)

The AI will read the skill, **automatically install any missing tools** (Python, pdftotext, pymupdf) for your OS, then start the interview.

✅ **Done when:** The AI reports the environment is ready and begins asking you questions.

---

## Step 2 — Answer the AI's Questions

After confirming the environment is ready, the AI will ask you 5 questions. These help it configure the wiki for your specific research. Take your time answering them — even rough answers are fine.

**The 5 questions:**

1. **What is your research topic?**
   *Example: "I study machine learning for protein structure prediction."*

2. **What is your thesis statement or main research question?**
   *Example: "I'm exploring whether graph neural networks can outperform traditional methods for predicting protein folding."*
   *Tip: Even a rough, uncertain answer is fine. You can update this later.*

3. **What are 3–5 big open questions you're trying to answer?**
   *Example: "Can we reduce compute costs? Does equivariance matter? How do we handle disordered regions?"*

4. **Do you need any extra folder categories beyond the defaults?**
   *Defaults are: Papers, Concepts, Models, Authors, Reviews.*
   *You might add: `datasets/`, `experiments/`, `methods/`, `clinical_trials/`.*
   *If you're not sure, just say "no, the defaults are fine."*

5. **Any special fields you want tracked for each paper?**
   *Example for ML: "I want to track whether code is available and what benchmark was used."*
   *If unsure, say "use the defaults."*

✅ **Done when:** You've answered all 5 questions and the AI has confirmed it understood your answers.

---

## Step 3 — Confirm the Plan

The AI will show you a summary of what it's about to create, looking something like this:

> **Here's what I'll create:**
> ```
> my-research-wiki/
> ├── raw/   (your PDFs go here)
> └── wiki/  (the AI writes here)
>     └── index.md, log.md, overview.md, schema.md
> ```
> Wiki configured for: **[your research topic]**
> Shall I proceed?

Read it over quickly and reply **"Yes, go ahead"** (or ask to change anything before it starts).

✅ **Done when:** You've confirmed and the AI starts creating files.

---

## Step 4 — The AI Creates Your Wiki Files

Now the AI will create several files automatically. You don't need to do anything — just wait.

Here's what gets created and what each file does:

| File | What it does |
|------|--------------|
| `AGENTS.md` | The AI's instruction manual — it reads this every session |
| `wiki/overview.md` | Your thesis statement and research questions |
| `wiki/schema.md` | The format (template) for each type of wiki page |
| `wiki/index.md` | A master list of all wiki pages (starts empty) |
| `wiki/log.md` | A history of everything the AI has done |

✅ **Done when:** The AI says all files have been created and shows you the verification output.

---

## Step 5 — Drop Your First PDF Into `raw/papers/`

Now it's your turn. Find a research paper you want to add to the wiki (any PDF will do).

Copy or move that PDF into the `raw/papers/` folder inside your project.

**Example:** If your project is at `Documents/my-research-wiki/`, put the PDF at:
```
Documents/my-research-wiki/raw/papers/my-first-paper.pdf
```

✅ **Done when:** Your PDF is sitting inside `raw/papers/`.

---

## Step 6 — Ingest Your First Paper

Now tell the AI to read and process the paper:

> "Ingest raw/papers/my-first-paper.pdf"

The AI will:
1. Extract the text from the PDF
2. Read the full paper
3. Give you a short briefing about what it found
4. Ask what you want it to emphasize
5. Create wiki pages for the paper, its key concepts, models, and authors
6. Update the index and log

**During the discussion step, you can say things like:**
- "This paper is important because it contradicts what I thought about X"
- "Focus on the math, not the experiments"
- "This is the baseline I'm trying to beat — note its limitations"
- "Just go ahead" (if you have no strong preferences)

✅ **Done when:** The AI says the ingest is complete and you can see new files in `wiki/papers/`, `wiki/concepts/`, etc.

---

## Step 7 — Explore What Was Created

Open the `wiki/` folder and look around. You should see:

- A new file in `wiki/papers/` with the paper's title
- Possibly new files in `wiki/concepts/` and `wiki/models/`
- An entry in `wiki/index.md` listing the paper
- A new entry at the bottom of `wiki/log.md`

You can open any of these files in a text editor to read them. If you use [Obsidian](https://obsidian.md) (free), you can open the `wiki/` folder as a vault to see the `[[links]]` between pages as a graph.

✅ **Done when:** You've looked at at least one wiki page and seen the structured content the AI created.

---

## You're Done! 🎉

Your wiki is running. Here's what to do next:

### Keep growing it
After each paper you read, drop the PDF in `raw/papers/` and say "Ingest [filename]". The wiki gets richer with every paper.

### Ask it questions
At any point, ask your AI assistant a research question like:
- "What does the wiki say about attention mechanisms?"
- "Compare the two models we've ingested so far"
- "What are the gaps in my coverage of topic X?"

### Run a health check
After every 10–15 papers, say: **"Lint the wiki"** — the AI will check for broken links, missing pages, and gaps, and suggest what to read next.

### Write a literature review
When you're ready to write, say: **"Write a review of [topic]"** — the AI synthesizes everything the wiki knows into a structured narrative.

---

## Quick Reference Card

| What you want to do | What to say |
|---|---|
| Add a paper | `"Ingest raw/papers/filename.pdf"` |
| Ask a research question | Just ask it naturally |
| Check wiki health | `"Lint the wiki"` |
| Write a literature review | `"Write a review of [topic]"` |
| See everything in the wiki | Open `wiki/index.md` |
| See what the AI has done | Open `wiki/log.md` |

---

## Troubleshooting

**"The AI didn't install the tools / says Python is missing"**
Make sure your AI assistant has permission to run terminal commands. If it can't install automatically, follow its instructions to install Python from https://python.org/downloads, then restart and try again.

**"The AI didn't create the folders"**
Make sure your AI assistant has permission to create files and folders on your computer.

**"I can't find the files the AI created"**
Check that you told the AI the correct path to your project folder. Try asking: "Where did you create the wiki files?"

**"A wiki page looks wrong or incomplete"**
You can ask the AI to fix it: "Please update the page for [paper name] to include [missing information]."

**"I want to add folders for my field (e.g., `datasets/`)"**
Say: "Add a `datasets/` folder to the wiki structure and update AGENTS.md to include it."

---

## Tips for Long-Term Success

- **Ingest one paper at a time.** Rushing through many at once produces shallow, low-quality pages.
- **Talk to the AI during ingestion.** Tell it what the paper means for your research. This is where your own thinking gets woven in.
- **Run a lint pass every 2–3 weeks.** It catches problems before they pile up.
- **Update `wiki/overview.md` as your thinking evolves.** The AI uses it as your compass.
- **Don't obsess over perfect PDFs.** Messy scans, preprints, and imperfect formatting all work fine.

---

*This protocol works for any research field. Once you've adapted the schema to your domain and built up 20+ papers, you'll have a genuinely powerful intellectual artifact — a compounding graph of your field that grows smarter with every session.*