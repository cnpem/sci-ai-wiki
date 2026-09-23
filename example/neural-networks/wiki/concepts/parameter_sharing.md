---
title: "Parameter Sharing in CNNs"
tags: [cnn, efficiency, inductive_bias]
related_papers: [lecun_gradient_based_1998]
status: "developing"
---

# Parameter Sharing

In a CNN, the same learned filter is applied at multiple spatial locations. This reduces parameter count and encodes the assumption that a useful local feature can recur across an image. The paper presents sharing as a central reason CNNs are appropriate for two-dimensional document patterns [[lecun_gradient_based_1998]].
