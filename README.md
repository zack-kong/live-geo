# LIVE-GEO

A benchmark for evaluating Generative Engine Optimization (GEO) on the live web.

Existing GEO evaluations often supply rewritten text directly to an LLM or use
controlled retrieval pipelines. LIVE-GEO publishes rewritten product pages as
real, crawlable websites and asks web-connected AI systems to access and rank
them through supplied URLs.

**Paper:** [Do GEO Gains Survive the Live Web?](https://arxiv.org/abs/2611.01126) (arXiv:2611.01126)
**Site:** https://livegeobench.com/
**Code and round data:** https://github.com/zack-kong/live-geo (private during review)

## What we found

- Across 80 brands and 18 product families, three generative engines
  (ChatGPT, Gemini, Grok) agree on a top pick in **48.8–66.3%** of brands
  in the frozen-price product-URL comparisons.
- ChatGPT is sensitive to the order of candidate URLs: CORE scores
  **73.8%** Top-1 under one fixed order and **93.8%** under the reverse
  with equal prices.
- The JEV verifier flags 86 of 400 rewritten descriptions for potential numerical
  unfaithfulness, including all 80 produced by Statistics Addition.

These observations provide evidence complementary to direct-text evaluations.

## The catalogue

18 families · 80 categories · 80 brands · 480 listings.

Every brand and product is fictional, and the names are deliberately unusual
("Cryptoendolith-shield stone case", "Brine-mist fogponic rack") to reduce the
influence of prior brand familiarity. Each listing's price is assigned within
±0.2% of its brand's base price and then held fixed. Listing order is randomized
on each request to a brand page.

## Rounds

LIVE-GEO is meant to be re-run. Engines change, so observations are tied to their
collection dates and evaluation settings.

| Round | Date | Engines | Status |
|-------|------|---------|--------|
| 001 | October 2026 | ChatGPT, Gemini, Grok | Reported in the paper; private review release |
| 002 | TBD | TBD | Planned |

Round 001 includes five frozen +/-0.2% price conditions: ChatGPT and Grok with
brand-page URLs, and ChatGPT, Grok and Gemini with randomly ordered product URLs.
Each condition contains 80 final outputs, their settings and derived scores. Directories use `<model>-<price-condition>-<entry>`, for example
`chatgpt-random-price-url`, under both `raw/` and `scores/`.

## Reproducing

```bash
git clone https://github.com/zack-kong/live-geo.git
cd live-geo
pip install -r requirements.txt

# Re-score the released round from its saved outputs.
python analysis/reproduce_tables.py --round round_001_2026-10 --check
```

The repository is private during review; cloning requires collaborator access.

To run a new round:

1. Download the catalogue and choose the evaluator, price condition and URL entry
   point. Record the content version, model/mode, collection date and prompt.
2. Use the templates in `prompts/templates.md`. Save the supplied URL order for
   each brand; keep it unchanged when testing repeatability.
3. Save the final selected output and its settings for each brand in
   `rounds/round_002_YYYY-MM-DD/raw/<model>-<price-condition>-<entry>/`.
4. Calculate Top-1 rates and mean ranks from the included brand rankings. Save
   the scores and sample counts in the corresponding `scores/` directory.

The replay command covers these five round 001 conditions. The other findings
above are reported in the paper.

## Running your own method

1. Download the catalogue (`catalogue/index.json`).
2. Rewrite only the descriptions and reviews. Leave prices and category
   structure untouched.
3. Publish the rewritten listings at a reachable URL.
4. Ask a web-connected AI for the best product in each category using the
   templates in `prompts/templates.md`. Record the returned ranking, engine,
   settings, date and reported page access. Do not assign a rank to a missing
   response.

## Disclosure

CORE was developed by the same research team as LIVE-GEO. We evaluate it alongside
four other methods. Each method folder links its paper and official code and
explains our adaptations. Released rounds provide the model outputs used in their
reported statistics and scoring scripts so that the calculations can be checked
independently.

## Citation

```bibtex
@misc{kong2026geogainssurvivelive,
  title={Do GEO Gains Survive the Live Web? Evaluating In-the-Wild Visibility Gains of Generative Engine Optimization via LIVE-GEO},
  author={Runze Kong and Haibo Jin and Xucheng Yu and Xiaoqi Wang and Huimin Zeng and Haohan Wang},
  year={2026},
  eprint={2611.01126},
  archivePrefix={arXiv},
  primaryClass={cs.IR},
  url={https://arxiv.org/abs/2611.01126}
}
```

## License

Apache-2.0 for LIVE-GEO-authored code and documentation. Third-party materials
retain their applicable licenses; see `THIRD_PARTY_NOTICES.md`.
