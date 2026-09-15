# SelfieStick :: 40-Second Video Showcase Storyboard & Production Guide
> **High-impact video blueprint for Thunderstore, Reddit (r/valheim), YouTube Shorts, and X/Twitter.**

---

## 🎯 Video Thesis & The Psychological Hook

- **The Frustration**: You spent weeks or months creating a breathtaking fortress, mountain castle, or sprawling village in Valheim. But capturing it with vanilla controls is painful: your character's back blocks the view, the weather turns into foggy rain, torchlight fails in dark corners, and shaky manual angles never do your architecture justice.
- **The Solution**: **SelfieStick** gives you an automated 4K architectural camera rig: instant player mesh hiding, sub-centimetre spatial placement, locked sun angles, weather overrides, lighting sweeps, and unattended batch photography with mathematical receipts.
- **Target Duration**: **36–42 Seconds** (high-conversion format for social previews and store frontpages).

---

## 🎬 Shot-by-Shot Storyboard

| Timestamp | Visual Action | On-Screen Text Overlay | In-Game Sound & Audio |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:07**<br/>*(The Struggle)* | **Clumsy Vanilla Photography**: Player on a grand castle terrace trying to frame a shot.<br/>The camera is awkward, player character's Viking helmet blocks 30% of the screen, and heavy gray fog rolls in, ruining the view. | `PHOTOGRAPHING IN VALHEIM:`<br/>`Awkward angles, bad weather, character in the way 🌧️` | Footsteps on stone → heavy rain & thunder ambiance → comical vinyl scratch. |
| **0:07 - 0:15**<br/>*(The Transformation)* | **Engage SelfieStick**: Cut to console (`F5`). Fast-type `camproof_hideplayer on`.<br/>Player mesh instantly vanishes! Camera lifts smoothly into a sweeping aerial elevation above the ramparts. | `WITH SELFIESTICK:`<br/>`Instant character concealment & sub-centimetre rig 📐` | Whoosh sound effect → majestic Nordic brass & horn theme begins (e.g. ambient Viking orchestral). |
| **0:15 - 0:23**<br/>*(Sun & Weather Lock)* | **Lighting & Mood Sweeps**: Same castle courtyard.<br/>Type `camproof_env Clear` and `camproof_time 0.64`.<br/>The sky clears into crystal-blue atmosphere; golden afternoon sun strikes the timber gables.<br/>Cut to night: an 80m flash sweep lights every wall sconce and hearth simultaneously (`camproof_variantstills`). | `Instant weather & sun lock`<br/>`Atmospheric lighting sweeps ☀️🔥` | Sunbeam chime → crackling fire ignition sound. |
| **0:23 - 0:31**<br/>*(The Archive Engine)* | **Unattended Batch Photography**: Split screen: terminal running `Invoke-EraCapture.ps1` on left; right side cuts through 4 magnificent historical archive builds in 4K.<br/>Camera automatically lands at exact centimetre coordinates, settles, and shutters. | `Shoot 100+ architectural frames unattended`<br/>`Continuous Feed Mode: No game restarts ⚡` | Mechanical camera shutter clicks (`ka-chink!`) in sync with each architectural cut. |
| **0:31 - 0:36**<br/>*(The Proof Ledger)* | **Cryptographic Verification**: Zoom into a generated `receipt.json` card overlaying the photo:<br/>Showing pitch `38.2°`, yaw `120.0°`, clearance `14.2m`, and SHA-256 hashes matching the public FX99 archive gallery. | `Cryptographic receipts for every frame`<br/>`Clickable 3D scene links on FX99 🏛️` | Modern tech scan / digital confirmation chime. |
| **0:36 - 0:41**<br/>*(Call to Action)* | **Title Card & Logo**: Clean dark slate card displaying the amber camera aperture badge, Thunderstore link, and GitHub badge. | **SelfieStick**<br/>`The Camera Behind the Valheim Era Archives`<br/>`Free on Thunderstore • Mod by djcdevelopment` | Epic orchestral crescendo → fade to black. |

---

## 🎮 10-Minute In-Game Recording Setup Runbook

You can easily capture all video footage in single-player or dev mode in under 10 minutes:

### 1. Scene 1: The Vanilla Struggle (Terrace Shot)
1. Load any village or fortress world.
2. Force bad weather via console:
   ```text
   devcommands
   env Rain
   ```
3. Walk onto a high ledge. Turn the camera around your character so your cloak and helmet block the castle view.
4. Record 5 seconds of frustrated camera wiggling.

### 2. Scene 2: The Clean Aerial Rig
1. Open console (`F5`) and run:
   ```text
   camproof_hideplayer on
   camproof_env Clear
   camproof_time 0.64
   ```
2. Character mesh disappears completely.
3. Use fly mode (`fly`) or `camproof_tp <x> <y> <z>` to glide smoothly into a cinematic 45-degree angle overlooking the build.
4. Record the transformation from foggy clutter to clean golden architecture!

### 3. Scene 3: The Night Atmosphere Sweep
1. Transition to dusk/night:
   ```text
   camproof_time 0.95
   camproof_env Clear
   ```
2. Type in console:
   ```text
   camproof_variantstills 1 20 basic
   ```
3. Watch the engine automatically cycle through the 4 lighting presets and capture crisp frames with lighting hold!

### 4. Scene 4: The Terminal & Gallery Showcase
1. Run a 3-shot sample pass with the runner:
   ```powershell
   .\Invoke-EraCapture.ps1 -World MyWorld -Character MyViking -Shots .\examples\sample-shots.tsv -Out .\out\demo
   ```
2. Screen-record the PowerShell terminal printing the verified SHA-256 receipts alongside the output PNGs in File Explorer.
3. Cut to a 2-second screen capture of the live public gallery at `https://fx99.tail8e749c.ts.net/valheim/` showing the interactive 3D camera link.
