"""Re-score the selected outputs of a released LIVE-GEO round; no model calls."""
import argparse
import csv
import hashlib
import json
import math
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
METHODS=['Original','CORE','CSEO','EGEO','AgenticGEO','GEO-StatisticsAddition']
def read(path):return json.loads(path.read_text(encoding='utf8'))
def parse(record):
 names=record['model_output']['ranking']
 if len(names)!=6 or len(set(names))!=6:raise ValueError('Expected six distinct candidates')
 ranks={record['name_to_method'][name]:i for i,name in enumerate(names,1)}
 if set(ranks)!=set(METHODS):raise ValueError('Expected all six methods')
 if ranks!=record['ranks']:raise ValueError('Saved ranks differ from output')
 return ranks

def fixed(value,places):return str(Decimal(str(value)).quantize(Decimal(10)**-places,rounding=ROUND_HALF_UP))
def summarize(cid,matrix):
 n=len(matrix)
 if n==0:raise ValueError('No included observations')
 rows=[]
 for m in METHODS:
  count=sum(r[m]==1 for r in matrix.values());total=sum(r[m] for r in matrix.values())
  rows.append({'condition_id':cid,'method':m,'n':n,'top1_count':count,'rank_sum':total,
   'top1_percent':fixed(Decimal(count)*100/n,1),'mean_rank':fixed(Decimal(total)/n,2)})
 return rows

def csv_write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def load_round(folder,check=False):
 manifest=read(folder/'manifest.json');matrices={}
 for c in manifest['conditions']:
  cid=c['condition_id'];matrix={}
  settings=read(folder/c['raw_directory']/'settings.json');assert settings==c
  for p in sorted((folder/c['raw_directory']).glob('*.json')):
   if p.name=='settings.json':continue
   d=read(p);cat=d['category_id'];assert p.stem==cat and cat not in matrix and d['condition_id']==cid
   assert d['output_kind'] in ['structured_model_output','ranking_array_excerpt']
   matrix[cat]=parse(d)
  assert len(matrix)==c['n'],cid
  matrices[cid]=matrix
 if check:
  for relative,digest in read(folder/'checksums.json').items():
   assert hashlib.sha256((folder/relative).read_bytes()).hexdigest()==digest,relative
  refs=read(folder/'scores/reference.json');assert {r['condition_id'] for r in refs}==set(matrices)
  for ref in refs:
   cid=ref['condition_id'];assert matrices[cid]==ref['matrix'],cid
   actual=summarize(cid,matrices[cid]);expected=ref['summary']
   assert [r['top1_count'] for r in actual]==expected['top1_counts']
   assert [r['rank_sum'] for r in actual]==expected['rank_sums']
   assert [f"{r['top1_percent']} / {r['mean_rank']}" for r in actual]==expected['cells']
  catalogue=read(ROOT/'catalogue/index.json');assert len(catalogue)==80 and len({c['family'] for c in catalogue})==18
  cats={c['category_id'] for c in catalogue};prices={}
  for cat in catalogue:
   listings=[read(ROOT/p) for p in cat['listings']]
   assert len(listings)==6 and {x['method'] for x in listings}==set(METHODS)
   for x in listings:
    assert len(x['reviews'])==7
    prices[(cat['category_id'],x['method'])]=x['price_display']
  for c in manifest['conditions']:
   assert set(matrices[c['condition_id']])==cats
   for cat in cats:
    d=read(folder/c['raw_directory']/f'{cat}.json')
    assert d['input']['prompt']
    for method,price in d['input']['prices'].items():
     assert str(price) in prices[(cat,method)].replace(',',''),(cat,method,price)
    if c['entry']=='product URLs':
     urls=d['input']['supplied_url_order'];assert len(urls)==len(set(urls))==6
     assert all(u in d['input']['prompt'] for u in urls)
    else:assert d['input']['supplied_brand_url'] in d['input']['prompt']
  sample={'model_output':{'ranking':METHODS},'name_to_method':{m:m for m in METHODS},'ranks':dict(zip(METHODS,range(1,7)))}
  assert parse(sample)==sample['ranks']
  for invalid in [METHODS[:-1],METHODS[:-1]+METHODS[:1],METHODS[:-1]+['Unknown']]:
   try:parse({**sample,'model_output':{'ranking':invalid}})
   except (ValueError,KeyError):pass
   else:raise AssertionError('Invalid ranking accepted')
 return manifest,matrices

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--round',default='round_001_2026-10');p.add_argument('--check',action='store_true');p.add_argument('--out',type=Path)
 args=p.parse_args();r=Path(args.round);folder=r if r.is_absolute() else ROOT/(r if r.parts[0]=='rounds' else Path('rounds')/r)
 manifest,matrices=load_round(folder,args.check);out=args.out or folder/'scores';allrows=[]
 for c in manifest['conditions']:
  cid=c['condition_id'];matrix=matrices[cid];rows=summarize(cid,matrix);allrows+=rows
  sub=Path(c['scores_directory']).relative_to('scores')
  csv_write(out/sub/'summary.csv',rows)
  csv_write(out/sub/'rankings.csv',[{'category_id':cat,**ranks} for cat,ranks in sorted(matrix.items())])
 csv_write(out/'summary.csv',allrows)
 agreements=[]
 for i,a in enumerate(manifest['conditions']):
  for b in manifest['conditions'][i+1:]:
   x=matrices[a['condition_id']];y=matrices[b['condition_id']];cats=sorted(x.keys()&y.keys());n=len(cats)
   rho=sum(1-sum((x[k][m]-y[k][m])**2 for m in METHODS)/35 for k in cats)/n
   same=sum(min(x[k],key=x[k].get)==min(y[k],key=y[k].get) for k in cats)
   gap=sum(abs(x[k][m]-y[k][m]) for k in cats for m in METHODS)/(6*n)
   agreements.append({'first':a['condition_id'],'second':b['condition_id'],'n':n,'mean_spearman':rho,'same_winner_count':same,'same_winner_percent':fixed(Decimal(same)*100/n,1),'mean_absolute_rank_change':gap})
 csv_write(out/'agreement_descriptive.csv',agreements)
 print(json.dumps({'conditions':len(matrices),'brand_outputs':sum(len(m) for m in matrices.values()),'verified':args.check,'summary_rows':len(allrows)}))
if __name__=='__main__':main()
