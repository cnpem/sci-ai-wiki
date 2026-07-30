---
name: llm-wiki-query
description: >
  Answer a research question by reading relevant wiki pages and synthesizing a cited response.
  Use for explanations, comparisons, literature questions, and "what does the wiki say" requests.
---

# LLM Wiki — Query Skill

Answer from the wiki, not from memory alone.

1. Read `wiki/index.md` and identify the pages that can answer the question.
2. Tell the user which pages you will consult, then read those pages in full.
3. Synthesize the answer with `[[page_id]]` links. Distinguish evidence, interpretation, and
   uncertainty. Surface contradictions and say when the wiki has no answer.
4. Offer to save the answer only after presenting it. Do not assume a folder or create a page
   without the user's agreement; if saved, use the schema and update the index and log.

For comparisons, cover the same useful dimensions for each option. For a concept explanation, use
definition, intuition, evidence, and open questions as appropriate. Never fabricate citations or
fill a gap with an unsupported claim.
