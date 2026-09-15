#!/usr/bin/env python3
"""Run the real archive matrix with an explicit, hash-pinned runner artifact."""
import argparse
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('runner', 'spec', 'game-root', 'world-db', 'world-fwl', 'character-file', 'out'):
        parser.add_argument('--' + key, type=Path, required=True)
    parser.add_argument('--host', choices=('OMEN', 'AM4'), required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.runner.resolve()))
    contract = importlib.import_module('capture_spec')
    capture = importlib.import_module('capture')
    kit = importlib.import_module('capture_kit')
    spec = contract.validate(json.loads(args.spec.read_text(encoding='utf-8')))
    manifest = capture.verify_runner(args.runner.resolve())
    contract.verify_world(spec, args.world_db, args.world_fwl)
    capture.assert_game_idle(args.game_root)
    game = args.game_root.resolve()
    originals = {str(p): contract.file_record(p) for p in (args.world_db, args.world_fwl, args.character_file)}
    plugins = capture.tree_records(game / 'BepInEx/plugins')
    controls = {name: (game / 'BepInEx/config' / name).read_bytes() if (game / 'BepInEx/config' / name).exists() else None for name in kit.CONTROL}
    saves_before = capture.save_records()
    args.out.mkdir(parents=True, exist_ok=False)
    write(args.out / 'saves-before.json', saves_before)
    lock = game / 'BepInEx/selfiestick-capture.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    specs, labels, frames, cases, compatibility = {}, {}, [], [], []
    error, result = None, None
    try:
        with tempfile.TemporaryDirectory(prefix='selfiestick-proof-') as directory:
            work, rows = Path(directory), []
            for size, fovs in ((1920, (90, 65, 35)), (3840, (65,))):
                for fov in fovs:
                    for label, frame in zip(('Landscape', 'Square', 'Portrait'), contract.FRAMES):
                        candidate = copy.deepcopy(spec)
                        width, height = contract.dimensions(frame, size)
                        candidate['camera'].update(verticalFov=fov, width=width, height=height)
                        if size == 3840 and label == 'Square':
                            candidate['camera']['roll'] = 12
                        name = f'{label.lower()}-{fov}-{size}'
                        specs[name], labels[name] = candidate, label
                        row = contract.shot_list(candidate).splitlines()[1].split('\t')
                        row[1] = name
                        rows.append('\t'.join(row))
            legacy = contract.shot_list(spec).splitlines()[1].split('\t')[:16]
            legacy[1], legacy[13] = 'legacy', 'detail'
            rows.append('\t'.join(legacy))
            legacy[1] = 'legacy-projection'
            rows.append('\t'.join(legacy + ['', '', '', '35', '1080', '1920', '0']))
            shots = work / 'shots.tsv'
            shots.write_text(contract.HEADER + '\n'.join(rows) + '\n', encoding='utf-8')
            write(args.out / 'requested.json', specs)
            code = kit.main(['--game-root', str(game), '--world', spec['source']['world']['id'],
                '--world-db', str(args.world_db.resolve()), '--world-fwl', str(args.world_fwl.resolve()),
                '--character', 'proof', '--character-file', str(args.character_file.resolve()),
                '--shots', str(shots), '--out', str(args.out.resolve()), '--save-root', str(work / 'saves'),
                '--mods', str(args.runner.resolve() / 'mods'), '--width', '1280', '--height', '720', '--timeout-minutes', '8'])
            result = json.loads((args.out / 'receipt.json').read_text(encoding='utf-8'))
            for frame in result['results']:
                if 'receipt' not in frame:
                    raise ValueError('capture skipped: ' + str(frame))
                if frame['shot'].startswith('legacy'):
                    expected = [1280, 720] if frame['shot'] == 'legacy' else [1080, 1920]
                    if frame['dimensions'] != expected:
                        raise ValueError('legacy output dimensions changed')
                    if frame['shot'] == 'legacy-projection':
                        observed = frame['receipt'].get('observed', {})
                        if observed.get('verticalFov') != 35 or frame['receipt'].get('camera_restored') is not True:
                            raise ValueError('legacy optional projection was not measured/restored')
                    compatibility.append({'shot': frame['shot'], 'status': 'passed', 'dimensions': frame['dimensions']})
                    continue
                contract.verify_observed(specs[frame['shot']], frame['receipt'], frame['dimensions'])
                if frame['sha256'] != frame['receipt']['image_sha256']:
                    raise ValueError('image hash mismatch')
                frames.append(frame)
            if code or len(frames) != 12 or len(compatibility) != 2:
                raise ValueError(f'Only {len(frames)}/12 exact and {len(compatibility)}/2 legacy cases completed')
    except BaseException as exc:
        error = str(exc) or type(exc).__name__
    finally:
        restored = plugins == capture.tree_records(game / 'BepInEx/plugins') and all(
            ((game / 'BepInEx/config' / name).read_bytes() if (game / 'BepInEx/config' / name).exists() else None) == data for name, data in controls.items())
        unchanged = all(contract.file_record(Path(name)) == before for name, before in originals.items())
        saves_after = capture.save_records()
        write(args.out / 'saves-after.json', saves_after)
        discovery_unchanged = saves_before == saves_after
        restoration = {'pluginsAndControls': restored, 'sourceSavesUnchanged': unchanged,
                       'discoverySavesUnchanged': discovery_unchanged,
                       'beforeSha256': digest(saves_before), 'afterSha256': digest(saves_after)}
        lock.unlink()
        if not restored or not unchanged or not discovery_unchanged:
            error = error or 'restoration failed'
        for frame in frames:
            candidate = specs[frame['shot']]
            receipt = {'schema': 'selfiestick-capture-case/v1', 'host': args.host, 'requested': candidate,
                       'observed': frame['receipt'], 'identity': result['identity'], 'restoration': restoration,
                       'png': {key: frame[key] for key in ('file', 'sha256', 'bytes', 'dimensions')}, 'runner': manifest}
            path = args.out / (frame['shot'] + '.json')
            write(path, receipt)
            cases.append({'verticalFov': candidate['camera']['verticalFov'], 'frame': labels[frame['shot']],
                          'longestEdge': max(candidate['camera']['width'], candidate['camera']['height']),
                          'status': 'passed' if not error else 'failed',
                          'pluginSha256': contract.file_record(args.runner / 'mods/CameraProof.dll')['sha256'],
                          'receipt': path.name, 'receiptSha256': contract.file_record(path)['sha256'], 'restored': not error})
        proof = {'schema': 'selfiestick-capture-proof/v1', 'hosts': {args.host: cases}, 'error': error,
                 'restoration': restoration, 'compatibility': compatibility}
        write(args.out / 'capture-proof.json', proof)
        print(json.dumps({'proof': str(args.out / 'capture-proof.json'), 'exact': len(frames),
                          'legacy': len(compatibility), 'error': error, 'restoration': restoration}, indent=2))
    return 1 if error else 0


if __name__ == '__main__':
    raise SystemExit(main())
