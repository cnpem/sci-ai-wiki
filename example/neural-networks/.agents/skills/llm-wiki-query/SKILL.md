---
name: llm-wiki-query
description: >
  Answer a research question by consulting the personal wiki, synthesizing across pages, and producing
  a cited, cross-linked response. Use when the user asks any domain question, wants to understand a concept,
  compare models, or trace an idea through the literature — especially when they have an existing wiki.
  Also handles saving the answer as a new wiki page if the user wants to keep it.
  Trigger on: "what does the wiki say about", "explain", "compare", "how does X relate to Y",
  "summarize what we know about", or any open research question in the domain.
---

# LLM Wiki — Query Skill

Answer research questions by reading the wiki first, then synthesizing a response with dense cross-references.

---

## Step 1 — Read the Index

Always start by reading `wiki/index.md`. This gives you the map of everything that has been ingested. Do not answer from memory alone — always ground your response in wiki pages.

---

## Step 2 — Identify Relevant Pages

From the index, identify which pages are relevant to the question. Relevant pages typically include:

- **Concept pages** for core ideas mentioned in the question
- **Paper pages** that introduce or evaluate those ideas
- **Model pages** if the question is architecture-specific
- **Author pages** only if the question is about a researcher's body of work

List the pages you're about to read before reading them, so the user can see your reasoning.

---

## Step 3 — Read Relevant Pages

Read each identified page in full. As you read, note:

- **Direct answers** to the question
- **Contradictions** between pages (e.g., paper A claims X, paper B claims ¬X)
- **Gaps** — aspects of the question the wiki doesn't address
- **Related threads** the user might not have asked about but would want to know

---

## Step 4 — Synthesize and Respond

Write the answer using `[[wiki-link]]` syntax to reference every page you draw from. Structure the response based on the question type:

### Concept explanation
- Definition → Intuition → Math → Why it matters → Open questions
- Cite `[[paper_id]]` for every non-trivial claim

### Model comparison
- Side-by-side on: equivariance type, message-passing order, benchmark results, computational cost
- Note which benchmarks appear in which `[[paper_id]]`

### Literature trace ("how has X evolved?")
- Chronological structure
- Use `[[paper_id]]` citations throughout
- End with current frontier and open problems

### Open question / thesis-level question
- Synthesize what the wiki currently supports
- Explicitly flag what is not yet answered
- Suggest which ingested papers are most relevant next steps

---

## Step 5 — Flag Gaps

If the question touches on something the wiki doesn't cover, be explicit:

> "The wiki doesn't currently have a page on [topic]. Based on what I've read, [best current answer]. You might want to ingest [related paper/concept] to fill this gap."

Do not fabricate citations. If you're reasoning beyond the wiki, say so clearly.

---

## Step 6 — Offer to Save

After answering, ask:

> "Should I save this as a wiki page? If so, I'll add it under `wiki/concepts/` or `wiki/notes/` and update the index and log."

If the user says yes:
1. Choose an appropriate `snake_case` page ID
2. Create the page with YAML frontmatter (consult `wiki/schema.md`)
3. Update `wiki/index.md`
4. Append to `wiki/log.md`:

```
## [YYYY-MM-DD] query | <Question>
- Brief answer summary.
- New page created: [[page_id]]
```

---

## Quality Checks

Before finalizing your response:

- Every factual claim has a `[[wiki-link]]` citation
- Contradictions between sources are surfaced, not hidden
- Gaps are named explicitly
- The response could stand alone as a useful wiki page (in case the user wants to save it)