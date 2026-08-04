---
name: llm-wiki-lint
description: >
  Perform a full health-check of a research wiki: detect orphan pages, broken links, stale claims,
  missing concept pages, and data gaps. Suggest new sources to fill identified gaps.
  Use when the user says "lint the wiki", "health-check", "audit the wiki", "what's missing",
  "check my wiki", or asks for a wiki quality report. Always read this skill before starting a lint pass.
---

# LLM Wiki — Lint Skill

A lint pass audits the entire wiki for structural and semantic issues. It is non-destructive by default — it reports and proposes fixes, then applies only what the user approves.

---

## Step 1 — Read Everything

Read all files in `wiki/`:
- `wiki/index.md`
- `wiki/overview.md`
- `wiki/schema.md`
- All files in `wiki/papers/`
- All files in `wiki/concepts/`
- All files in `wiki/models/`
- All files in `wiki/authors/`
- `wiki/log.md`

Build an internal map:
- **All page IDs** that exist as files
- **All `[[links]]`** found anywhere in the wiki, and which pages they point to
- **All concept names** mentioned in body text (not just as links)
- **All paper IDs** cited inline

---

## Step 2 — Run Checks

### 2a. Orphan Pages
Pages that exist as files but have **zero inbound `[[links]]`** from any other page.
These are isolated nodes — they contribute nothing to the knowledge graph.

### 2b. Broken Links
`[[links]]` that point to page IDs that **do not exist** as files.
These are dangling references.

### 2c. Missing Concept Pages
Concept names mentioned in body text (not as `[[links]]`) that **lack their own page**.
These are implicit concepts that deserve formalization.

### 2d. Stale Claims
Claims in one page that are **contradicted by a more recently ingested paper**.
Use `wiki/log.md` to determine ingestion order (most recent date = most authoritative).
Flag, do not auto-correct.

### 2e. Schema Violations
Pages missing required YAML frontmatter fields (consult `wiki/schema.md`).

### 2f. Author–Paper Mismatches
Papers listed in `wiki/papers/` whose authors don't have corresponding pages in `wiki/authors/`, and vice versa (author pages citing papers that don't exist in the wiki).

### 2g. Overview–Wiki Divergence
Claims in `wiki/overview.md` that are not supported by any `[[paper_id]]` link, or frontier questions that have been answered by ingested papers but not updated in the overview.

### 2h. Data Gaps
Important open questions mentioned in papers or the overview that have **no corresponding concept or paper pages** attempting to address them.

---

## Step 3 — Report

Present the findings as a structured report. Group by severity:

**🔴 Critical** (broken links, missing required frontmatter)
**🟡 Structural** (orphans, author mismatches, schema violations)
**🟠 Semantic** (stale claims, overview divergence)
**🔵 Gaps** (missing concept pages, unanswered frontier questions)

For each issue, name the specific page(s) involved and describe the problem clearly.

Example format:
```
🔴 Broken link: [[nequip_symmetry_2022]] referenced in `concepts/equivariance.md` but no such paper page exists.
🟡 Orphan: `authors/schutt_kristof.md` has no inbound links.
🟠 Stale claim: `concepts/body_order.md` states "ACE is state-of-the-art" — contradicted by [[batatia_mace_2022]] (ingested later).
🔵 Missing page: "Clebsch-Gordan decomposition" mentioned 4× in papers but has no concept page.
```

---

## Step 4 — Suggest New Sources

Based on identified gaps, suggest **3–5 sources** to look for. Be specific:

- Paper title + author + approximate year (if known)
- DOI or arXiv ID (if you have it)
- Why it would fill the identified gap

---

## Step 5 — Apply Approved Fixes

Ask the user: "Which issues should I fix now?"

Only apply fixes the user explicitly approves. Safe fixes (that don't change semantics):
- Create stub pages for broken links (with a `stub: true` frontmatter flag)
- Add `[[wiki-link]]` syntax around concept names that were mentioned without links
- Fix frontmatter fields that are clearly missing

Do not auto-correct stale claims — flag them and let the user decide.

---

## Step 6 — Append to Log

```
## [YYYY-MM-DD] lint | Lint pass
- Issues found: N (X critical, Y structural, Z semantic, W gaps)
- Issues fixed: N
- Summary: [2–3 sentence summary of wiki health]
```