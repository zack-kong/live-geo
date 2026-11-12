"""Offline contract tests; synthetic fixtures are not experimental results."""
import copy
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import runtime
import run_api
import score_new
from jev import verify


class Runners(unittest.TestCase):
    def setUp(self):
        self.packet = runtime.prepare('actinic-shielded-print-cabinet', 3)

    def test_input_complete_and_reproducible(self):
        self.assertEqual(self.packet, runtime.prepare(self.packet['category_id'], 3))
        self.assertNotEqual(self.packet['input_order'], runtime.prepare(self.packet['category_id'], 4)['input_order'])
        for listing in self.packet['listings']:
            self.assertIn(listing['description'], self.packet['prompt'])
            self.assertIn(listing['price_display'], self.packet['prompt'])
            for review in listing['reviews']:
                self.assertIn(review['text'], self.packet['prompt'])

    def test_rank_parser_controls(self):
        names = self.packet['input_order']
        self.assertEqual(runtime.parse_ranking(json.dumps(names), names), names)
        for value in [names[:-1], names[:-1] + [names[0]], list(range(6)), names[:-1] + ['unknown']]:
            self.assertIsNone(runtime.parse_ranking(json.dumps(value), names))
        self.assertIsNone(runtime.parse_ranking(json.dumps(names)+json.dumps(names[::-1]), names))

    def test_http_contract_both_providers(self):
        body = run_api.request_body(self.packet, 'test-model', 32)
        names = self.packet['input_order']
        for provider in ['openai', 'anthropic']:
            response = ({'choices': [{'message': {'content': json.dumps(names)}}]} if provider == 'openai'
                        else {'content': [{'type': 'text', 'text': json.dumps(names)}]})
            stream = io.BytesIO(json.dumps(response).encode())
            with patch.dict(os.environ, {'TEST_KEY': 'synthetic-test-key'}), patch('urllib.request.build_opener') as opener:
                opener.return_value.open.return_value = stream
                received = runtime.post('https://example.invalid/api', body, 'TEST_KEY', provider)
                request = opener.return_value.open.call_args.args[0]
                self.assertEqual(json.loads(request.data), body)
                self.assertEqual(request.headers.get('Authorization' if provider == 'openai' else 'X-api-key'),
                                 'Bearer synthetic-test-key' if provider == 'openai' else 'synthetic-test-key')
                self.assertEqual(opener.return_value.open.call_count, 1)
            self.assertEqual(runtime.parse_ranking(run_api.response_text(received, provider), names), names)

    def test_transport_error_has_no_retry(self):
        with patch.dict(os.environ, {'TEST_KEY': 'synthetic-test-key'}), patch('urllib.request.build_opener') as opener:
            opener.return_value.open.side_effect = TimeoutError('synthetic-test-key')
            with self.assertRaises(TimeoutError):
                runtime.post('https://example.invalid/api', {}, 'TEST_KEY')
            self.assertEqual(opener.return_value.open.call_count, 1)
        with tempfile.TemporaryDirectory() as folder:
            runtime.fail(Path(folder), TimeoutError('synthetic-test-key'))
            self.assertNotIn('synthetic-test-key', (Path(folder)/'error.json').read_text())

    def test_api_cli_prepare_and_execute(self):
        with tempfile.TemporaryDirectory() as folder:
            base = ['run_api.py', '--category', self.packet['category_id'], '--endpoint',
                    'https://example.invalid/api', '--model', 'fixture']
            with patch('sys.argv', base + ['--output', str(Path(folder)/'prepare')]), patch('run_api.post') as post:
                run_api.main()
                post.assert_not_called()
            prepared = runtime.prepare(self.packet['category_id'], 0)
            response = {'choices': [{'message': {'content': json.dumps(prepared['input_order'])}}]}
            target = Path(folder)/'execute'
            with patch('sys.argv', base + ['--output', str(target), '--execute']), patch('run_api.post', return_value=response) as post:
                run_api.main()
                post.assert_called_once()
            self.assertEqual(runtime.read(target/'response.json'), response)
            self.assertEqual(runtime.read(target/'result.json')['status'], 'complete')

    def test_credential_routes_and_no_overwrite(self):
        for endpoint in ['http://example.com', 'https://user:secret@example.com', 'https://example.com?key=secret']:
            with self.assertRaises(ValueError):
                runtime.post(endpoint, {}, 'TEST_KEY')
        with self.assertRaises(ValueError):
            runtime.NoRedirect().redirect_request(None, None, None, None, None, None)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'result.json'
            runtime.save(target, {'a': 1})
            with self.assertRaises(FileExistsError):
                runtime.save(target, {'a': 2})
            self.assertEqual(runtime.read(target), {'a': 1})

    def test_jev_threshold_and_malformed_results(self):
        fixture = {'model': verify.MODEL, 'answers': {'verdict': {'type': 'choice', 'choice': 'FLAG',
                   'probabilities': {'FLAG': .95, 'NO_FLAG': .05}}}}
        self.assertTrue(verify.verdict(fixture)['flag'])
        lower = copy.deepcopy(fixture)
        lower['answers']['verdict']['probabilities'] = {'FLAG': .94, 'NO_FLAG': .06}
        self.assertFalse(verify.verdict(lower)['flag'])
        for probabilities in [{'FLAG': float('nan'), 'NO_FLAG': .1}, {'FLAG': .2}, {'FLAG': .9, 'NO_FLAG': .9}]:
            bad = copy.deepcopy(fixture)
            bad['answers']['verdict']['probabilities'] = probabilities
            with self.assertRaises(ValueError):
                verify.verdict(bad)
        body = verify.request_body(self.packet['listings'][0])
        self.assertEqual(body['state']['TARGET_DESCRIPTION'], self.packet['listings'][0]['description'])
        self.assertNotIn('reviews', body['state'])

    def test_scoring_missing_and_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, ranking in [('one', self.packet['input_order']), ('two', None)]:
                (root/name).mkdir()
                runtime.save(root/name/'result.json', runtime.record(self.packet, ranking, 'fixture'))
            scores = score_new.summarize(root)
            self.assertEqual({r['n'] for r in scores}, {1})
            self.assertEqual(sum(r['top1_percent'] for r in scores), 100)
            (root/'duplicate').mkdir()
            runtime.save(root/'duplicate/result.json', runtime.record(self.packet, self.packet['input_order'], 'fixture'))
            with self.assertRaises(ValueError):
                score_new.summarize(root)


if __name__ == '__main__':
    unittest.main()
