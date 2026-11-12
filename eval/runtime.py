"""Shared input and output handling for new, direct-text evaluations."""
import argparse
import hashlib
import json
import os
import random
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def save(path, value):
    with Path(path).open('x', encoding='utf8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)


def prepare(category, seed=0, catalogue=ROOT):
    catalogue = Path(catalogue)
    entries = read(catalogue / 'catalogue/index.json')
    entry = next((x for x in entries if x['category_id'] == category), None)
    if entry is None:
        raise ValueError('Unknown category: ' + category)
    listings = [read(catalogue / p) for p in entry['listings']]
    if len(listings) != 6 or len({x['name'] for x in listings}) != 6:
        raise ValueError('Expected six distinct listings')
    random.Random(seed).shuffle(listings)
    blocks = []
    for item in listings:
        reviews = '\n'.join(f"{r['title']} ({r['rating']}/5): {r['text']}" for r in item['reviews'])
        blocks.append(f"{item['name']}\nPrice: {item['price_display']}\n"
                      f"{item['description']}\nReviews:\n{reviews}")
    query = 'best ' + entry['name']
    prompt = (f'For the query "{query}", rank the six product listings below from best to worst.\n\n'
              + '\n\n'.join(blocks)
              + '\n\nReturn only a JSON array of the six exact product names in rank order, best first.')
    return {'category_id': category, 'query': query, 'seed': seed,
            'input_order': [x['name'] for x in listings],
            'name_to_method': {x['name']: x['method'] for x in listings},
            'listings': listings, 'prompt': prompt,
            'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest()}


def parse_ranking(text, names):
    """Reject incomplete, duplicated, or conflicting ranking arrays."""
    arrays = []
    for i, character in enumerate(text):
        if character != '[':
            continue
        try:
            value, _ = json.JSONDecoder().raw_decode(text[i:])
        except ValueError:
            continue
        if isinstance(value, list):
            arrays.append(value)
    if not arrays or any(x != arrays[0] for x in arrays):
        return None
    values = arrays[0]
    if len(values) != 6 or not all(isinstance(x, str) for x in values):
        return None
    return values if len(set(values)) == 6 and set(values) == set(names) else None


def record(packet, ranking, evaluator):
    return {'category_id': packet['category_id'], 'evaluator': evaluator,
            'captured_utc': datetime.now(timezone.utc).isoformat(),
            'status': 'complete' if ranking is not None else 'invalid',
            'input_order': packet['input_order'], 'name_to_method': packet['name_to_method'],
            'model_output': {'ranking': ranking},
            'ranks': ({packet['name_to_method'][name]: i for i, name in enumerate(ranking, 1)}
                      if ranking is not None else None)}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('API redirects are not followed')


def post(endpoint, body, key_env, provider='openai', timeout=120):
    url = urlsplit(endpoint)
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query:
        raise ValueError('Use an HTTPS API endpoint without credentials or query parameters')
    key = os.environ.get(key_env)
    if not key:
        raise ValueError('Set credential environment variable ' + key_env)
    headers = {'Content-Type': 'application/json'}
    if provider == 'anthropic':
        headers.update({'x-api-key': key, 'anthropic-version': '2023-06-01'})
    else:
        headers['Authorization'] = 'Bearer ' + key
    request = urllib.request.Request(endpoint, json.dumps(body).encode(), headers, method='POST')
    # One request only; callers retain inputs and errors without automatic retries.
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout) as response:
        return json.load(response)


def arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--category', required=True)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--catalogue', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing paths are refused')
    parser.add_argument('--execute', action='store_true', help='Actually run inference; otherwise prepare inputs only')
    return parser


def begin(args):
    packet = prepare(args.category, args.seed, args.catalogue)
    args.output.mkdir(parents=True, exist_ok=False)
    save(args.output / 'input.json', packet)
    return packet


def fail(folder, error):
    # Exception bodies may contain provider echoes or credentials. Keep only the error class/status.
    save(folder / 'error.json', {'status': 'error', 'error_type': type(error).__name__,
                                'http_status': getattr(error, 'code', None), 'ranks': None})
    print('Evaluation failed; see error.json. No ranking was assigned.')
