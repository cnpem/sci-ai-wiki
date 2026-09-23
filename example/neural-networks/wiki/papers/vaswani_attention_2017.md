---
title: "Attention Is All You Need"
authors: ["Vaswani, Ashish", "Shazeer, Noam", "Parmar, Niki", "Uszkoreit, Jakob", "Jones, Llion", "Gomez, Aidan N.", "Kaiser, Łukasz", "Polosukhin, Illia"]
year: 2017
venue: "NeurIPS 2017"
doi: ""
arxiv: "1706.03762"
tags: [transformer, attention, sequence_to_sequence, machine_translation, architecture]
status: "read"
relevance: high
architecture: "6-layer encoder and 6-layer decoder Transformer; d_model=512, d_ff=2048, 8 attention heads"
task: "Neural machine translation"
dataset: "WMT 2014 English-German and English-French"
benchmark: "newstest2014 BLEU"
evaluation_metrics: [BLEU, perplexity]
training_setup: "Adam; 4000-step warmup; dropout; label smoothing; BPE/word-piece tokenization"
compute_requirements: "8 NVIDIA P100 GPUs; Base 12 hours/100K steps; Big 3.5 days/300K steps"
code_available: "Tensor2Tensor repository"
main_findings: "Attention-only sequence transduction can outperform recurrent and convolutional baselines while training more parallelly."
limitations: "Evidence is centered on machine translation; full self-attention has O(n^2 d) per-layer complexity; decoder generation remains autoregressive."
reproducibility_notes: "The paper reports detailed configurations, schedules, datasets, and ablations, but hardware and software versions are limited by 2017 reporting conventions."
---

# Attention Is All You Need

## Abstracted contribution

[[vaswani_attention_2017]] introduces the Transformer, an encoder–decoder architecture that replaces sequence-aligned recurrence and convolution with stacked [[multi_head_attention]] and position-wise feed-forward layers. The paper’s original claim is specific: on WMT 2014 translation, this design improves quality and reduces training time through parallel computation and short dependency paths.

## Method

Scaled dot-product attention is:

`Attention(Q,K,V) = softmax(QKᵀ / √d_k)V`.

[[multi_head_attention]] projects queries, keys, and values into multiple subspaces, computes attention in parallel, concatenates the outputs, and projects them back. The encoder and decoder use residual connections followed by layer normalization. Since there is no recurrence or convolution, sinusoidal [[positional_encoding]] is added to token embeddings.

The decoder masks future positions, preserving autoregressive generation. Each layer also includes a position-wise feed-forward network with `d_model=512` and `d_ff=2048` in the Base configuration.

## Demonstrated results

On WMT 2014, Transformer Big reaches 28.4 BLEU for English–German and 41.0 BLEU for English–French. The paper reports 8 P100 GPUs, 3.5 days of training for the Big model, and lower estimated training cost than the compared systems. Ablations show sensitivity to attention-head count, key dimension, model width/depth, dropout, and positional encoding choices.

These results directly establish the architecture’s effectiveness for the evaluated translation tasks. They do not, by themselves, establish superiority for vision, speech, scientific data, or all sequence lengths.

## Architecture comparison and inductive bias

Relative to recurrent models, the Transformer removes sequential state updates and gives every position a direct path to every other position. Relative to CNNs, it does not impose a local receptive field or translation-equivariant weight sharing; locality and relationships must be learned through attention and data. This creates a different inductive-bias and scaling trade-off: global interaction and parallel training at the cost of quadratic attention complexity in sequence length and weaker built-in locality.

[[residual_connections]] and [[layer_normalization]] are important optimization components, not evidence that attention alone explains the result. The paper compares complete architectures, training recipes, and compute regimes rather than isolating every design choice causally.

## Skeptical reading

The appendix shows heads with patterns that appear syntactic or semantic, but this is observational evidence. Attention weights should not automatically be treated as faithful explanations of a model’s decisions; that claim requires separate causal or faithfulness tests and is not demonstrated here.

Likewise, the paper proposes extending attention to images, audio, and video, but does not evaluate those domains. Transfer to other domains is therefore an open question in this source, not an established result.

## Open questions

- When does learned global interaction outweigh CNN-like locality and equivariance?
- How should attention be restricted for very long inputs without losing useful paths?
- How do dataset size and compute budget determine whether the Transformer’s weaker prior is beneficial?
- Which parts of the result come from attention, and which come from residual pathways, normalization, scale, regularization, or training schedule?

## Connections

See [[transformer]], [[self_attention]], [[multi_head_attention]], [[positional_encoding]], [[residual_connections]], [[layer_normalization]], [[wmt_2014]], and [[machine_translation_bleu]].
