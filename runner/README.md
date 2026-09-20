# Local gallery capture

Extract the entire download. You need Python 3.11 or later, a local Valheim client
with BepInEx, Steam running, the archive `.db`/`.fwl` pair named in `capture.json`,
and a local `.fch` character file. Close Valheim before starting.

Windows (PowerShell):

```powershell
.\Capture.ps1 -GameRoot 'D:\Games\Valheim' -WorldDb 'D:\Archives\ComfyEra11.db' -WorldFwl 'D:\Archives\ComfyEra11.fwl' -CharacterFile 'D:\Characters\Viking.fch'
```

Linux (a graphical desktop session):

```sh
sh capture.sh --game-root "$HOME/games/valheim" --world-db /archives/ComfyEra11.db --world-fwl /archives/ComfyEra11.fwl --character-file /archives/Viking.fch
```

The runner verifies dependency hashes and exact archive bytes before launching.
It plays unique disposable local copies. Windows saves are parked intact while a
temporary copy occupies Unity's fixed save path; Linux uses an isolated XDG path.
The plugin refuses a missing or cloud save instead of selecting another profile.
Plugins, control files, Windows preferences and the original save directory are
restored after exit. Leave the terminal open until restoration completes. Following
a power loss, inspect the lock and `Valheim.selfiestick-*` directory before restarting;
that parked directory contains the original saves. Never delete it to clear a lock.

`results/` contains the PNG, requested composition, measured camera values, source
identity, dependency hashes and restoration receipt. Nothing is uploaded. Coverage
in the browser is an estimate from archived scene geometry; the game renders the
finished photograph. Obstructed lenses or failed placement produce a failure receipt,
never a silently adjusted "exact" composition.

The manifest pins every runner file and dependency, while `capture.json` pins the
source photo/build, archive `.db`/`.fwl` bytes and SHA-256, inherited weather/time/
lighting, absolute lens pose, vertical FOV and output dimensions. A wrong world or
plugin version fails before capture. `results/` stays local; inspect the receipt's
requested/observed camera values, image hash and restoration fields before calling
a PNG an exact match. The gallery's yellow coverage pyramid is a preview of available
archived geometry, not a reproduction of the game render.

This runner serves one still composition per download. Source and proof promotion
for public gallery downloads is tracked in the
[fleet plan](https://github.com/djcdevelopment/baseline/blob/main/docs/gallery-capture-program-plan.md);
moving-camera recording needs a later versioned contract and real game proof.

## Capture contract and existing shot lists

`capture.json` uses `selfiestick-capture/v1`, plugin 0.3.2. The camera records absolute
**lens** xyz (Unity world coordinates), yaw clockwise from +Z, positive downward
pitch, roll, vertical FOV, width, height and an aim distance. Supported longest edges
are 1920 and 3840; frames are 16:9, 1:1 and 9:16. Source identity includes photo/build,
world ID, and the byte counts and SHA-256 of both archive files. Weather, time of day,
fire lighting and optional flash bearing are inherited from the reference receipt.

The original sixteen shot-list columns keep their meanings. Optional columns 17–23
are `lens_x lens_y lens_z vertical_fov width height roll`. Explicit lenses require
all projection fields. With no lens columns, the existing feet placement and recovery
behavior remains. Optional FOV and dimensions also work independently of explicit
lens placement. Composer rows use feet = lens − (0, 1.7, 0) only to stream the world;
the render camera is placed at the lens exactly once.

Legacy CLI remains available as `capture_kit.py` and `Invoke-EraCapture.ps1`.
Use `capture.py` for verified archive identity and disposable composer captures.
