# Run new evaluations

Run commands from the repository root. Each output directory must be new.
Inputs include the six names, fixed prices, descriptions and all seven reviews.
`--seed` determines the saved candidate order. These are direct-text tasks;
the web-product templates remain in `prompts/templates.md`.

## API evaluation

Set `EVALUATOR_API_KEY` in your environment without putting it in a command or file.
Specify the model and full endpoint for your provider. The OpenAI-compatible route
supports providers offering the chat-completions schema; `--provider anthropic`
uses the Messages schema. Provider model support and billing are account-specific.

```bash
python eval/run_api.py --category actinic-shielded-print-cabinet --seed 0 --provider openai --endpoint https://api.openai.com/v1/chat/completions --model gpt-4o --output outputs/api-prepare
# After reviewing request.json and the provider's cost, run one request:
python eval/run_api.py --category actinic-shielded-print-cabinet --seed 0 --provider openai --endpoint https://api.openai.com/v1/chat/completions --model gpt-4o --output outputs/api/actinic-shielded-print-cabinet --execute
```

For Claude, use `--provider anthropic --endpoint https://api.anthropic.com/v1/messages`
and the model identifier available to your account. The runner saves the exact
request and raw response; malformed rankings remain invalid. It makes no automatic
retries. `direct_text.py` remains available for parsing previously saved responses.

## Local Qwen evaluation

Install the optional dependencies and download the model once, subject to its
[model license](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct).

```bash
pip install -r requirements-local.txt
pip install huggingface_hub
hf download Qwen/Qwen2.5-3B-Instruct
python eval/run_qwen.py --category actinic-shielded-print-cabinet --seed 0 --device cuda --output outputs/qwen/actinic-shielded-print-cabinet --execute
```

Use `--device cpu` when no CUDA device is available. Model loading uses the local
cache only. Set `--revision` to a model commit to pin weights. The saved response
records the resolved revision, token counts and generated text. Decoding is greedy;
inputs exceeding the context window are rejected rather than truncated.
`local_evaluator.py` also supports BM25 and parsing saved Qwen ID rankings.

## Collect and score a round

Run one command per category from `catalogue/index.json`, with one parent output
directory per model/price/entry condition. Keep the generated `input.json`,
`settings.json`, `request.json` when applicable, `response.json` and `result.json`.
Select at most one complete output per brand for the final condition.

```bash
python eval/score_new.py outputs/qwen --output outputs/qwen-summary.csv
python -m unittest discover -s eval -p "test_*.py"
```

The scorer reports the number of complete brands; invalid or absent rankings
do not enter its denominator. Put selected outputs and settings in the new
`rounds/round_.../raw/<model>-<price-condition>-<entry>/` directory and its CSV
in `scores/`. Historical round 001 records remain unchanged. The existing
`analysis/reproduce_tables.py --check` verifies the frozen round 001 release.

For optional description checks, see [JEV](jev/README.md).
