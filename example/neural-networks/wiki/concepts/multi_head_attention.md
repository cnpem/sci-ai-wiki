---
title: "Multi-Head Attention"
tags: [attention, representation_learning]
related_papers: [vaswani_attention_2017]
status: "developing"
---

# Multi-Head Attention

Multi-head attention runs several lower-dimensional attention functions in parallel and concatenates their outputs. The Transformer uses eight heads with `d_k=d_v=64` in the Base model. The paper reports that one head is 0.9 BLEU below the best setting and that too many heads can also reduce quality, showing a configuration-dependent trade-off rather than a universal optimum [[vaswani_attention_2017]].
