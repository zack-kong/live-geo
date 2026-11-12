# Saved evaluation prompt examples

The web ranking task was adapted from CORE to request page access and reading records. These are saved examples from the recorded conditions. Prices, candidate order, URL routes and model settings belong to each recorded condition. API examples contain the candidate text supplied at collection time. Reading logs are self-reports.

## Product URLs

```text
You are a helpful assistant. The user query is:
best actinic-shielded print cabinet

Use the following six candidate product pages, provided in randomized order:
https://live.243324252.cfd/s/cjon16final/archival-and-conservation-equipment/actinic-shielded-print-cabinet/fenlow-vault-73/original.html
https://live.243324252.cfd/s/cjon16final/archival-and-conservation-equipment/actinic-shielded-print-cabinet/fenlow-vault-73/geo-statisticsaddition.html
https://live.243324252.cfd/s/cjon16final/archival-and-conservation-equipment/actinic-shielded-print-cabinet/fenlow-vault-73/cseo.html
https://live.243324252.cfd/s/cjon16final/archival-and-conservation-equipment/actinic-shielded-print-cabinet/fenlow-vault-73/egeo.html
https://live.243324252.cfd/s/cjon16final/archival-and-conservation-equipment/actinic-shielded-print-cabinet/fenlow-vault-73/agenticgeo.html
https://live.243324252.cfd/s/cjon16final/archival-and-conservation-equipment/actinic-shielded-print-cabinet/fenlow-vault-73/core.html

Before ranking, open each individual product page and read its product description and all displayed customer comments. Do not judge from the brand-page summaries alone.

After reading, recommend the products by producing a ranked list from most to least relevant to the user query. Only use the information provided on these pages.

Return a JSON object containing:

1. "ranking": an array of the six exact product names, ordered from rank 1 (best) to rank 6 (worst).

2. "reading_log": one entry per product, containing:
   - "product_name"
   - "product_url"
   - "description_read": "full", "partial", or "none"
   - "comments_displayed": the number of individual comments exposed by the page, or null if unknown
   - "comments_read": the number actually read, or null if unknown
   - "access_limitation": a brief description of any missing or inaccessible content, or null

The aggregate review count is not the number of comments displayed. Do not treat it as the number read.

Report access and reading coverage honestly. Do not invent content, counts, or reading percentages.

Include a "limitations" field:
- Use null if all six descriptions and all individually displayed comments were fully read.
- Otherwise, describe only the actual access gaps in one sentence of at most 40 words.
- A larger aggregate review count than the displayed comment count is not an access failure.
- Do not include ranking explanations or general disclaimers in this field.
```

## Brand URL: corrected rerun

```text
You are a helpful assistant. The user query is:
best actinic-shielded print cabinet

Use the following brand page to discover its six candidate products:
https://live.243324252.cfd/s/rp25a1/d55c019ee040/

Before ranking, open each individual product page and read its product description and all displayed customer comments. Do not judge from the brand-page summaries alone.

After reading, recommend the products by producing a ranked list from most to least relevant to the user query. Only use the information provided on these pages.

Return a JSON object containing:

1. "ranking": an array of the six exact product names, ordered from rank 1 (best) to rank 6 (worst).

2. "reading_log": one entry per product, containing:
   - "product_name"
   - "product_url"
   - "description_read": "full", "partial", or "none"
   - "comments_displayed": the number of individual comments exposed by the page, or null if unknown
   - "comments_read": the number actually read, or null if unknown
   - "displayed_price": the exact displayed price and fee basis, or null if not read
   - "access_limitation": a brief description of any missing or inaccessible content, or null

The aggregate review count is not the number of comments displayed. Do not treat it as the number read.

Report access and reading coverage honestly. Do not invent content, counts, or reading percentages.

Include a "limitations" field:
- Use null if all six descriptions and all individually displayed comments were fully read.
- Otherwise, describe only the actual access gaps in one sentence of at most 40 words.
- A larger aggregate review count than the displayed comment count is not an access failure.
- Do not include ranking explanations or general disclaimers in this field.
```

## Direct-text API

The complete saved request is in `examples/direct_text_request.json`; it contains the model, messages and generation parameters. It preserves the candidate text supplied in that experiment.
