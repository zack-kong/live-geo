"""Run one six-listing evaluation using an OpenAI-compatible or Anthropic API."""
from runtime import arguments, begin, fail, parse_ranking, post, record, save


def request_body(packet, model, max_tokens):
    return {'model': model, 'messages': [{'role': 'user', 'content': packet['prompt']}],
            'max_tokens': max_tokens, 'temperature': 0}


def response_text(response, provider):
    if provider == 'anthropic':
        return '\n'.join(x['text'] for x in response['content'] if x.get('type') == 'text')
    return response['choices'][0]['message']['content']


def main():
    parser = arguments(__doc__)
    parser.add_argument('--provider', choices=['openai', 'anthropic'], default='openai')
    parser.add_argument('--endpoint', required=True, help='Full HTTPS chat/completions or messages endpoint')
    parser.add_argument('--model', required=True)
    parser.add_argument('--key-env', default='EVALUATOR_API_KEY')
    parser.add_argument('--max-tokens', type=int, default=512)
    args = parser.parse_args()
    if args.max_tokens <= 0:
        parser.error('--max-tokens must be positive')
    packet = begin(args)
    body = request_body(packet, args.model, args.max_tokens)
    save(args.output / 'request.json', body)
    save(args.output / 'settings.json', {'provider': args.provider, 'endpoint': args.endpoint,
                                        'model': args.model, 'seed': args.seed, 'attempts': 1})
    if not args.execute:
        print('Prepared inputs; no API request sent. Add --execute with a new output directory to run.')
        return
    try:
        response = post(args.endpoint, body, args.key_env, args.provider)
        save(args.output / 'response.json', response)
        ranking = parse_ranking(response_text(response, args.provider), packet['input_order'])
        save(args.output / 'result.json', record(packet, ranking, args.model))
        print('complete' if ranking is not None else 'invalid; raw response preserved')
    except Exception as error:
        fail(args.output, error)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
