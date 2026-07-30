## SciAI Wiki - Scientific Artificial Intelligence Wikis

_This is the repository for the article "Beyond Retrieval: Compounding Scientific Extelligence with Artificial Intelligence Wikis" ([arXiv (May 18th)](https://github.com/cnpem/sci-ai-wiki/blob/main/docs/arxiv_manuscript_SciAIwiki.pdf), 2026) by Luiz Lopes, Pedro Zanineli, Bruno Focassio, and Gabriel R. Schleder._

SciAI Wiki is a framework for building persistent scientific memory with Large Language Models, building on [Karpathy's LLM Wiki discussions](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Instead of treating papers, notes, and research questions as isolated chat sessions, it organises scientific context into human-readable markdown pages (as a wiki) that preserve provenance, relationships, and accumulated reasoning over time.

The present repository acts as a structured knowledge substrate for AI-assisted research. Agents can ingest sources, link concepts, answer questions from the accumulated context, audit the knowledge graph, and generate literature syntheses, while researchers remain in control of interpretation, validation, and research direction.

## A beginner-friendly workflow

An **IDE** (integrated development environment) is an application where you can view project files,
edit them, search, and run commands in one place. This project uses **Antigravity** as its IDE and
agentic workspace. Antigravity lets you work with an AI agent alongside the files: ask it to ingest
a paper, explain a page, check the wiki, or make a small documentation change, then review what it
proposes before accepting it.

An **agent** is a software assistant that follows instructions and can perform a task in the
project, such as reading a paper and creating linked wiki pages. The skills in `.agents/skills/`
are those instructions. They guide the agent, but you remain responsible for checking important
claims against the original source.

The wiki is written in **Markdown**, a simple way to format plain text. For example, `# Title`
creates a heading, `- item` creates a list item, and `[[page_id]]` is this project's convention for
linking to another wiki page. You do not need programming experience to contribute: open a `.md`
file in Antigravity, edit the words directly, and save it. You can also add a PDF or note to
`raw/papers/` or `raw/notes/` and ask the agent to ingest it. Keep original files in `raw/`, check
the generated pages, and ask for a health check when something looks inconsistent.

Prepare the local validation tools from any directory with:

```bash
/path/to/sci-ai-wiki/scripts/install_dependencies.sh
```

The script finds the project from its own location, creates `.venv` only when needed, and installs
PyYAML only when it is missing. Activate the environment before running Python commands:

```bash
source .venv/bin/activate
```

## Front matter

**Front matter** is the small YAML block at the very top of a Markdown page. It appears before the
first heading, between two lines containing only `---`. It gives the agent searchable information
without hiding the readable notes below it.

For a paper page, these fields are required:

```yaml
---
title: "A full paper title"
authors: [Ada Lovelace, Alan Turing]
year: 1843
---
```

`title` is the page's readable title, `authors` is a non-empty list of full names, and `year` is
the publication year. Write names as `Given names Family name`; use one list item per author. The
same format is used for an author page's required `name` field. `affiliation` and `website` are
optional. Other page types may define different required fields in `wiki/schema.md`.

Common mistakes are putting text before the opening `---`, forgetting the closing `---`, writing
`authors: Ada Lovelace` instead of a list, using `Lovelace, Ada` or an author ID in a paper's
`authors` list, and leaving required values blank. When in doubt, copy a valid example and ask the
agent to validate the page.

## Skills

This wiki is designed around specialised agent skills: persistent operational routines that help ingest, organise, query, and maintain scientific knowledge without changing the underlying model. In this setup, skills act as human-guided procedures for turning papers and research notes into a coherent, linked memory system.

- **Ingestion** is the controlled entry point for new sources. The agent extracts the source, performs an initial reading, asks the researcher clarifying questions, and then writes interconnected paper, concept, model, and author pages with preserved provenance.
- **Query** turns the wiki into a reasoning workspace. The agent answers research questions by navigating accumulated context, synthesising cited evidence, surfacing contradictions, and identifying gaps that may become new persistent pages.
- **Lint** is the maintenance layer. It checks demonstrable errors such as broken links and invalid required metadata, clearly reports when validation passes, and keeps optional suggestions separate.
- **Review** supports literature synthesis. It builds structured narrative reviews from the ingested wiki context, connecting foundational work, current methods, disagreements, and open problems into manuscript-ready outlines or sections.

## SciAI Wiki overview:
<img width="1920" alt="SciAI wiki overview" src="https://github.com/user-attachments/assets/43d8c92a-0986-4bdb-b3dc-8b62460dac3b" />

#### SciAI Wiki minimal implementation stylized example (_this repository_):
<img width="600" alt="SciAI wiki minimal implementation example" src="https://github.com/user-attachments/assets/7eb920a2-c31a-40fd-acdf-1d5847a57340" />
