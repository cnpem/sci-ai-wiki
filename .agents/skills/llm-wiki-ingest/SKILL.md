---
name: llm-wiki-ingest
description: >
  Add one academic source to a research wiki after reading it and discussing the useful focus
  with the researcher. Use for "ingest", "process", or "add this paper" requests.
---

# LLM Wiki — Ingest Skill

The result is a set of useful, connected wiki pages—not a copied abstract. Protect the original
source and preserve uncertainty.

## Before writing

1. Confirm the file exists and identify whether it is PDF, Markdown, or plain text. Extract PDF text
   before reading it; use the project setup script for the required tools when available.
2. Read the complete source. Note its question, contribution, evidence, limitations, concepts,
   models, and authors. Do not write pages yet.
3. For one source, summarize what you found and ask what the researcher wants emphasized. For a
   batch, process sources one at a time and use neutral defaults between them.

## Create or update pages

Read `wiki/schema.md` first. Create only pages with enough evidence to be meaningful. For each page:

- add the required front matter;
- explain the idea in your own words;
- cite the source with `[[paper_id]]` links;
- connect it to existing pages without inventing relationships;
- preserve existing content when updating a page.

For paper pages, `authors` must always be a non-empty YAML list of full names in the form
`Given names Family name`, for example `authors: [Ada Lovelace, Alan Turing]`. Do not use
`Last, First`, author IDs, or a single unwrapped string. Author pages use the same name format in
their scalar `name` field. Models may refer to author-page IDs only in fields explicitly documented
as IDs.

Update the index, overview, and append-only log only when the source genuinely changes them. Never
write to `raw/`.

## Report

Tell the researcher which pages were created or updated, what the source contributed, and what was
left uncertain. Do not claim that a page is complete when the source does not support it.
