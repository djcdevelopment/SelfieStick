#!/usr/bin/env python3
"""Run a gallery capture using verified dependencies and disposable local saves."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

import capture_kit
from capture_spec import PLUGIN_VERSION, file_record, shot_list, validate, verify_observed, verify_world

HERE = Path(__file__).resolve().parent


def verify_runner(root):
    manifest = json.loads((root / "runner-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "selfiestick-runner/v1" or manifest.get("pluginVersion") != PLUGIN_VERSION:
        raise ValueError("incompatible runner/plugin version")
    required = {"capture.py", "capture_kit.py", "capture_spec.py", "mods/CameraProof.dll", "mods/BetterServerPortals.dll"}
    entries = manifest.get("files", [])
    names = [r["path"] for r in entries]
    if not required.issubset(names) or len(names) != len(set(names)):
        raise ValueError("incomplete dependency manifest")
    for entry in entries:
        path = (root / entry["path"]).resolve()
        if not path.is_relative_to(root.resolve()) or file_record(path) != {k: entry[k] for k in ("bytes", "sha256")}:
            raise ValueError("runner dependency hash mismatch: " + entry["path"])
    return manifest


def assert_game_idle(game):
    if os.name == "nt":
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq valheim.exe"], capture_output=True, text=True, check=True)
        busy = "valheim.exe" in result.stdout.lower()
    else:
        steam = subprocess.run(["pgrep", "-x", "steam"], capture_output=True)
        if steam.returncode != 0:
            raise ValueError("Steam must be running; start Steam before local capture")
        result = subprocess.run(["pgrep", "-x", "valheim.x86_64"], capture_output=True)
        if result.returncode not in (0, 1):
            raise ValueError("could not check whether Valheim is running")
        busy = result.returncode == 0
    if busy:
        raise ValueError("Valheim is already running; close it before local capture")


def tree_records(root):
    return {p.relative_to(root).as_posix(): file_record(p) for p in sorted(root.rglob("*")) if p.is_file()} if root.exists() else None


def save_records():
    """Verify the real discovery path and all local Steam character mirrors, too."""
    roots = [capture_kit.save_dir()]
    if os.name == "nt":
        steam = [Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam/userdata"]
    else:
        steam = [Path.home() / ".steam/steam/userdata", Path.home() / ".local/share/Steam/userdata"]
    for root in steam:
        roots.extend(p.resolve() for p in root.glob("*/892970/remote/characters"))
    return {str(root): tree_records(root) for root in set(roots)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec", type=Path, default=HERE / "capture.json")
    p.add_argument("--game-root", type=Path, required=True)
    p.add_argument("--world-db", type=Path, required=True)
    p.add_argument("--world-fwl", type=Path, required=True)
    p.add_argument("--character-file", type=Path, required=True)
    p.add_argument("--out", type=Path, default=HERE / "results")
    p.add_argument("--timeout-minutes", type=float, default=8)
    args = p.parse_args(argv)
    spec = validate(json.loads(args.spec.read_text(encoding="utf-8")))
    runner = verify_runner(HERE)
    verify_world(spec, args.world_db, args.world_fwl)
    if not args.character_file.is_file():
        raise ValueError("character file missing")
    assert_game_idle(args.game_root)
    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out.resolve() / time.strftime("capture-%Y%m%dT%H%M%S")
    out.mkdir()
    (out / "capture.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    game = args.game_root.resolve()
    lock = game / "BepInEx/selfiestick-capture.lock"
    # One owner per install. A stale lock is evidence to inspect, never silently remove.
    original_plugins = tree_records(game / "BepInEx/plugins")
    controls = {name: (game / "BepInEx/config" / name).read_bytes() if (game / "BepInEx/config" / name).exists() else None
                for name in capture_kit.CONTROL}
    character_before = file_record(args.character_file)
    saves_before = save_records()
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    error = None
    result = None
    try:
        with tempfile.TemporaryDirectory(prefix="selfiestick-") as temporary:
            work = Path(temporary)
            shots = work / "shots.tsv"
            shots.write_text(shot_list(spec), encoding="utf-8")
            code = capture_kit.main(["--game-root", str(game), "--world", spec["source"]["world"]["id"],
                "--world-db", str(args.world_db.resolve()), "--world-fwl", str(args.world_fwl.resolve()),
                "--character", "capture", "--character-file", str(args.character_file.resolve()),
                "--shots", str(shots), "--save-root", str(work / "saves"), "--out", str(out),
                "--mods", str(HERE / "mods"), "--width", "1280", "--height", "720",
                "--timeout-minutes", str(args.timeout_minutes)])
            result = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
            if code or len(result["results"]) != 1:
                raise ValueError("local capture failed; see receipts.jsonl and BepInEx.log")
            frame = result["results"][0]
            verify_observed(spec, frame["receipt"], frame["dimensions"])
            if frame["sha256"] != frame["receipt"].get("image_sha256"):
                raise ValueError("game and runner image hashes disagree")
    except BaseException as exc:
        error = str(exc) or type(exc).__name__
    finally:
        restored = original_plugins == tree_records(game / "BepInEx/plugins") and all(
            ((game / "BepInEx/config" / name).read_bytes() if (game / "BepInEx/config" / name).exists() else None) == data
            for name, data in controls.items())
        unchanged = file_record(args.character_file) == character_before
        discovery_unchanged = save_records() == saves_before
        try:
            verify_world(spec, args.world_db, args.world_fwl)
        except Exception as exc:
            unchanged = False; error = error or str(exc)
        lock.unlink()
        if not restored or not unchanged or not discovery_unchanged:
            error = error or "restoration verification failed"
        receipt = {"schema": "selfiestick-capture-receipt/v1", "status": "failed" if error else "passed",
                   "error": error, "requested": spec, "runner": runner, "result": result,
                   "restoration": {"pluginsAndControls": restored, "sourceSavesUnchanged": unchanged,
                                   "discoverySavesUnchanged": discovery_unchanged}}
        (out / "capture-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(str(out / "capture-receipt.json"))
    if error:
        raise ValueError(error)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        raise SystemExit(str(error))
