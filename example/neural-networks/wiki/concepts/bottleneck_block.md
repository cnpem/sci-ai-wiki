---
title: "ResNet Bottleneck Block"
tags: [resnet, convolutional_networks, efficiency]
related_papers: [he_deep_residual_2016]
status: "developing"
---

# ResNet Bottleneck Block

ImageNet ResNet-50/101/152 variants use a three-layer residual branch: 1×1 convolution to reduce channels, 3×3 convolution, then 1×1 convolution to restore channels. This increases depth while controlling computation relative to simply adding full-width convolutions [[he_deep_residual_2016]].
