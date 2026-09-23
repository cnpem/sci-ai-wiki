---
title: "Scaled Dot-Product Attention"
tags: [attention, method]
related_papers: [vaswani_attention_2017]
---

# Scaled Dot-Product Attention

The method computes `softmax(QKᵀ/√d_k)V`. Scaling prevents large dot products from pushing the softmax into very small-gradient regions and supports efficient matrix multiplication [[vaswani_attention_2017]].
