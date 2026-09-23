---
title: "Identity Mapping in Residual Networks"
tags: [residual_learning, optimization]
related_papers: [he_deep_residual_2016]
status: "developing"
---

# Identity Mapping

An identity shortcut passes `x` directly to a block’s output, allowing the learned residual branch to approach zero when the desired transformation is close to identity. This is the central optimization intuition of [[he_deep_residual_2016]], not a claim that all deep-network optimization reduces to identity learning.
