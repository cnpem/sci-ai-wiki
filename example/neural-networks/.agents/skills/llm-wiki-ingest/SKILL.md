---
name: llm-wiki-ingest
description: >
  Ingest one or more academic sources (PDF, markdown, or plain text) into a personal research wiki.
  Handles PDF extraction automatically, conducts a focused conversation with the researcher before writing anything,
  then populates all relevant wiki directories (papers/, concepts/, models/, authors/) one section at a time.
  Use this skill whenever the user says "ingest", "process", "add this paper", or hands over a file path or PDF
  for inclusion in the wiki. Always read this skill before beginning any ingestion workflow.
---

# LLM Wiki — Ingest Skill

Ingest one source at a time. For a single source, conduct a discussion with the researcher before writing. For multiple sources (batch mode), follow the strict sequential protocol below — **never process papers in parallel, never read only part of a paper, and never delegate extraction to an external tool**.

---

## Batch Ingest Mode — When the User Provides Multiple Papers

If the user provides more than one file path or PDF at once, switch into **Batch Ingest Mode**. This mode has strict rules:

### Rules (non-negotiable)

1. **One paper at a time.** Process each paper fully — from extraction to wiki updates — before opening the next one. Do not interleave or parallelize.
2. **Full text only.** You MUST read the entire extracted text of each paper before extracting entities. Never summarize based on the abstract alone or skip sections. Read everything: introduction, related work, methods, experiments, conclusion, and appendices.
3. **Self-contained extraction.** Extract all entities yourself by reading the text directly. Do not call other tools, sub-agents, or APIs to do the reading or entity extraction for you.
4. **No user interruptions mid-batch.** Do not ask the user questions between papers. Begin writing immediately after reading each paper (Step 2's discussion is skipped for batch mode — proceed with defaults). Only report at the end of each paper and after the entire batch.

### Batch Ingest Protocol

For each paper `i` of `N`, execute this loop:

```
[Paper i/N: <filename>]

1. Extract text  →  pdftotext (or pymupdf fallback). Write to <path>.txt.
2. Read FULL text →  Read the entire .txt file. No skipping.
3. Extract entities:
   - Paper metadata (title, authors, year, venue, DOI/arXiv)
   - Core contribution (1–3 sentences)
   - All concepts introduced or relied upon
   - Models / architectures proposed or evaluated
   - Key results and benchmarks
   - Limitations and open questions
   - Key authors
4. Write wiki pages  →  Steps 3–8 of the standard ingest flow.
5. Report to user   →  Brief one-paragraph summary of what was created/updated for this paper.
6. Proceed to paper i+1.
```

After all `N` papers are processed, give a consolidated batch summary listing all pages created and updated across the entire batch.

### When to Ask Questions in Batch Mode

- **Before starting**: Confirm the list of files with the user and ask if there is any specific angle to emphasize across all papers (one question, one reply).
- **During**: Never. Process papers sequentially without pausing for feedback.
- **After**: Offer to revise any specific paper's pages if the user wishes.

---

## Step 0 — Detect File Type and Read

Before anything else, determine what kind of file you have.

### If the file is a PDF
PDFs are the most common source. They require extraction before you can read them.

```bash
# First, check if pdftotext is available
which pdftotext || apt-get install -y poppler-utils -q

# Extract text from the PDF
pdftotext -layout "<path_to_pdf>" "<path_to_pdf>.txt"

# If pdftotext fails (scanned PDF), try OCR fallback
# pip install pymupdf --break-system-packages --quiet
# python3 -c "
# import fitz
# doc = fitz.open('<path_to_pdf>')
# text = '\n'.join([page.get_text() for page in doc])
# open('<path_to_pdf>.txt', 'w').write(text)
# "
```

Read the extracted `.txt` file. Then clean it up mentally: PDFs often have broken hyphenation, garbled reference lists, and column artifacts. Focus on the body text.

### If the file is Markdown or plain text
Read it directly. No pre-processing needed.

### If the user just gives a title or DOI without a file
Ask: "Do you have the PDF or a markdown version? If not, I can note this source as pending and we can ingest it later." Do not fabricate content.

---

## Step 1 — First Pass Read

Read the source in full before talking to the user. Build a mental model of:

- **What problem does it solve?**
- **What is the core method/contribution?**
- **Which concepts does it rely on or introduce?**
- **Which models or architectures does it evaluate or propose?**
- **Who are the key authors?**
- **What are the limitations or open questions?**

Do not write anything to the wiki yet.

---

## Step 2 — Discuss Before Writing

> **Batch Mode:** Skip this step entirely. Proceed directly to Step 3 using defaults.

For single-paper ingestion, present a structured briefing to the user. Format it as a short summary, then ask targeted questions.

**Briefing template:**

> **[Paper Title]** — [First Author et al., Year]
>
> **Core contribution:** [1–2 sentences]
>
> **Key concepts touched:** [comma-separated list]
>
> **Proposed/evaluated models:** [if any]
>
> **I'm planning to create/update these wiki pages:**
> - `papers/<id>.md` (new)
> - `concepts/<concept_a>.md` (update)
> - `concepts/<concept_b>.md` (new)
> - `models/<model_name>.md` (new or update)
> - `authors/<author_id>.md` (new or update)
>
> **Before I write, I have a few questions:**
> 1. Is there a particular angle or contribution you want me to emphasize?
> 2. Does this paper connect to something you're already working on in your thesis?
> 3. Are there any claims here you're skeptical of or want flagged?

Wait for the user's answers. Adjust your plan based on their input. If they say "just go ahead", proceed with defaults.

---

## Step 3 — Create the Paper Page

Read `wiki/schema.md` to get the exact YAML frontmatter fields for paper pages.

Create `wiki/papers/<id>.md` using the schema. The paper ID format is:
`<first_author_lastname>_<keyword>_<year>` → e.g., `batatia_cartesian_ace_2023`

Include:
- Full frontmatter per schema
- Abstract (your paraphrase, not a copy)
- Core contribution section
- Method summary with math where relevant
- Key results/benchmarks
- Limitations
- Connections to other wiki pages using `[[wiki-link]]` syntax
- Open questions this paper raises

---

## Step 4 — Update Concept Pages

For each major concept the paper touches:

1. Check if `wiki/concepts/<concept_id>.md` exists.
2. **If it exists**: Add a new subsection or update the existing one. Note which paper supports which claim using `[[paper_id]]` citations. Do not erase prior content.
3. **If it doesn't exist**: Create it from scratch using the concept schema from `wiki/schema.md`. **IMPORTANT**: Never create synthetic concepts, stub pages, or placeholder pages with no substantive information. If a concept lacks enough detail in the source to populate a meaningful page, do not create it. Instead, note this gap and prompt the user to search for more information about that concept (e.g., "I found mentions of X, Y, and Z, but not enough info to create pages. Could you search for more info about them?").

Concept IDs are `snake_case` noun phrases: `polylatic_acid`, `nanotechnology`, `multi-head_attention`, `group_theory`.

For each concept page, always include:
- Definition / intuition
- Mathematical formulation (if applicable)
- Why it matters for the research domain
- `[[paper_id]]` references for every claim
- Related concepts using `[[wiki-link]]`

---

## Step 5 — Update Model Pages

If the paper introduces or significantly evaluates a specific architecture or learned potential:

1. Check if `wiki/models/<model_id>.md` exists.
2. Create or update per the model schema in `wiki/schema.md`.

Model IDs are the canonical name in `snake_case`: `mace`, `nequip`, `cartesian_ace`, `allegro`.

Each model page should include:
- Overview
- Detailed Architecture Breakdown (explain initialization, message-passing mechanics, and physical inductive biases)
- Exact architectural configuration (e.g., layers, channels, cutoff, L_max), both in YAML frontmatter and body
- Equivariance properties
- Benchmarks (with `[[paper_id]]` citations)
- Known limitations
- Links to related models and concepts

---

## Step 6 — Update Author Pages

For each key author (typically first author, corresponding author, and any recurring names in your field):

1. Check if `wiki/authors/<author_id>.md` exists.
2. Create or update using author schema from `wiki/schema.md`.

Author IDs: `<lastname>_<firstname>` → `batatia_imre`.

Author pages should note affiliation, key papers (with `[[paper_id]]` links), and research focus.

---

## Step 7 — Update `wiki/index.md`

Add new pages to the appropriate sections of the index. Format:

```markdown
- [[page_id]] — One-line summary. (Year, Author if paper)
```

If updating an existing entry, revise the summary if your new ingest changed the scope of that page.

---

## Step 8 — Update `wiki/overview.md`

Read the current `wiki/overview.md`. Ask yourself:

- Does this paper **support** the current thesis? If so, add a reference.
- Does it **challenge** or **complicate** the thesis? Flag it.
- Does it open a **new frontier question** not currently listed?

Update the relevant sections. The overview is a living document — keep it honest about what the field currently says.

---

## Step 9 — Append to `wiki/log.md`

Use the exact log format:

```
## [YYYY-MM-DD] ingest | <Paper Title>
- Summary of what was added or changed.
- Pages created: [[page_id_1]], [[page_id_2]]
- Pages updated: [[page_id_3]]
```

---

## Step 10 — Report to User

Tell the user:

> **Ingest complete.**
> Pages created: [list with `[[links]]`]
> Pages updated: [list with `[[links]]`]
>
> Anything you'd like me to revise or expand before we move on?

---

## Edge Cases

**Paper with no model contribution**: Skip Step 5. Note in the paper page that no architecture is proposed.

**Author already has a page**: Only add the new paper link. Don't overwrite their bio.

**Concept is very broad** (e.g., "graph neural networks"): Create a focused sub-concept page rather than bloating the parent. E.g., `gnn_equivariant_atomistic` rather than editing `gnn.md`.

**Scanned PDF with bad OCR**: Tell the user: "The OCR quality is poor in sections [X, Y]. I'll do my best but some math/tables may be incomplete. Consider providing a cleaner copy." Then proceed with what you have.

**No wiki yet**: If `wiki/` doesn't exist at all, tell the user: "I don't see a wiki directory yet. Should I initialize one? I'll create the structure and `schema.md` before ingesting." Then create the skeleton.