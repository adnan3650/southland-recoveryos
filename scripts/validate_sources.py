"""Validate and normalize curated ingestion input; never mark HTTP success as content verification."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app.services.resources import ResourceService
parser=argparse.ArgumentParser()
parser.add_argument('input',nargs='?',default='data/resources.json')
parser.add_argument('--output',help='New normalized dataset path; must not exist')
args=parser.parse_args()
rows=ResourceService.normalize(json.loads(Path(args.input).read_text()))
if args.output:
    with Path(args.output).open('x') as stream:
        json.dump(rows,stream,indent=2)
print(f'{len(rows)} validated unique records. Review source content manually before setting verified_at.')
