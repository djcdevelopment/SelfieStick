#!/usr/bin/env python3
"""Check the contract against fixtures from an explicitly pinned Steward artifact."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runner'))
import capture_spec as contract

parser = argparse.ArgumentParser(description=__doc__)
for key in ('artifact', 'pin', 'out'):
    parser.add_argument('--' + key, type=Path, required=True)
args = parser.parse_args()
pin = json.loads(args.pin.read_text(encoding='utf-8'))
assert contract.file_record(args.artifact) == {key: pin[key] for key in ('bytes', 'sha256')}
with zipfile.ZipFile(args.artifact) as archive:
    data = archive.read('camera-fixtures.json')
    manifest = json.loads(archive.read('manifest.json'))
    row = next(row for row in manifest['files'] if row['path'] == 'camera-fixtures.json')
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
fixture = json.loads(data)
for case in fixture['projections']:
    camera = {**fixture['camera'], **{key: case[key] for key in ('verticalFov', 'width', 'height')}}
    assert contract.dimensions(case['frame'], case['longestEdge']) == [case['width'], case['height']]
    spec = {'schema': contract.SCHEMA, 'requiredPluginVersion': contract.PLUGIN_VERSION, 'camera': camera,
            'source': {'photoId': 'fixture', 'buildKey': 'fixture', 'world': {'id': 'Fixture', 'db': {'bytes': 1, 'sha256': 'a'*64}, 'fwl': {'bytes': 1, 'sha256': 'b'*64}}},
            'settings': {'environment': 'Clear', 'timeOfDay': .64, 'fires': False, 'flashBearing': None}}
    fields = contract.shot_list(spec).splitlines()[1].split('\t')
    assert list(map(float, fields[2:5])) == fixture['playerFeet']
    assert list(map(float, fields[16:19])) == camera['lens']
    assert list(map(int, fields[20:22])) == [case['width'], case['height']]
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps({'status': 'passed', 'cases': len(fixture['projections']), 'artifact': pin,
                               'fixtureSha256': row['sha256']}, indent=2)+'\n', encoding='utf-8')
print(f"{len(fixture['projections'])} shared camera fixtures passed")
