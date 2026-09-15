# SelfieStick :: Quick Start Guide

Take your first 4K architectural photograph in **under 60 seconds**.

---

## Option A: Interactive Photography (In-Game)

If you just want to take beautiful, unobstructed screenshots while playing:

1. **Install SelfieStick** via Thunderstore Mod Manager or extract `CameraProof.dll` to `Valheim/BepInEx/plugins/`.
2. Launch Valheim and load your world.
3. Press **`F5`** to open the in-game console.
4. Run these four commands:
   ```text
   camproof_hideplayer on     # Hides your Viking character mesh completely
   camproof_env Clear         # Locks the weather to crystal-clear skies
   camproof_time 0.64         # Sets golden mid-afternoon sunlight
   camproof_capture castle_01 # Takes high-res shutter and generates receipt
   ```
5. **Boom!** Your frame and cryptographic receipt are saved to:
   `Valheim/BepInEx/config/manual-captures/<timestamp>/`

### 💡 Pro-Tip: The 4-Mood Preset Sweep
Want to capture your build across morning, noon, sunset, and torchlit night automatically?
Position your camera and run:
```text
camproof_variantstills 1 45 basic
```
SelfieStick will freeze the camera and capture 4 beautifully balanced lighting variations in a single click.

---

## Option B: Unattended Batch Photography (The Archive Way)

If you want to photograph an entire world or cluster of builds headlessly:

1. Create a simple text file named `sample-shots.tsv` with your desired camera coordinates (see [examples/sample-shots.tsv](examples/sample-shots.tsv)):
   ```tsv
   # cluster_id	shot	cam_x	cam_y	cam_z	yaw	pitch	env	time	aim_x	aim_y	aim_z	label	mode	fires	flash
   1	001	120.5	45.0	-310.2	45.0	25.0	Clear	0.64	150.0	40.0	-280.0	gatehouse	photo	true	false
   ```
2. Run the automated PowerShell capture script:
   ```powershell
   .\Invoke-EraCapture.ps1 -World MyWorld -Character MyViking -Shots .\examples\sample-shots.tsv -Out .\out\my-shots
   ```
3. **What happens behind the scenes**:
   - Temporarily parks your existing mods so nothing interferes.
   - Boots Valheim directly, bypassing the 1.0 intro cinematic.
   - Clones your Viking to `<name>-kit` to keep your original save 100% untouched.
   - Teleports the camera rig to `(120.5, 45.0, -310.2)` at `yaw 45°` looking down `25°`.
   - Waits for terrain and physics to settle.
   - Takes a 4K screenshot (`0001_gatehouse.png`).
   - Writes SHA-256 hashes, coordinate metadata, and lens receipts to `receipt.json`.
   - Restores all your original mods and exits cleanly.

---

## 📚 Where to Go Next
- [In-Game Console Commands Guide](wiki/02-In-Game-Console-Commands.md)
- [Shot Plans TSV Format Reference](wiki/03-Shot-Plans-TSV-Reference.md)
- [Continuous Feed Mode & Proof Receipts](wiki/04-Continuous-Feed-Mode-and-Receipts.md)
- [Live Public Gallery on FX99](https://fx99.tail8e749c.ts.net/valheim/)
