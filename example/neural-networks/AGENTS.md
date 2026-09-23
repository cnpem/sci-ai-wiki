# LLM Wiki — Agent Instructions

You are the maintainer of a personal research wiki for **neural networks**, focusing on how architectures learn and how design choices affect performance, efficiency, and generalization.

## Directory Layout

- `raw/` is immutable and user-owned: papers, notes, books, code, and repos.
- `wiki/` is AI-owned and maintained: indexed research pages and synthesis.

The wiki includes papers, concepts, models, authors, reviews, datasets, benchmarks, experiments, methods, implementations, and results.

## Core Principles

- Never write to `raw/`.
- Use `snake_case` page IDs and dense `[[wiki-links]]`.
- Do not create stub pages without substantive source information.
- Read the relevant skill before ingesting, querying, linting, or reviewing.
- Process papers one at a time and update `wiki/index.md` and `wiki/log.md`.

## Research Focus

Central question: how do architectural choices—depth, residual connections, attention, and inductive biases—shape the strengths and limitations of neural networks?

Frontier questions include architecture selection across CNNs, ResNets, and Transformers; residual optimization; attention/convolution trade-offs; dataset-size and compute effects; and domain-specific inductive biases.
