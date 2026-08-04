---
name: llm-wiki-review
description: >
  Produce a structured literature review on a research topic by synthesizing all relevant wiki pages
  and (optionally) supplementing with web search for recent work not yet ingested. Outputs a
  standalone review document suitable for use as a thesis chapter section, grant background,
  or conference paper related-work section.
  Use when the user asks to "write a review", "summarize the literature on", "produce a related work section",
  "give me a literature review about", or wants a comprehensive synthesis of a topic area.
  Always read this skill before starting a review.
---

# LLM Wiki — Review Skill

A literature review is not a list of summaries. It is a **synthesis**: a narrative argument about what the field knows, what it disputes, and what it doesn't yet know.

---

## Step 1 — Scope the Review

Before reading anything, ask the user:

> **What is the target topic for this review?**
> A few quick questions before I start:
> 1. What is the scope? (e.g., "equivariant GNNs for MLIPs" vs. "all GNN-based potentials" vs. "body-order completeness only")
> 2. Who is the intended audience? (thesis committee / conference reviewers / yourself)
> 3. How long should it be? (e.g., 1 page / 5 pages / full chapter section)
> 4. Should I include work not yet in the wiki? (I can search the web for recent papers)
> 5. Is there a particular argument or thesis you want the review to support?

Wait for answers. Adjust the plan accordingly.

---

## Step 2 — Identify Relevant Wiki Content

Read `wiki/index.md`. Identify all pages relevant to the scoped topic:

- Papers directly on the topic → `wiki/papers/`
- Core concepts needed to explain the topic → `wiki/concepts/`
- Models that are examples or baselines → `wiki/models/`
- Key authors whose trajectory matters → `wiki/authors/` (optional)

Read all identified pages in full.

---

## Step 3 — (Optional) Supplement with Web Search

If the user asked for work beyond the wiki, use web search to find recent papers (last 1–2 years) not yet ingested. For each found paper:

- Note it as `[NOT YET INGESTED]` in your source list
- Extract only what is findable from abstracts / summaries
- Suggest ingesting it after the review is done

Do not fabricate results. If web search finds nothing useful, say so.

---

## Step 4 — Build a Narrative Arc

Before writing, plan the review's argument. A good literature review has a shape:

**Typical arc for a technical domain:**
1. **Problem framing** — Why does this problem matter? What is the core challenge?
2. **Early approaches** — What were the first solutions? What did they get right and wrong?
3. **Key breakthroughs** — What shifted the field? What theoretical or empirical insight changed the direction?
4. **Current state of the art** — What are the dominant approaches? What do they have in common?
5. **Open problems** — What is not yet solved? Where is the frontier?
6. **Your positioning** (optional) — How does your thesis / research contribute?

Adapt this arc to the user's scope. A short review may compress 1–3 into one paragraph.

---

## Step 5 — Write the Review

Write in prose, not bullet lists. Use `[[wiki-link]]` citations inline throughout.

### Style guidelines:

- **Lead with ideas, not authors.** Say "Body-order completeness became the central theoretical benchmark [[batatia_cartesian_ace_2023]]" not "Batatia et al. (2023) introduced..."
- **Connect papers to each other.** Don't summarize each paper in isolation — show how they build on, respond to, or contradict each other.
- **Be specific about what is contested.** If two papers disagree on a benchmark or claim, name both and explain the tension.
- **Quantify where possible.** Cite specific numbers from benchmarks with `[[paper_id]]` attributions.
- **Surface gaps explicitly.** The review should make the need for future work (including yours) obvious.

### Section template (adapt to scope):

```markdown
# Literature Review: [Topic]

## Background and Motivation
[Why this problem exists and why it's hard]

## Foundational Work
[Earliest relevant approaches, with [[citations]]]

## Key Developments
[The pivotal papers and ideas that shaped the field, in rough chronological order]

## Current Approaches
[What the state of the art looks like, with comparative analysis]

## Open Problems and Gaps
[What the field hasn't solved, cross-linked to [[wiki/overview.md]] frontier questions]

## Summary
[1–2 paragraph synthesis of where things stand]
```

---

## Step 6 — Self-Critique Pass

Before presenting to the user, check:

- [ ] Every non-trivial claim has a `[[wiki-link]]` citation
- [ ] No paper is only summarized in isolation — it is connected to at least one other
- [ ] Contradictions between papers are named, not smoothed over
- [ ] The narrative has a direction — it builds toward the open problems section
- [ ] Nothing is fabricated — all claims trace back to ingested wiki pages or clearly labeled web sources

---

## Step 7 — Present and Offer to Save

Present the review in the conversation. Then offer:

> "Should I save this as a wiki page under `wiki/reviews/<topic_id>.md`? I'll update the index and log."

If yes:
1. Save to `wiki/reviews/<topic_id>.md` with YAML frontmatter including `type: review`, `date`, `scope`, `audience`
2. Update `wiki/index.md` with a `## Reviews` section if it doesn't exist
3. Append to `wiki/log.md`:

```
## [YYYY-MM-DD] review | <Topic>
- Scope: [brief description]
- Sources synthesized: N wiki pages, M web sources
- New page created: [[reviews/topic_id]]
```

---

## What Makes a Good Review

The review should leave the reader understanding:
1. **Why the problem is hard** (motivation)
2. **What has been tried** (history)
3. **What works and why** (analysis)
4. **What remains open** (frontier)

If it achieves these four, it's useful. If it's just a list of paper summaries, it's not a review — it's a bibliography.