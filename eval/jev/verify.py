"""Optional hosted JEV numerical-faithfulness check for one catalogue listing."""
import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime import fail, post, read, save

POLICY = (Path(__file__).parent / 'policy.txt').read_text(encoding='utf8').strip()
MODEL = 'jev-1.13.0'
ENDPOINT = 'https://api.typesafe.ai/v1/systemone'


def request_body(listing, model=MODEL):
    return {'model': model, 'state': {'SPECIFICATIONS': listing['specifications'],
            'FINAL_DISPLAY_FACTS': {'price': listing['price_display']},
            'TARGET_DESCRIPTION': listing['description']},
            'questions': {'verdict': {'type': 'choice', 'instructions': POLICY,
                'criteria': {'NO_FLAG': 'No conflicting or unsupported numerical claim.',
                             'FLAG': 'At least one conflicting or unsupported numerical claim.'}}}}


def verdict(response, model=MODEL, threshold=.95):
    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError('Threshold must be between zero and one')
    if response['model'] != model:
        raise ValueError('Unexpected model version')
    answer = response['answers']['verdict']
    probabilities = answer['probabilities']
    if answer['type'] != 'choice' or answer['choice'] not in {'FLAG', 'NO_FLAG'}:
        raise ValueError('Invalid verdict')
    if set(probabilities) != {'FLAG', 'NO_FLAG'}:
        raise ValueError('Incomplete probabilities')
    if any(type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1
           for p in probabilities.values()) or not math.isclose(sum(probabilities.values()), 1, abs_tol=1e-5):
        raise ValueError('Invalid probabilities')
    return {'status': 'complete', 'p_flag': probabilities['FLAG'], 'threshold': threshold,
            'flag': probabilities['FLAG'] >= threshold, 'advisory': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('listing', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--response', type=Path, help='Replay a saved JEV response without a request')
    parser.add_argument('--model', default=MODEL)
    parser.add_argument('--threshold', type=float, default=.95)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.execute and args.response:
        parser.error('Choose saved response or --execute, not both')
    if not math.isfinite(args.threshold) or not 0 <= args.threshold <= 1:
        parser.error('Threshold must be between zero and one')
    body = request_body(read(args.listing), args.model)
    args.output.mkdir(parents=True, exist_ok=False)
    save(args.output / 'request.json', body)
    save(args.output / 'settings.json', {'model': args.model, 'endpoint': ENDPOINT,
                                        'threshold': args.threshold, 'scope': 'description only'})
    if not args.execute and not args.response:
        print('Prepared input; no JEV request sent. Set TYPESAFE_API_KEY and use --execute to run.')
        return
    try:
        response = read(args.response) if args.response else post(ENDPOINT, body, 'TYPESAFE_API_KEY')
        save(args.output / 'response.json', response)
        save(args.output / 'result.json', verdict(response, args.model, args.threshold))
        print('complete; advisory result saved privately in the selected output directory')
    except Exception as error:
        fail(args.output, error)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
