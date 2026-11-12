# CORE

## Evaluated method

Ranking-feedback optimization of an appended reasoning/review-based addition.

- Paper: [Controlling Output Rankings in LLM-Based Search via Generative Engine Optimization](https://arxiv.org/abs/2602.03608)
- Official code: [https://github.com/haibojin001/AmazonCOREBench](https://github.com/haibojin001/AmazonCOREBench)

## LIVE-GEO adaptation

We retained the author ranking-feedback and suffix-optimization functions.
GPT-3.5 Turbo generated the initial suffix; GPT-4o ranked candidates and optimized
subsequent suffixes. Each suffix also guided rewriting of all seven reviews, and
both descriptions and reviews were supplied to the local ranker. A later adaptive
phase used browser rankings for non-winning CORE listings to revise their text.
Texts were then frozen for evaluation. Optimization feedback and final evaluation
records are stored separately.

Author code version recorded for the initial pilot:
[`71c5165`](https://github.com/haibojin001/AmazonCOREBench/tree/71c5165879ba39db1fe952ee21f7cf270390be54).
