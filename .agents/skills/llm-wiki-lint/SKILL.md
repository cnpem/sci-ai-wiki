---
name: llm-wiki-lint
description: >
  Check a research wiki for verifiable structural and metadata errors. Report a clear pass when
  no objective errors are found, and keep optional improvements separate from errors.
  Use for "lint the wiki", "health-check", "audit the wiki", or "check my wiki".
---

# LLM Wiki — Lint Skill

Use this skill to check whether the wiki is internally consistent. A lint pass is a validation
step, not a search for criticism. Report only problems that can be demonstrated from files in
the wiki or from the documented schema.

## What to do

1. Read the wiki map (`wiki/index.md`), schema (`wiki/schema.md`), overview, log, and every page.
2. Record the page IDs that exist and every `[[page_id]]` link that appears.
3. Check only these objective conditions:
   - a wiki link points to a page that does not exist;
   - a page has malformed or missing required front matter;
   - a paper's `authors` field violates the documented author format;
   - a paper and an author page explicitly refer to each other by an ID that does not exist;
   - the index lists a page that does not exist, or omits a page when the schema requires indexing.
4. If the wiki has no pages of a type, say that the check was not applicable. Do not call an empty
   wiki broken.
5. Report results with two separate sections:
   - **Errors:** concrete, reproducible problems. Include the file and the exact field or link.
   - **Optional suggestions:** ideas such as adding more cross-links or sources. Include this
     section only when there is a clear reason, and never present it as a failure.

## Important limits

- Do not infer that a prose concept needs its own page. Mentioning a concept is not an error.
- Do not label a page an orphan unless the project schema explicitly requires inbound links.
- Do not call a claim stale or contradicted without two identifiable claims and evidence that one
  is newer. If that evidence is unavailable, do not report it.
- Do not invent missing pages, sources, authors, or fixes.
- Do not modify files during the check. Ask before applying a correction.

## Result format

If errors exist, list them by severity only when the schema defines severity. Otherwise use a plain
numbered list. If there are no errors, begin with:

> **Validation passed.** No objective errors were found in the checked wiki.

Then state what was checked and any optional suggestions separately. Do not suggest sources merely
to make the report longer.

## Local validation helper

When this repository is being checked, run `scripts/wiki_validation.py` if `wiki/` exists. It
validates the canonical author format used by the schema. It is a supporting check, not a reason to
report speculative issues.
