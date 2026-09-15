# Continuous Feed Mode & Proof Receipts

When photographing multi-gigabyte worlds holding millions of objects, loading the world can take several minutes. **Feed Mode** keeps Valheim resident in memory so you can shoot new batches continuously with zero downtime.

---

## ⚡ How Feed Mode Works

1. In your configuration or command parameters, set `quit_when_done: false`.
2. SelfieStick designates a feed drop directory:
   `Valheim/BepInEx/config/feed/`
3. As long as the game remains running, dropping a new `.tsv` shot plan into `feed/` causes SelfieStick to immediately:
   - Read the plan.
   - Fly to each camera pose sequentially.
   - Wait for chunks and physics to settle.
   - Shutter each frame.
   - Write receipt entries to `shotplan-receipts.jsonl`.
   - Move the plan to `feed/done/` and wait for the next input!

This hot loop enabled photographing **84 builds and 601 frames in a single uninterrupted session** during the historical era archive passes.

---

## 🧾 Cryptographic Receipts (`receipt.json`)

Every completed photograph produces a cryptographic receipt proving the authenticity of the shot:

```json
{
  "frame": "0001_castle_gate.png",
  "sha256": "3a7b9e...01c4",
  "game_build": "25253764",
  "plugin_version": "0.2.7",
  "camera": {
    "pos": [-420.5, 86.9, 1250.3],
    "yaw": 45.0,
    "pitch": 15.0,
    "fov": 65.0
  },
  "environment": {
    "name": "Clear",
    "time_fraction": 0.64
  },
  "settle": {
    "duration_seconds": 8.5,
    "unloaded_chunks": 0
  }
}
```

Receipts guarantee that every photo in your portfolio or community archive was captured at identical optical geometry without manual camera warping or post-processing artifacts.
