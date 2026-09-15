# In-Game Console Commands Reference

SelfieStick provides a dedicated suite of console commands under the `camproof_*` prefix. Press **`F5`** in-game to access them.

---

## 🎮 Command Table

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `camproof_status` | *none* | Dumps the active camera's position `(x, y, z)`, yaw, pitch, field of view, and settle state to `camera-proof-status.json`. |
| `camproof_hideplayer` | `on` \| `off` | Hides or shows the local player's model, equipment, and weapons. |
| `camproof_tp` | `<x> <y> <z>` | Teleports the player and camera rig to exact coordinates and writes movement telemetry to `camera-proof-move.json`. |
| `camproof_move` | `[x y z]` | Shifts the camera relatively along coordinate axes. |
| `camproof_env` | `<name>` \| `noforce` | Forces weather to any Valheim environment (`Clear`, `Misty`, `Rain`, `ThunderStorm`, `Twilight_Clear`, etc.). |
| `camproof_time` | `<0.0..1.0>` \| `off` | Sets exact time of day (`0.25` = 6 AM, `0.5` = Noon, `0.64` = 3:30 PM, `0.9` = Dusk). |
| `camproof_capture` | `[label]` | Takes a high-resolution screenshot with a receipt file recording camera telemetry and active plugin hashes. |
| `camproof_variantstills`| `[count] [fov] [preset]` | Captures the current view across 4 mood presets (Morning, Noon, Sunset, Night). |
| `camproof_stills` | `[count] [delay]` | Automatically steps through predefined waypoints and takes stills with a stabilization pause. |
| `camproof_sky` | *none* | Dumps sun, moon, and horizon vector angles for each time fraction to `camera-proof-sky.json`. |
| `camproof_lights` | *none* | Dumps every light prefab and 39 environment definitions to `camera-proof-lights.json`. |
| `camproof_envs` | *none* | Outputs a complete list of valid environment names supported by the active world to `camera-proof-envs.json`. |

---

## ⌨️ Hotkeys & Shortcuts

- **`F8`**: Instant manual shutter capture (emits PNG + receipt).
- **`PageUp` / `PageDown`**: Step forward / backward through loaded waypoints.
- **`F7`**: Intentionally unbound to ensure compatibility with third-party quest and control mods.
