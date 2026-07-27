---
name: llm-wiki-review
description: >
  Write a literature review by connecting relevant wiki pages into a supported narrative.
  Use for requests to write or summarize a review, related work section, or literature overview.
---

# LLM Wiki — Review Skill

A review explains how ideas relate, what evidence supports them, where researchers disagree, and
what remains open. It is not a list of isolated paper summaries.

## 1. Clarify the requested result

Ask only for information that is missing and would change the review: topic and scope, audience,
approximate length, whether to include newer work outside the wiki, and any argument to emphasize.
Do not assume a folder, output location, or save request. If the user does not name a folder, keep
the review in the conversation and ask before saving it.

## 2. Read the evidence

Start with `wiki/index.md`, then read every relevant paper, concept, model, and (when useful) author
page in full. Keep a source list. Separate facts supported by wiki pages from your own synthesis.
If the user requests work outside the wiki, search for it and label each such source as not yet
ingested. Never invent a result or citation.

## 3. Write the review

Organize the result around the topic, usually with background, foundational work, key developments,
current approaches, open problems, and a short synthesis. Connect papers to one another and use
`[[page_id]]` links for claims drawn from the wiki. Explain disagreements instead of hiding them.

## 4. Check before presenting

- Every important factual claim is traceable to a wiki page or clearly labeled external source.
- The review has a narrative, not just one paragraph per paper.
- Gaps and uncertainty are explicit.
- No page, folder, or source was assumed without evidence or user instruction.

Present the review first. Offer to save it only after the user has seen it. If they agree, ask for a
file name or use `wiki/reviews/<topic_id>.md` only when that location is explicitly accepted, then
update the index and log.
