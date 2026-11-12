# Frozen catalogue

`index.json` enumerates 80 fictional brands across 18 product families.
`listings/<category_id>/<method>.json` contains 480 listings: Original and five
GEO rewrites per brand. Each contains a description and seven reviews.

The listings are extracted from `approved80-20261105-v1`.
Description/review HTML fragments preserve the rendered structure; plain text is
also provided. A source-page SHA256 is recorded for each listing. Reviewer IDs,
ratings, dates and fictional author names retain the Original record's identity.

Displayed prices are the frozen +/-0.2% prices of that snapshot. Saved experiment
inputs contain the prices used for each equal-price or varied-price condition.
The index lists the files; recorded prompts preserve experimental candidate order.
Numerical-faithfulness decisions are stored separately from these listing exports.
