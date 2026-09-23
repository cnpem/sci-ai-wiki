---
title: "Transformer"
authors: ["vaswani_ashish", "shazeer_noam", "parmar_niki", "uszkoreit_jakob"]
year: 2017
paper: "vaswani_attention_2017"
tags: [attention, sequence_to_sequence, encoder_decoder]
---

# Transformer

## Overview

The Transformer is an encoder–decoder sequence model based on self-attention rather than recurrence or convolution. The original configuration uses six encoder layers, six decoder layers, model width 512, feed-forward width 2048, and eight heads of dimension 64.

## Architecture

Each encoder layer contains multi-head self-attention and a position-wise feed-forward network. Each decoder layer adds encoder–decoder attention and masks future target positions. Every sub-layer is wrapped with a residual pathway and layer normalization. Token embeddings are combined with sinusoidal positional encodings.

## Inductive bias and trade-offs

The model has a global relational bias: any position can attend to any other position in one layer. It lacks the strong locality and translation-equivariance built into standard CNNs, and its full attention costs `O(n²d)` per layer. In exchange, training positions can be processed in parallel and long-range paths are constant length in the dense-attention formulation. These properties make it a central comparison point for [[cnn]], [[residual_network]], and later attention architectures.

## Benchmarks and limitations

[[vaswani_attention_2017]] reports 28.4 BLEU on WMT14 English–German and 41.0 BLEU on WMT14 English–French for Transformer Big. The original evidence does not establish universal superiority, domain transfer, explanation faithfulness, or favorable scaling for arbitrarily long inputs.
