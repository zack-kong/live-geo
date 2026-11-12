"""Saved-input BM25 and Qwen response parsing; no downloads or model calls.

lexical and parse_ids are copied unchanged from the frozen local-evaluation runner.
"""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
TOKEN=re.compile(r'[a-z0-9]+')

def lexical(docs,query):
    tokens={m:TOKEN.findall(docs[m].lower()) for m in docs};terms=TOKEN.findall(query.lower())
    n=len(tokens);avg=sum(map(len,tokens.values()))/n;assert avg>0
    df=Counter(t for d in tokens.values() for t in set(d));scores={}
    for m,d in tokens.items():
        tf=Counter(d)
        scores[m]=sum(math.log(1+(n-df[t]+.5)/(df[t]+.5))*tf[t]*2.2/(tf[t]+1.2*(.25+.75*len(d)/avg)) for t in terms)
    ranks={m:sum(v>scores[m] for v in scores.values())+(sum(v==scores[m] for v in scores.values())+1)/2 for m in scores}
    assert math.isclose(sum(ranks.values()),n*(n+1)/2)
    return ranks,scores

def parse_ids(raw,order):
    for match in re.finditer(r'\[',raw):
        try:value,_=json.JSONDecoder().raw_decode(raw[match.start():])
        except ValueError:continue
        if isinstance(value,list) and len(value)==6 and all(type(x) is int or (type(x) is str and re.fullmatch('[1-6]',x)) for x in value):
            numbers=[int(x) for x in value]
            if set(numbers)==set(range(1,7)):return {order[x-1]:rank for rank,x in enumerate(numbers,1)}
    return None

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path, help='Saved input.json with query and candidate prose')
    p.add_argument('--qwen-result', type=Path, help='Optional saved qwen_ids_result.json')
    args = p.parse_args()
    packet = json.loads(args.input.read_text(encoding='utf8'))
    if args.qwen_result:
        result = json.loads(args.qwen_result.read_text(encoding='utf8'))
        ranks = parse_ids(result['raw'], packet['input_order'])
        print(json.dumps({'valid': ranks is not None, 'ranks': ranks}))
    else:
        ranks, scores = lexical({m:v['prose'] for m,v in packet['candidates'].items()},packet['query'])
        print(json.dumps({'ranks': ranks, 'scores': scores}))
