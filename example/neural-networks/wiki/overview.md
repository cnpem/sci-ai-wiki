# Research Overview

*Last updated: 2026-09-23*

## Thesis Statement

How do architectural choices—such as depth, residual connections, attention, and inductive biases—shape the strengths and limitations of neural networks?

## Frontier Questions

1. When are CNNs, ResNets, and Transformers most appropriate?
2. How do residual connections help optimization in deep networks?
3. What trade-offs exist between attention-based models and convolutional models?
4. How do dataset size and compute budget affect architecture choice?
5. Which inductive biases help models generalize in different domains?

## Current Position

The wiki currently contains 3 ingested sources. [[lecun_gradient_based_1998]] establishes the CNN baseline: locality and parameter sharing are architectural priors for visual patterns, while joint feature learning replaces much hand-designed extraction. [[he_deep_residual_2016]] adds residual parameterization for optimization through depth, and [[vaswani_attention_2017]] adds global attention and parallel sequence processing.

## Key Tensions

[[lecun_gradient_based_1998]], [[he_deep_residual_2016]], and [[vaswani_attention_2017]] suggest that architecture choice combines inductive bias and optimization mechanism. CNN locality/sharing, residual pathways, and global attention solve different problems. The 1998 results are historical document-recognition evidence, the ResNet results are convolutional vision evidence, and the Transformer results are translation evidence; none establishes universal superiority.

## What Would Falsify the Thesis

The thesis would need revision if controlled comparisons showed that locality, parameter sharing, residual pathways, or attention provide no task-dependent advantages after matching compute, optimization recipe, parameter count, data scale, and evaluation protocol.
