# Wiki Schema Reference

All wiki pages must include YAML frontmatter.

## Paper Page

```yaml
---
title: "Full paper title"
authors: []
year: YYYY
venue: ""
doi: ""
arxiv: ""
tags: []
status: "read"
relevance: high
architecture: ""
task: ""
dataset: ""
benchmark: ""
evaluation_metrics: []
training_setup: ""
compute_requirements: ""
code_available: ""
main_findings: ""
limitations: ""
reproducibility_notes: ""
---
```

Concepts use `title`, `tags`, `related_papers`, and `status`. Models use `title`, `authors`, `year`, `paper`, and `tags`. Authors use `name`, `affiliation`, `website`, and `papers`. Reviews use `title`, `topic`, `scope`, `audience`, `date`, `sources_wiki`, and `sources_web`.
