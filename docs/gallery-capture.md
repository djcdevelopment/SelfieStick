# Gallery capture contract and proof

SelfieStick 0.3.1 implements `selfiestick-capture/v1`. [Runner instructions](../runner/README.md)
describe the extracted download. [capture_spec.py](../runner/capture_spec.py) is the
portable validator and shot-list serializer; [ExactCapture.cs](../ExactCapture.cs)
applies and measures the actual Unity camera.

The download preserves photo/build/world identity and inherited weather, time and
lighting. It records the absolute lens independently of player feet. The player is
placed 1.7 m below that lens to stream the world, then the render camera receives the
authored pose directly. Exact capture never performs legacy ground clearance or camera
recovery. Obstruction, unavailable world pieces and render failure are receipt failures.

A RenderTexture provides requested image dimensions independently of desktop size.
The still path clears temporal history and temporarily disables motion blur so a change
in lens or roll cannot smear the image using a previous frame. It restores the camera,
projection, render targets and motion-blur setting in `finally`.

## Use a downloaded still capture

Choose a photograph and composition in Steward's gallery or Creator/DM Capture mode,
then download and extract the entire ZIP. Keep `capture.json`, generated shot list,
reference thumbnail, launchers, DLLs and runner manifest together; dependency hashes
are checked before the game is touched. Read `capture.json` to identify the required
archive world and its `.db`/`.fwl` SHA-256 values. Supply that matching pair, a local
`.fch` character, a Valheim installation with BepInEx and a running Steam session.
Close Valheim before launching. The [Windows and Linux commands](../runner/README.md)
accept those paths explicitly and keep results on the local machine.

The runner copies the world and character under unique names. The original saves
are isolated at the client's actual discovery path, not merely a supplied input path.
Keep the launcher terminal open until it prints restoration status. In `results/`,
inspect the PNG and capture receipt together: the receipt records source photo/world,
requested and observed lens, angles, vertical FOV, dimensions, plugin/dependency
versions, PNG hash and original-save restoration. A requested exact pose is a claim
only when the observed values and PNG match; a blocked lens, wrong archive, wrong
plugin, absent local profile, busy game or render failure produces an explicit failure.
Following a power loss, preserve any `Valheim.selfiestick-*` parked-save directory
and lock until the original save location has been inspected; deleting it would
discard the original saves. The extracted Windows launcher passed a real capture;
AM4 passed the same pinned runner and plugin through Linux game capture proof.

The portable runner verifies archive `.db` and `.fwl` bytes/hash and all dependency
hashes before mutation. Disposable world and character copies have unique filenames.
The plugin requires those exact files with local save authority. Windows parks the
original Unity save directory while the copied files occupy its fixed discovery path;
Linux isolates discovery with `XDG_CONFIG_HOME`. Controls, plugins and Windows PlayerPrefs
are restored. The wrapper checks the actual save discovery tree and Steam character
mirrors as well as the supplied source files. A process lock prevents overlapping runs.

## Candidate builds and tests

`runner/build_runner.py` takes explicit camera/portal DLL paths and a fresh output
directory. Its release manifest and every-file runner manifest pin exact bytes. The
runner source, launchers and manifests use LF checkout rules in `.gitattributes` so
the same pinned ZIP bytes and Linux shebangs survive a fresh Windows worktree.
Baseline camera-kit transfer under `provenance/` includes the source working snapshot
on base revision `833fc59e5b0c0347f0220bf928eef9e418178a99`; it does not silently pull
later Baseline changes. The snapshot ZIP SHA-256 is
`8a5e3703759d29cf19c66edce2df3fb0c955266612042211ba0336926a4d8b49` (16,737 bytes).

Run `python -m unittest discover -s tests -v` and build `CameraProof.csproj` against
the intended local Valheim installation. `tools/check_camera_fixture.py` verifies the
shared Steward camera fixture through explicit `--artifact` and `--pin` inputs.
`tools/prove_capture.py` takes the pinned runner and real archive inputs; one game load
checks nine lens/frame combinations at 1920, three at 3840 (including 12° roll), and
two legacy rows. It writes measured PNG/camera receipts and before/after save evidence.

See `docs/evidence/gallery-capture-20260915.json` for candidate hashes and measured
results. Candidates include working changes; publication is a separate rollout step.

## Why this contract and what follows

The browser knows an authored **lens** pose, not a safe player-feet position. Treating
those as the same value, or applying the historical 1.7 m eye-height conversion twice,
would move the photograph. Composer captures therefore place the render camera at
the specification's lens and use lower player feet only for world streaming. Legacy
sixteen-column rows retain their older placement/recovery path. Vertical FOV and
width/height are measured from the actual game camera; browser frustum geometry alone
cannot prove the PNG.

The first release is one still per download. After source is pushed, publish a
clean-revision runner/DLL pin and repeat real capture if those bytes change. Steward
then stages the exact runner, archive catalog and measured OMEN/AM4 receipts before
public downloads. [The fleet plan](https://github.com/djcdevelopment/baseline/blob/main/docs/gallery-capture-program-plan.md)
names the release gate. Moving-camera capture needs a time-sampled path in a later
contract and observed game output; video, fisheye, panorama, physical aperture and
cross-world reuse are not implemented by this still runner.

## Initial OMEN isolation incident

The first 0.3.0 OMEN tests incorrectly assumed that `-savedir` controlled client save
discovery. The game selected cloud character **Questy** and the existing local
**ComfyEra11**, then saved them. The earlier r1 restoration claims are invalid; they
checked the supplied source files rather than the saves actually selected by the game.

Evidence and post-run copies are preserved under
`artifacts/incident-omen-20260915/`. Questy was 35,705 bytes before the first test and
44,868 bytes afterward. Its `.old` was overwritten during the second test. Several
existing local world chunks and the current save manifest also changed. No exact
pre-run Questy backup was found. Derek confirmed Questy is capture-only. Its current
save matches the preserved post-run copy and remains in place; no older backup was
restored. Derek also confirmed the existing local ComfyEra11 world is capture-only.
Its current files match the preserved post-run copies and remain in place. Only an
older flat archive backup was found, not an exact pre-run copy. Both owner decisions
are recorded in [the disposition addendum](evidence/save-incident-disposition-20260915.json).
Recovery disposition is resolved. The original writes were not reversed, and the
initial r1 restoration claim remains invalid independently of corrected runner proof.

0.3.1 refuses the wrong profile before world entry. The corrected strict runs check
unique local identities and the actual original save directories before and after.
The r3 pose/restoration proof exposed motion blur on a rotated still during visual
review; the subsequent candidate resets that history. Only final reviewed candidate
receipts are eligible for the download gate.
