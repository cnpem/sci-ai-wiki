---
title: "Positional Encoding"
tags: [sequence_modeling, inductive_bias]
related_papers: [vaswani_attention_2017]
status: "developing"
---

# Positional Encoding

Positional encodings inject token-order information without recurrence or convolution. The original Transformer adds sinusoidal functions at geometrically increasing wavelengths to token embeddings. Learned positional embeddings performed nearly identically in the reported ablation [[vaswani_attention_2017]].
