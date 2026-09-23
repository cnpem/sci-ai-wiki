---
title: "Residual Network (ResNet)"
authors: ["he_kaiming", "zhang_xiangyu", "ren_shaoqing", "sun_jian"]
year: 2016
paper: "he_deep_residual_2016"
tags: [cnn, residual_learning, image_recognition]
depths: [18, 34, 50, 101, 152]
---

# Residual Network (ResNet)

ResNet is a convolutional architecture built from blocks that learn residual functions and add them to shortcut-transformed inputs. Basic blocks use two 3×3 convolutions; bottleneck blocks use 1×1, 3×3, and 1×1 convolutions.

[[he_deep_residual_2016]] shows that this parameterization supports deeper CNNs than comparable plain stacks. A 1202-layer CIFAR-10 model optimized successfully but generalized worse than a 110-layer model, limiting any claim that more depth is automatically better.

ResNet and [[transformer]] share additive residual pathways, but ResNet’s learned transformations are convolutional and spatially local, whereas the Transformer’s are attention-based and sequence-global. The original evidence for each is task-specific.
