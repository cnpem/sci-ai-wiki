---
title: "Residual Connections"
tags: [optimization, deep_learning]
related_papers: [vaswani_attention_2017]
status: "developing"
---

# Residual Connections

Residual connections add a learned transformation to an input through an additive shortcut. In ResNet, the basic form is `y = F(x) + x`; in the original Transformer, the corresponding sub-layer form is `LayerNorm(x + Sublayer(x))` [[he_deep_residual_2016]], [[vaswani_attention_2017]].

In [[he_deep_residual_2016]], identity shortcuts are hypothesized to make near-identity mappings easier to optimize and are supported by lower training error in deep residual CNNs than in matched plain CNNs. This is not evidence that shortcuts alone solve vanishing gradients: batch normalization, initialization, nonlinearities, optimizer, and data pipeline also matter. The Transformer uses the same broad pathway idea, but the ResNet paper directly demonstrates its empirical effect only in convolutional vision models.
