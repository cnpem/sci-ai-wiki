---
title: "Gradient-Based Learning Applied to Document Recognition"
authors: ["LeCun, Yann", "Bottou, Léon", "Bengio, Yoshua", "Haffner, Patrick"]
year: 1998
venue: "Proceedings of the IEEE"
doi: "10.1109/5.726791"
arxiv: ""
tags: [cnn, lenet_5, document_recognition, gradient_based_learning, ocr]
status: "read"
relevance: high
architecture: "Convolutional neural networks, including LeNet-5; Graph Transformer Networks for document systems"
task: "Handwritten character recognition and document recognition"
dataset: "Handwritten digit/character recognition datasets and bank-check recognition data"
benchmark: "Historical digit-recognition comparisons and commercial check-reading systems"
evaluation_metrics: [error_rate, recognition_accuracy]
training_setup: "Gradient-based backpropagation; task-specific preprocessing and system pipelines"
compute_requirements: "Historical workstation and production-system settings; not directly comparable to modern training reports"
code_available: "Not identified in the paper"
main_findings: "Carefully designed CNNs can learn feature extraction and classification jointly, reducing dependence on hand-crafted representations for document recognition."
limitations: "Evidence and metrics come from historical recognition settings; system details and dataset protocols do not map directly to modern benchmarks."
reproducibility_notes: "Treat reported systems as historical case studies; preserve preprocessing, segmentation, module boundaries, and evaluation protocol when reconstructing them."
---

# Gradient-Based Learning Applied to Document Recognition

## Contribution

[[lecun_gradient_based_1998]] argues that document-recognition systems should learn more of their feature extraction rather than rely on manually designed pipelines. The paper surveys gradient-based learning and presents convolutional neural networks as a way to handle two-dimensional shape variability through local connectivity, shared weights, and subsampling.

## CNNs and LeNet-5

The central architecture thread is the CNN: successive layers combine local receptive fields, spatially shared filters, nonlinearities, and spatial reduction into increasingly abstract feature maps. Weight sharing builds a translation-related prior and sharply reduces parameters compared with fully connected image networks. Subsampling improves tolerance to small local shifts while reducing spatial resolution.

LeNet-5 is presented as a concrete handwritten-character recognition system. Its learned feature extractor and classifier are trained together with backpropagation, making the representation task-dependent rather than a fixed front end. This makes LeNet-5 a historical foundation for comparing CNNs with later architectures such as [[resnet]] and [[transformer]].

## Connection to ResNet

This paper’s principal architectural prior is convolutional locality and parameter sharing: the network assumes that nearby pixels and repeated local patterns are useful. [[he_deep_residual_2016]] retains these CNN priors while changing the optimization parameterization by adding residual shortcuts. Convolutional inductive bias and residual connections should therefore be analyzed separately: one constrains how features are computed, while the other provides an optimization and information pathway through depth.

## Secondary application: Graph Transformer Networks

The paper also describes Graph Transformer Networks (GTNs) for integrating tasks such as field extraction, segmentation, recognition, and language modeling in document systems. GTNs are historically important as an example of differentiable, trainable system-level composition, but they are not treated here as a peer architectural branch to CNNs in the CNN–ResNet–Transformer comparison.

## Historical evidence and limits

The paper reports successful handwritten recognition and commercial bank-check reading systems. These results support the feasibility of learned feature extraction in their historical settings. They are not directly comparable to current ImageNet, CIFAR, or Transformer benchmarks because data, preprocessing, error definitions, compute, and evaluation protocols differ substantially.

## Open questions

- Which convolutional priors remain useful when data and compute are large enough to learn broader relationships?
- How much of CNN performance comes from locality and sharing versus optimization and regularization?
- When should a CNN’s spatial hierarchy be replaced or augmented by global attention?
