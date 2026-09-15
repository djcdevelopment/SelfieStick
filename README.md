# SelfieStick

> **The automated 4K photographic camera engine for Valheim: sub-centimetre pose accuracy, lighting and weather control, and cryptographic proof receipts for world archives.**

[![Valheim 1.0](https://img.shields.io/badge/Valheim-1.0-blue.svg)](#)
[![BepInEx 5](https://img.shields.io/badge/BepInEx-5.4.2202-green.svg)](#)
[![Hardware Verified](https://img.shields.io/badge/OMEN%20Verified-0%20Errors-purple.svg)](#)
[![Archify Diagram](https://img.shields.io/badge/Archify-Showcase%209%2F9-0891b2.svg)](https://github.com/djcdevelopment/SelfieStick/blob/main/docs/selfie-stick-architecture.html)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)
[![Client-Side Safe](https://img.shields.io/badge/Multiplayer-100%25%20Client--Side-success.svg)](#)
[![AI Assisted](https://img.shields.io/badge/Development-AI--Assisted-blueviolet.svg)](#)

---

## 📑 Table of Contents

- [🎯 The Origin & Why This Mod Exists](#-the-origin--why-this-mod-exists)
  - [🌐 Live Public Showcase Gallery](#-live-public-showcase-gallery)
  - [📖 The Photography Essays (Background & Design)](#-the-photography-essays-background--design)
- [🏗️ Visual System Architecture (Archify)](#️-visual-system-architecture-archify)
- [⚡ Core Features](#-core-features)
  - [1. Unattended Headless Photography](#1-unattended-headless-photography)
  - [2. Sub-Centimetre Camera Rig & Optics](#2-sub-centimetre-camera-rig--optics)
  - [3. Atmosphere, Sun Angle & Flash Sweeps](#3-atmosphere-sun-angle--flash-sweeps)
  - [4. Stabilization & Physics Settling Engine](#4-stabilization--physics-settling-engine)
  - [5. Valheim 1.0 Headless Shields](#5-valheim-10-headless-shields)
  - [6. Continuous Feed Mode (Hot Loop)](#6-continuous-feed-mode-hot-loop)
  - [7. Cryptographic Proof Receipts](#7-cryptographic-proof-receipts)
  - [8. Interactive Console CLI Suite](#8-interactive-console-cli-suite)
- [🎮 Hotkey & CLI Quick Reference](#-hotkey--cli-quick-reference)
- [⚙️ Configuration & Intake Reference](#️-configuration--intake-reference)
- [💻 In-Game Console Commands (`F5`)](#-in-game-console-commands-f5)
- [🔬 Hardware Verification (OMEN Rig)](#-hardware-verification-omen-rig)
- [📋 Changelog](#-changelog)
- [📦 Installation Guide](#-installation-guide)
- [🛠️ Building from Source](#️-building-from-source)
- [📄 License](#-license)

---

## 🎯 The Origin & Why This Mod Exists

Valheim community servers generate massive worlds holding millions of objects across multiple years. Recording and preserving these architectural achievements at photographic fidelity requires positioning cameras with sub-centimetre precision, locking uniform sun angles and weather states, waiting for terrain LOD and physics to settle, and cryptographically proving the exact coordinates of every frame.

**SelfieStick** (powered by the underlying `CameraProof.dll` plugin engine) is the automated capture and telemetry tool developed to photograph the Valheim Era Archives.

### 🌐 Live Public Showcase Gallery

See the live results of this photography engine in action:
* **[Valheim Era Archive Public Gallery](https://fx99.tail8e749c.ts.net/valheim/)**: Thousands of 4K photographs with clickable 3D scene camera links, pitch/yaw telemetry, and exact lens receipts.
* **[Creator & Builder Stats](https://fx99.tail8e749c.ts.net/valheim/creators/stats/)**: Spatial build clustering, contributor kinship, and comprehensive builder directory attribution.

### 📖 The Photography Essays (Background & Design)

Read the technical and artistic history behind the engine in the 3-part essay series:
1. **Part 1: [Photographing a world nobody had time to look at](https://djcdevelopment.github.io/baseline/selfie-stick/)** — Automating cameras across multi-million-object saves.
2. **Part 2: [Standing where the builders stood](https://djcdevelopment.github.io/baseline/selfie-stick/part-2/)** — Reverse-engineering vantage points, player paths, and architectural sightlines.
3. **Part 3: [The light they built for](https://djcdevelopment.github.io/baseline/selfie-stick/part-3/)** — Controlling weather, sun azimuth, and lighting sweeps to capture builds as their creators saw them.

---

## 🏗️ Visual System Architecture (Archify)

Archify verified showcase diagram illustrating the unattended boot, camera rig mechanics, weather synchronization, and cryptographic receipt pipeline:

[![SelfieStick Architecture Preview](https://raw.githubusercontent.com/djcdevelopment/SelfieStick/main/docs/selfie-stick-architecture.visual-check.1440x900.dark.png)](https://github.com/djcdevelopment/SelfieStick/blob/main/docs/selfie-stick-architecture.html)

👉 **[Open Live Interactive Archify Diagram](https://github.com/djcdevelopment/SelfieStick/blob/main/docs/selfie-stick-architecture.html)** ([Live Web Preview](https://htmlpreview.github.io/?https://github.com/djcdevelopment/SelfieStick/blob/main/docs/selfie-stick-architecture.html)) *(Dark/Light themes, guided view inspection, and node reachability)*

---

## ⚡ Core Features

### 1. Unattended Headless Photography
Point the runner at a world save and character. SelfieStick hooks `FejdStartup`, loads the specified world and character without human intervention, places the camera, waits for world settle, captures the frame, and closes cleanly upon completion.

### 2. Sub-Centimetre Camera Rig & Optics
Positions the lens at precise spatial coordinates `(x, y, z)` with explicit `yaw` (clockwise from +Z), `pitch` (positive downwards), field-of-view, and an automatic 1.7m player eye-height offset. Completely hides the character mesh during the exposure (`_hidePlayerForScreenshots`) so portraits and architecture remain unobstructed.

### 3. Atmosphere, Sun Angle & Flash Sweeps
- **Weather Enforcement**: Locks environment states (`Clear`, `Misty`, `Rain`, `ThunderStorm`, etc.) via `EnvMan` to guarantee identical lighting.
- **Sun Angle**: Sets exact time-of-day fractions (`0.0` to `1.0`, e.g. `0.64` for afternoon sun).
- **Light & Flash Sweeps**: Automatically illuminates surrounding light prefabs within an 80m radius and holds simulated lightning strikes (`FlashHoldSeconds = 1.2s`) to properly expose subterranean or shadowed builds.

### 4. Stabilization & Physics Settling Engine
Never shoots prematurely. Before releasing the shutter, SelfieStick holds the camera in place (`_holdAt`) and waits for terrain chunk generation, vegetation placement, dynamic lighting, and rigidbodies to reach equilibrium.

### 5. Valheim 1.0 Headless Shields
- **Cinematic Bypass**: Skips Valheim 1.0's mandatory startup cinematic.
- **Cloth Crash Guard**: Suppresses MagicaCloth physics evaluation during initial spawn, eliminating the known Linux/Wine/Proton driver crash.
- **Character Save Isolation**: Automatically plays cloned characters (`<name>-kit`) to eliminate the risk of Steam Cloud overwriting your primary Viking saves.

### 6. Continuous Feed Mode (Hot Loop)
Loading a multi-gigabyte world with 7+ million objects takes several minutes. SelfieStick's **Feed Mode** (`0.2.3+`) keeps the world resident in memory and continuously polls a designated feed directory. Dropping new shot plans into the folder executes them immediately without rebooting the game.

### 7. Cryptographic Proof Receipts
Every frame output is accompanied by an immutable cryptographic receipt in `shotplan-receipts.jsonl` and `receipt.json`:
- Client build number (e.g. `25253764`).
- SHA-256 hashes of all active plugins and output images.
- Exact lens coordinates, aim point, yaw, pitch, weather environment, and settling clearance.

### 8. Interactive Console CLI Suite
Full in-game console commands under the `camproof_*` namespace for live scene composing, teleportation, lighting dumps, and manual captures.

---

## 🎮 Hotkey & CLI Quick Reference

| Command / Key | Action | Description |
| :--- | :--- | :--- |
| **`camproof_status`** | **Camera Telemetry** | Dumps active camera position, yaw, pitch, and settle status. |
| **`camproof_tp <x> <y> <z>`** | **Teleport Camera** | Teleports camera to exact coordinates and writes movement receipt. |
| **`camproof_move`** | **Relative Shift** | Adjusts camera position incrementally along coordinates. |
| **`camproof_env <name>`** | **Lock Environment** | Forces weather (`Clear`, `Rain`, `ThunderStorm`, or `noforce`). |
| **`camproof_time <0..1>`** | **Lock Time** | Sets time of day (`0.25` morning, `0.5` noon, `0.64` afternoon, `off`). |
| **`camproof_hideplayer <on/off>`** | **Hide Player** | Toggles local character mesh visibility for clean framing. |
| **`camproof_stills <N> <sec>`** | **Batch Stills** | Captures still series across waypoints with settle delays. |
| **`camproof_variantstills`** | **Mood Sweep** | Captures active frame across 4 lighting and weather presets. |
| **`camproof_capture <label>`** | **Manual Shutter** | Captures high-res screenshot and writes receipt file. |
| **`camproof_sky`** | **Sky Dump** | Dumps sun and moon vector angles per time of day to JSON. |
| **`camproof_lights`** | **Light Dump** | Dumps every light prefab and environment definition. |

---

## ⚙️ Configuration & Intake Reference

### Shot Plan Intake (`shotplan.tsv`)
Tab-separated camera poses (one frame per row):
```tsv
# cluster_id	shot	cam_x	cam_y	cam_z	yaw	pitch	env	time	aim_x	aim_y	aim_z	label	mode	fires	flash
104	001	-420.5	85.2	1250.3	45.0	15.0	Clear	0.64	-400.0	80.0	1270.0	keep	photo	true	false
```

### Orbit Request Intake (`orbit-request.json`)
```json
{
  "world": "MyWorld",
  "character": "MyViking-kit",
  "quit_when_done": true
}
```

---

## 🔬 Hardware Verification (OMEN Rig)

**SelfieStick** was tested and validated on sovereign hardware (**OMEN**: Intel Core Ultra 9 285K, Dual Intel Arc Pro B70 GPUs, Steam Valheim 1.0.12 build `25253764`):

```powershell
==========================================================
   DeepNorthTesting :: Valheim 1.0 Autonomous Launcher    
==========================================================
[OK] Valheim running with PID: 41280 (<8s to interactive menu)
[PASS] 0 Errors, 0 Exceptions, 0 Patch Failures detected.
[PASS] CameraProof 0.2.5 loaded and armed cleanly.
[PASS] Shot roundtrip verification: lens, yaw, pitch equal AM4 archive to the centimetre.
```

Verified BepInEx Chainloader Log:
```text
[Info   :   BepInEx] Loading [Camera Proof 0.2.5]
[Info   :Camera Proof] Camera Proof loaded. dev.djc.camera-proof v0.2.5.
[Info   :Camera Proof] Rig armed. Feed mode active.
```

---

## 📋 Changelog

### v0.2.6 (2026-09-15)
- **Thunderstore Media Fix**: Replaced relative image links with absolute repository URLs to render the Archify system architecture diagram directly on Thunderstore.
- **Mermaid Block Cleanup**: Removed raw plaintext mermaid block for cleaner store presentation.
- **Repository Launch**: Official GitHub repository live at `djcdevelopment/SelfieStick`.

### v0.2.5 (2026-09-12)
- **Local Character Isolation**: Auto-boot plays local copy `<name>-kit` by file stem, eliminating Steam Cloud overwrite collisions.
- **Valheim 1.0 Compatibility**: Verified against client build `25253764` (1.0.12) and `25185596` (1.0.7).
- **Public fx99 Gallery Integration**: Full provenance tracking linking captures directly to public archive galleries.

### v0.2.4 (2026-09-11)
- **Pose & Runclips Commands**: Interactive recording of the active viewpoint into TSV shot plans and multi-waypoint clip playback.

### v0.2.3 (2026-09-10)
- **Continuous Feed Mode**: World stays resident in memory; polls and shoots incoming plans dropped into the feed directory without game restarts.

### v0.2.2 (2026-09-08)
- **MagicaCloth Spawn Skip**: Suppresses equipment cloth physics during character spawn, resolving the Linux/Proton crash on 1.0 worlds.

### v0.2.1 (2026-09-06)
- **1.0 Intro Cinematic Bypass**: Bypasses the new Valheim 1.0 cinematic sequence for instant automated headless execution.

---

## 📦 Installation Guide

### Via Mod Manager (Recommended)
Install using **Thunderstore Mod Manager** or **r2modman**:
1. Search for `SelfieStick` in the Online tab.
2. Click **Download** with dependencies (**BepInExPack Valheim**).

### Manual Installation
1. Ensure **BepInExPack Valheim** is installed in your game directory (`Valheim/BepInEx/core` exists).
2. Download `SelfieStick-0.2.6.zip`.
3. Extract `CameraProof.dll` directly into your `Valheim/BepInEx/plugins/` directory.

---

## 🛠️ Building from Source

```powershell
git clone https://github.com/djcdevelopment/SelfieStick.git
cd SelfieStick
dotnet build -c Release -p:ValheimDir="C:\Program Files (x86)\Steam\steamapps\common\Valheim"
```

The compiled binary lands at `bin/Release/net472/CameraProof.dll`.

---

## 📄 License

MIT License. See `LICENSE` for details.
