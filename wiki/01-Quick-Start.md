# Quick Start & First Photograph

Welcome to **SelfieStick** — the automated 4K photographic camera engine for Valheim!

Whether you want to snap clean, character-free architectural shots of your personal builds or headlessly archive multi-gigabyte community worlds, this guide gets you running in under two minutes.

---

## ⚡ 1-Minute In-Game Photography

The quickest way to use SelfieStick is directly inside your active Valheim session:

1. **Install SelfieStick** via the Thunderstore Mod Manager or place `CameraProof.dll` in `BepInEx/plugins/`.
2. Load any Valheim character and world.
3. Press **`F5`** to open the in-game console.
4. Use these commands to frame and capture:

| Command | What it does |
| :--- | :--- |
| `camproof_hideplayer on` | Hides your character model so nothing blocks the camera. |
| `camproof_env Clear` | Overrides fog/rain with crystal-clear blue skies. |
| `camproof_time 0.64` | Locks warm, golden mid-afternoon sunlight. |
| `camproof_capture my_build` | Takes a 4K frame and outputs an exact coordinate receipt. |

Your photo and receipt land in:
`Valheim/BepInEx/config/manual-captures/<timestamp>/`

---

## 📸 The 4-Mood Variation Sweep

Want to showcase how your fortress looks under different times of day and weather?

Point your camera at your build, open `F5`, and run:
```text
camproof_variantstills 1 45 basic
```

SelfieStick locks the camera position and automatically shoots 4 mood presets:
- **Morning Clear** (warm sunrise)
- **Mid-Day** (high sun, maximum visibility)
- **Afternoon** (dramatic shadows)
- **Night Sweep** (fires and sconces illuminated across an 80m radius)

---

## 🤖 Headless Batch Photography

If you have coordinates or an entire world to photograph without human intervention, use the companion runner script:

```powershell
.\Invoke-EraCapture.ps1 -World MyWorld -Character MyViking -Shots .\examples\sample-shots.tsv -Out .\out\my-shots
```

This runs completely unattended:
- Bypasses the 1.0 intro sequence.
- Prevents equipment cloth physics crashes at spawn.
- Plays a safe clone (`<name>-kit`) to isolate your cloud save.
- Takes the photos, logs cryptographic receipts, and restores your game state.
