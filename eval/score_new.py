"""Score new run directories containing result.json; invalid outputs have no rank."""
import argparse
import csv
from pathlib import Path
from runtime import read


def summarize(folder):
    records = [read(p) for p in sorted(Path(folder).glob('*/result.json'))]
    valid = [r for r in records if r['status'] == 'complete']
    if not valid:
        raise ValueError('No complete rankings found')
    if len({r['category_id'] for r in valid}) != len(valid):
        raise ValueError('Select one output per category and condition before scoring')
    methods = set(valid[0]['ranks'])
    if len(methods) != 6 or any(set(r['ranks']) != methods or sorted(r['ranks'].values()) != list(range(1, 7)) for r in valid):
        raise ValueError('Rankings must be complete permutations of the same six methods')
    n = len(valid)
    return [{'method': m, 'n': n, 'top1_percent': 100*sum(r['ranks'][m] == 1 for r in valid)/n,
             'mean_rank': sum(r['ranks'][m] for r in valid)/n} for m in sorted(methods)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path, help='One condition, with one subdirectory per category')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = summarize(args.folder)
    with args.output.open('x', encoding='utf8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Scored {rows[0]['n']} complete brands")
