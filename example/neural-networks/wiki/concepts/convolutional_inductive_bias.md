---
title: "Convolutional Inductive Bias"
tags: [cnn, locality, parameter_sharing, inductive_bias]
related_papers: [lecun_gradient_based_1998, he_deep_residual_2016]
status: "developing"
---

# Convolutional Inductive Bias

CNNs assume that local neighborhoods and repeated local patterns are useful. Local connectivity limits interactions to nearby regions, while shared filters reuse the same detector across spatial locations. These priors reduce parameters and support translation-related robustness [[lecun_gradient_based_1998]].

[[he_deep_residual_2016]] preserves this convolutional prior in ResNet. Its residual shortcuts address optimization through depth; they do not replace or remove convolutional locality and sharing.
