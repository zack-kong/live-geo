"""Run cached local Qwen inference on the catalogue without truncating candidates."""
from runtime import arguments, begin, fail, parse_ranking, record, save


def generate(packet, model_name, revision, device, max_new_tokens):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, revision=revision, local_files_only=True,
        torch_dtype=torch.float32 if device == 'cpu' else torch.bfloat16).to(device).eval()
    text = tokenizer.apply_chat_template([{'role': 'user', 'content': packet['prompt']}],
                                         tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors='pt', add_special_tokens=False).to(device)
    length = inputs['input_ids'].shape[1]
    if length + max_new_tokens > model.config.max_position_embeddings:
        raise ValueError('Full candidates exceed model context; no truncation performed')
    with torch.inference_mode():
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    return {'raw': tokenizer.decode(outputs[0, length:], skip_special_tokens=True),
            'input_tokens': length, 'output_tokens': outputs.shape[1] - length,
            'resolved_revision': getattr(model.config, '_commit_hash', None),
            'torch_version': torch.__version__}


def main():
    parser = arguments(__doc__)
    parser.add_argument('--model', default='Qwen/Qwen2.5-3B-Instruct')
    parser.add_argument('--revision', default='main')
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
    parser.add_argument('--max-new-tokens', type=int, default=512)
    args = parser.parse_args()
    if args.max_new_tokens <= 0:
        parser.error('--max-new-tokens must be positive')
    packet = begin(args)
    save(args.output / 'settings.json', {'model': args.model, 'revision': args.revision,
        'device': args.device, 'seed': args.seed, 'do_sample': False,
        'max_new_tokens': args.max_new_tokens, 'local_files_only': True})
    if not args.execute:
        print('Prepared inputs; no model loaded. Add --execute with a new output directory to run.')
        return
    try:
        response = generate(packet, args.model, args.revision, args.device, args.max_new_tokens)
        save(args.output / 'response.json', response)
        ranking = parse_ranking(response['raw'], packet['input_order'])
        save(args.output / 'result.json', record(packet, ranking, args.model))
        print('complete' if ranking is not None else 'invalid; raw response preserved')
    except Exception as error:
        fail(args.output, error)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
