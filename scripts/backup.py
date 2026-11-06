"""Consistent local backup. Stop server first to synchronize evidence and case metadata."""
import argparse
import shutil
import sqlite3
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('destination',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]/'runtime'
args.destination.mkdir(parents=True,exist_ok=False)
with sqlite3.connect(root/'cases.sqlite3') as source, sqlite3.connect(args.destination/'cases.sqlite3') as target:
    source.backup(target)
shutil.copytree(root/'documents',args.destination/'documents')
args.destination.chmod(0o700)
print('Backup complete. Browser ownership cookies are also required to resume existing cases.')
