"""Inspect saved direct-text responses without making paid API calls."""
import argparse
import json
from pathlib import Path


def parse_response(response, expected_names):
    if 'choices' in response:
        text = response['choices'][0]['message']['content']
    elif 'content' in response:
        text = '\n'.join(b['text'] for b in response['content'] if b.get('type') == 'text')
    else:
        raise ValueError('Expected an OpenAI-compatible or Anthropic response object')
    arrays = []
    for i, char in enumerate(text):
        if char == '[':
            try:
                value, _ = json.JSONDecoder().raw_decode(text[i:])
            except ValueError:
                continue
            if isinstance(value, list):
                arrays.append(value)
    if not arrays or any(a != arrays[0] for a in arrays):
        return None
    values = arrays[0]
    if len(values) != 6 or not all(isinstance(v, str) for v in values):
        return None
    if len(set(values)) != 6 or set(values) != set(expected_names):
        return None
    return {name: rank for rank, name in enumerate(values, 1)}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('response', type=Path)
    p.add_argument('names', type=Path, help='JSON array of six exact expected product names')
    args = p.parse_args()
    ranks = parse_response(json.loads(args.response.read_text(encoding='utf8')),
                           json.loads(args.names.read_text(encoding='utf8')))
    print(json.dumps({'valid': ranks is not None, 'ranks': ranks}, ensure_ascii=False))
