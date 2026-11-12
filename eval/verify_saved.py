"""Verify selected web outputs and frozen reference scores without modifying them."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('reproduce_tables',ROOT/'analysis/reproduce_tables.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
if __name__=='__main__':
 manifest,matrices=mod.load_round(ROOT/'rounds/round_001_2026-10',check=True)
 print(f'PASS: {len(matrices)} conditions, {sum(map(len,matrices.values()))} selected outputs')
