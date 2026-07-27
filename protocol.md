# LLM Wiki Protocol
### A Researcher's Guide to Building a Compounding AI-Assisted Knowledge Base

---

## What is an LLM Wiki?

An LLM wiki is a **personal research knowledge base** maintained by an AI assistant. You own the raw materials (PDFs, notes, book chapters). The AI owns the structured wiki — creating, updating, and cross-referencing pages as you feed it sources.

The key insight is that knowledge compounds. Unlike a chatbot conversation that vanishes, every paper you ingest makes the wiki richer, denser, and more useful for answering your next question. After 20–30 ingested papers, the wiki becomes a genuine intellectual artifact — a graph of your field that can answer questions, surface contradictions, and generate literature reviews.

This protocol is **field-agnostic**. It works for any sustained research project: a Master's thesis, a PhD, a systematic review, or a research team's shared knowledge base.

---

## Prerequisites

### What you need
- An AI assistant that can read files and write to a local directory (e.g., Claude with computer use, Claude Code, or a similar agentic setup)
- A folder of raw materials: PDFs, markdown notes, book excerpts
- The four skill files: `llm-wiki-ingest`, `llm-wiki-query`, `llm-wiki-lint`, `llm-wiki-review`

### What you don't need
- Any coding experience
- A pre-existing organizational system
- Clean, well-formatted sources (the ingest skill handles messy PDFs)

---

## Directory Structure

Set up this exact layout. The AI will populate `wiki/` entirely — you only ever add files to `raw/`.

```
<your-project>/
├── raw/                    ← YOU OWN THIS. Never let the AI write here.
│   ├── papers/             # PDFs and markdown of academic papers
│   ├── notes/              # Personal reading notes, scratch thoughts
│   ├── books/              # Book chapters, textbook excerpts
│   ├── code/               # Reference implementations, snippets
│   └── repos/              # Cloned or summarized repositories
│
└── wiki/                   ← AI OWNS THIS. You read, AI writes.
    ├── index.md            # Master catalog — every wiki page with a one-line summary
    ├── log.md              # Append-only activity log (ingest, query, lint events)
    ├── overview.md         # Your evolving research thesis and frontier questions
    ├── schema.md           # Frontmatter schema for each page type
    ├── papers/             # One file per ingested source
    ├── concepts/           # Core theoretical concepts and math
    ├── models/             # Specific architectures, systems, or methods
    ├── authors/            # Key researchers
    └── reviews/            # Literature reviews produced by the AI
```

**The `raw/` directory is sacred.** The AI reads it; it never writes to it. This boundary protects your original materials and your own voice.

---

## Initial Setup

### 1. Create the directory structure
```bash
mkdir -p raw/{papers,notes,books,code,repos}
mkdir -p wiki/{papers,concepts,models,authors,reviews}
```

### 2. Initialize the wiki files
Ask the AI to create these four files for you:

- `wiki/index.md` — start with empty sections for Papers, Concepts, Models, Authors, Reviews
- `wiki/log.md` — start with a single entry: `## [DATE] init | Wiki initialized`
- `wiki/overview.md` — write your current thesis statement (even if rough) and 3–5 frontier questions you're trying to answer
- `wiki/schema.md` — ask the AI to generate schemas appropriate for your field (see Schema section below)

### 3. Drop your sources in `raw/`
Don't organize obsessively. Just put PDFs in `raw/papers/`. The wiki will do the organizing.

---

## Schema Design and Front Matter

The schema defines the YAML **front matter** for each page type. Front matter is a YAML block at the
top of a Markdown page, between two lines containing only `---`. It lets the agent search and check
pages while keeping the main text easy for a person to read.

For paper pages, `title`, `authors`, and `year` are required. `authors` must always be a non-empty
list of full names written as `Given names Family name`. This works for one or many authors:

Ask the AI to create `wiki/schema.md` with schemas for your field. A general starting point:

```yaml
---
title: "Full paper title"
authors: [Ada Lovelace]
year: 2024
venue: "NeurIPS / arXiv / JCTC / etc."
doi: "10.xxxx/xxxxx"        # optional
arxiv: "2401.12345"         # optional
tags: ["concept-a", "concept-b"]
status: "read"              # read | skimming | pending
relevance: high             # high | medium | low
---

# Concept page schema
---
title: "Concept Name"
tags: ["math", "theory", "implementation"]
related_papers: ["paper_id_1", "paper_id_2"]
status: "mature"            # stub | developing | mature
---

# Model page schema
---
title: "Model Name"
authors: ["author_id_1"]
year: 2023
paper: "paper_id"
tags: ["architecture-type", "domain"]
---

# Author page schema
---
name: "Full Name"
affiliation: "Institution"
website: ""                 # optional
papers: ["paper_id_1"]
---
```

Use a list for multiple authors too: `authors: [Ada Lovelace, Alan Turing]`. Do not use
`Lovelace, Ada`, author IDs, or an unwrapped string such as `authors: Ada Lovelace`.

Adapt these to your domain. Add fields that matter to your research questions.

---

## The Four Operations

### 1. Ingest — Adding a Source

**Trigger:** "Ingest [filename]" or "Process [filename]"

The ingest skill handles the full pipeline:
- Extracts text from PDFs automatically
- Reads the source in full before talking to you
- Presents a briefing and asks what to emphasize
- Creates/updates pages in papers/, concepts/, models/, authors/
- Updates the index, overview, and log

**One source at a time.** Dump-ingestion (processing many papers at once without conversation) is an antipattern. It produces shallow, disconnected pages. The conversation between ingest steps is where you add your own thinking.

**What to say during the discussion step:**
- "This paper is important because it contradicts what I thought about X"
- "Focus on the mathematical formulation, not the benchmarks"
- "This is the baseline I'm trying to beat — note its limitations carefully"
- "Just go ahead" (if you have no strong preferences)

### 2. Query — Asking a Research Question

**Trigger:** Any research question

The query skill reads the index, identifies relevant pages, and synthesizes an answer with dense cross-references. Use it to:
- Understand a concept ("Explain equivariance and why it matters for potentials")
- Compare approaches ("What are the tradeoffs between NequIP and MACE?")
- Trace an idea ("How has the treatment of many-body interactions evolved?")
- Stress-test your thesis ("What does the wiki say against my current argument?")

The AI will flag gaps — places where the wiki doesn't have an answer. This tells you what to ingest next.

### 3. Lint — Health-Checking the Wiki

**Trigger:** "Lint the wiki" or "Health-check the wiki"

Run a lint pass every 10–15 ingests, or before a major writing session. The lint skill checks
objective errors such as:
- **Broken links** — `[[references]]` pointing to pages that don't exist
- **Invalid required front matter** — missing fields or values that do not follow the schema
- **Invalid author metadata** — a paper's authors are not a non-empty list of full names
- **Index mismatches** — the index points to a page that does not exist

If no objective errors are found, the report says **Validation passed**. Optional ideas, such as
possible new sources or extra links, are clearly labeled as suggestions and are never treated as
failures. Concepts mentioned in prose, page connectivity, and research gaps are not errors unless
the schema explicitly requires them.

### 4. Review — Producing a Literature Review

**Trigger:** "Write a review of [topic]" or "Summarize the literature on [topic]"

The review skill synthesizes everything the wiki knows about a topic into a coherent narrative. You can specify:
- Scope (broad field vs. narrow subtopic)
- Audience (thesis committee, conference reviewers, yourself)
- Length
- Whether to include work not yet in the wiki (via web search)

Reviews can be saved back to `wiki/reviews/` and are updated as you ingest more papers.

---

## Page ID Conventions

Consistent IDs make the wiki navigable. Adapt these to your field:

| Type | Format | Example |
|------|--------|---------|
| Paper | `<lastname>_<keyword>_<year>` | `batatia_mace_2022` |
| Concept | `<concept_name>` | `equivariance`, `attention_mechanism` |
| Model/Method | `<name>` | `transformer`, `schnet`, `alphafold` |
| Author | `<lastname>_<firstname>` | `vaswani_ashish` |
| Review | `<topic>_review` | `mlip_review`, `protein_folding_review` |

Use `snake_case` throughout.

---

## Cross-Reference Conventions

The wiki uses `[[wiki-link]]` syntax (compatible with Obsidian, Foam, and similar tools). Every page should link to related pages. The richer the link graph, the more useful the wiki.

Rules:
- Every paper page should link to the concepts it introduces or uses
- Every concept page should link to the papers that define or use it
- Every model page should link to its paper and the concepts it implements
- Never leave a page as a dead end — always link outward

---

## Workflow Rhythm

A sustainable rhythm for active research:

| Frequency | Action |
|-----------|--------|
| After reading a paper | Ingest it. Have the conversation. |
| When stuck or confused | Query the wiki. |
| Every 2–3 weeks | Lint pass. |
| Before writing a chapter/section | Run a review on the relevant topic. |
| When starting a new research angle | Update `wiki/overview.md` manually, then query to see what the wiki already knows. |

---

## Tips for Better Ingestion

**Do say during the discussion step:**
- What this paper means for your thesis
- Which claims you're skeptical of
- What it contradicts or confirms from prior ingests
- Which concepts are most important to formalize

**Don't:**
- Ingest the same paper twice (check the log)
- Ingest papers you haven't read at all — shallow ingestion produces shallow pages
- Let the wiki go more than 20 papers without a lint pass

---

## For Teams

If multiple researchers share a wiki:

1. **One AI session per ingest** — don't have two people ingesting simultaneously
2. **Use git** — commit after every ingest session. The log makes commit messages easy: `git log wiki/log.md | tail -1`
3. **Shared overview.md** — have a weekly check-in to update the thesis and frontier questions together
4. **Author pages** — expand author pages to include "who in our team focuses on this author's work"

---

## Adapting the Schema to Your Field

The defaults work for any empirical research field. Adjust based on your domain:

**Experimental sciences:** Add `dataset`, `experimental_conditions`, `replication_status` fields to paper pages.

**Computer science / ML:** Add `code_available`, `benchmark`, `compute_requirements`.

**Social sciences / humanities:** Add `methodology`, `primary_sources`, `theoretical_framework`.

**Clinical / medical:** Add `study_type`, `n_participants`, `outcome_measures`, `evidence_level`.

---

## Anti-Patterns to Avoid

| Anti-pattern | Why it's harmful | Fix |
|---|---|---|
| Bulk ingestion without conversation | Produces shallow, disconnected pages | One source at a time, always discuss first |
| Never running lint | Broken links accumulate silently | Lint every 10–15 ingests |
| Ignoring the overview | The wiki loses its thesis thread | Update overview after every 5 ingests |
| Writing to `raw/` | Corrupts your original sources | Never. The boundary is sacred. |
| Trusting the wiki blindly | The AI can make mistakes | Cross-check surprising claims against the original source |
| Not using the query skill | Missing the compounding benefit | Ask the wiki questions regularly, not just at writing time |

---

## Getting Started Today

1. Create the directory structure
2. Drop 3–5 of your most important papers in `raw/papers/`
3. Ask the AI to initialize the wiki files with your thesis statement
4. Ingest your first paper: "Ingest [filename]"
5. After the conversation, look at what was created in `wiki/`

The wiki is only as good as what you put into it — and how much you talk to it. Start small, be consistent, and let it compound.

---

*This protocol is designed to be field-agnostic. If you adapt the schema or conventions for your domain in ways that work well, consider sharing your `wiki/schema.md` with others in your field.*
