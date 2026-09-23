---
title: "Deep Residual Learning for Image Recognition"
authors: ["He, Kaiming", "Zhang, Xiangyu", "Ren, Shaoqing", "Sun, Jian"]
year: 2016
venue: "CVPR 2016"
doi: "10.1109/CVPR.2016.90"
arxiv: "1512.03385"
tags: [resnet, residual_learning, convolutional_networks, image_recognition, optimization]
status: "read"
relevance: high
architecture: "Plain and residual CNNs from 18 to 152 layers; bottleneck blocks for ResNet-50/101/152"
task: "Image classification, object detection, localization, and segmentation"
dataset: "ImageNet, CIFAR-10, PASCAL VOC, MS COCO"
benchmark: "ImageNet top-1/top-5 error; COCO and VOC detection mAP"
evaluation_metrics: [top_1_error, top_5_error, mAP]
training_setup: "SGD, momentum 0.9, weight decay 0.0001, batch size 256, batch normalization, scale augmentation"
compute_requirements: "Training schedules and FLOPs are reported; hardware is not fully specified in the main paper"
code_available: "Caffe-compatible implementation described"
main_findings: "Identity shortcut connections make substantially deeper CNNs easier to optimize and improve recognition accuracy relative to matched plain networks."
limitations: "The causal explanation is a hypothesis supported by experiments; evidence is primarily visual recognition, and extreme depth can still hurt generalization."
reproducibility_notes: "Results depend on augmentation, batch normalization, training schedule, test-time crops/scales, and shortcut projection choices."
---

# Deep Residual Learning for Image Recognition

## Contribution and optimization intuition

[[he_deep_residual_2016]] introduces a residual learning framework for very deep convolutional networks. A block learns `F(x)=H(x)-x` and produces `y=F(x)+x`. If the desired mapping is close to identity, the learned branch can approach zero while the shortcut supplies the identity path. This changes the parameterization and creates a direct route for information and gradients.

This is a plausible optimization explanation supported by lower training error in deep ResNets and smaller residual responses. It does not show that shortcuts alone eliminate vanishing or exploding gradients: the networks also use batch normalization, ReLU, initialization, SGD, and a specific training schedule.

## Architecture

Basic blocks use two 3×3 convolutions. Identity shortcuts are used when dimensions match; projection shortcuts using 1×1 convolutions handle dimension changes. ResNet-50, -101, and -152 use bottleneck blocks with 1×1, 3×3, and 1×1 convolutions.

## Experiments and results

Matched plain and residual networks show the central contrast. A 34-layer plain network has higher ImageNet training and validation error than an 18-layer plain network, despite containing the shallower solution space in principle. The 34-layer ResNet reverses this pattern. On ImageNet validation, ResNet-34 reaches 25.03% top-1 error versus 28.54% for plain-34. ResNet-50, -101, and -152 reach 20.74%, 19.87%, and 19.38% top-1 error in the reported comparison.

On CIFAR-10, the authors trained models over 100 layers and explored a 1202-layer network. The 1202-layer model optimized successfully but generalized worse than the 110-layer model, showing that optimization success and generalization are distinct.

## Evidence boundaries

The experiments establish that, under the reported CNN architectures and training procedures, identity shortcuts make increased depth easier to optimize and can improve visual recognition. They do not establish that residual connections solve vanishing gradients in general, that depth is always beneficial, or that the same mechanism transfers unchanged to Transformers or non-visual domains.

## Connection to the Transformer

Both [[resnet]] and [[transformer]] use additive residual pathways around learned transformations. In ResNet, the residual branch is convolutional and preserves spatial feature maps; in the original Transformer, the branch is attention or a position-wise feed-forward network and preserves sequence representations. This analogy is useful, but [[he_deep_residual_2016]] demonstrates the effect in CNN vision models, while [[vaswani_attention_2017]] demonstrates a complete residual-plus-attention architecture in machine translation. Neither paper isolates residual connections as the sole cause of its headline gains.

## Open questions

- Which benefits arise specifically from identity paths versus normalization and initialization?
- Why can very deep residual models optimize well yet generalize worse on small datasets?
- When do convolutional locality and residual depth outperform global attention?
