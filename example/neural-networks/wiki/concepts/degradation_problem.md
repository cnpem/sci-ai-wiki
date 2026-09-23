---
title: "Degradation Problem in Deep Networks"
tags: [optimization, depth, residual_learning]
related_papers: [he_deep_residual_2016]
status: "developing"
---

# Degradation Problem

In the paper, increasing the depth of a plain CNN eventually increases training error, not merely test error. A deeper model should contain a solution equivalent to a shallower model, yet the solver fails to find it reliably. Residual parameterization substantially reduces this degradation in the reported vision experiments [[he_deep_residual_2016]].
