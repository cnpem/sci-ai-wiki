---
title: "Self-Attention"
tags: [attention, sequence_modeling]
related_papers: [vaswani_attention_2017]
status: "developing"
---

# Self-Attention

Self-attention computes each position’s representation by weighting values from positions in the same sequence using query–key compatibility. The dense formulation has `O(n²d)` per-layer complexity, constant sequential depth, and constant maximum path length between positions [[vaswani_attention_2017]]. It favors global dependencies and parallel training, but can be expensive for long sequences and supplies less locality than a CNN.
