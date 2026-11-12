# Round 001: frozen-price web evaluations

This round packages five reported conditions on the same 80-brand catalogue.
Prices are assigned within +/-0.2% of each brand's base price and remain fixed.

| Condition | Entry point | Brands |
|---|---|---:|
| ChatGPT | Six locally shuffled product URLs | 80 |
| ChatGPT | Brand-page URL with server-randomized listing order | 80 |
| Grok | Six locally shuffled product URLs | 80 |
| Grok | Brand-page URL with server-randomized listing order | 80 |
| Gemini | Six locally shuffled product URLs | 80 |

The catalogue is in `catalogue/` at the repository root. `raw/`
contains one directory per condition, with 80 brand files and `settings.json`.
Names follow `<model>-random-price-<entry>`, where `url` means supplied product
URLs and `brand` means a brand-page URL. For example: `chatgpt-random-price-url`.
Matching directories in `scores/` contain individual rankings and
strategy summaries. `scores/summary.csv` combines the five conditions;
`scores/agreement_descriptive.csv` compares their rankings on shared brands.

Each brand file contains the selected model output, its prompt and candidate
identities, prices, available recorded settings and parsed ranks. Product-URL
files also save the exact supplied URL sequence. Condition settings distinguish
requested model/mode settings from the evidence captured in each observation.

There are 381 structured responses and 19 extracted complete ranking arrays.
The latter are ChatGPT product-URL observations whose remaining JSON was not
fully captured. Reading-log fields retain the model's self-report. Three
user-supplied ChatGPT product-URL outputs have unverified settings; four
user-supplied ChatGPT brand-URL outputs have user-confirmed settings.

Brand-page order is randomized in server-rendered responses for the brand-URL
conditions. Product-URL order is the locally shuffled sequence in the saved
prompt. These are distinct mechanisms; the product-URL records do not establish
per-request shuffling on their historical destination pages.

The directory date refers to the October 2026 experiments. The packaged catalogue
snapshot was published later as `approved80-20261105-v1`. Original experiment URLs
are retained in the prompts. Comparisons across collection dates and entry
protocols are descriptive.

Run `python analysis/reproduce_tables.py --round round_001_2026-10 --check` from
the repository root to validate all selected outputs, hashes, catalogue prices
and frozen reference scores, then regenerate the CSVs. No model calls are made.
