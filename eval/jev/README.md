# JEV: numerical-faithfulness verification

JEV checks numerical claims in rewritten descriptions against the fixed product
specifications. It flags conflicting values and unsupported quantities. Users can
consult these flags and optionally move flagged listings after unflagged listings,
preserving the order within each group.

Upload validation is a separate website function. It checks JSON structure,
catalogue coverage, review identifiers and security requirements.

`verify.py` calls the hosted JEV service or parses a saved response. `policy.txt`
preserves the numerical policy used in the published80 experiment. The default
model is `jev-1.13.0`; a description is flagged when its FLAG probability is at
least 0.95. This is an advisory prediction, not a human-confirmed error.

Run from the repository root:

```bash
# Prepare and inspect the request without an API call.
python eval/jev/verify.py catalogue/listings/actinic-shielded-print-cabinet/core.json --output outputs/jev-prepare
# Set TYPESAFE_API_KEY in your environment; this call may incur provider charges.
python eval/jev/verify.py catalogue/listings/actinic-shielded-print-cabinet/core.json --output outputs/jev-run --execute
# Alternatively parse a previously saved response, without sending a request.
python eval/jev/verify.py catalogue/listings/actinic-shielded-print-cabinet/core.json --response outputs/jev-run/response.json --output outputs/jev-replay
```

The tool saves the request, settings, full response and advisory result in the
chosen directory. It checks descriptions only; comments and non-numeric claims
are outside this policy. Invalid or unavailable responses do not become NO_FLAG.
The service endpoint and response schema follow the
[official TypeSafe Choice API](https://docs.typesafe.ai/primitives/choice).
Model availability depends on the provider. No JEV weights are redistributed.

Keep generated flags and human-review materials separate from crawlable product
pages. Automated email delivery remains a separately configured website service.
