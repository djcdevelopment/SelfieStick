# Shot Plans & TSV Poses Reference

Shot plans allow you to pre-define dozens or hundreds of photographic viewpoints and execute them headlessly.

---

## 📄 The TSV File Format

A shot plan is a tab-separated file (`.tsv`). Lines beginning with `#` are treated as comments:

```tsv
# cluster_id	shot	cam_x	cam_y	cam_z	yaw	pitch	env	time	aim_x	aim_y	aim_z	label	mode	fires	flash
101	001	-420.5	85.2	1250.3	45.0	15.0	Clear	0.64	-400.0	80.0	1270.0	main_gate	photo	true	false
```

### Column Specifications

| Column | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `cluster_id` | Integer | `101` | Identifier grouping frames belonging to the same architectural complex. |
| `shot` | String/Int | `001` | Shot index within the cluster. |
| `cam_x` | Float | `-420.5` | East/West player feet coordinate. |
| `cam_y` | Float | `85.2` | Elevation / altitude (lens rides ~1.7m above). |
| `cam_z` | Float | `1250.3` | North/South player feet coordinate. |
| `yaw` | Float | `45.0` | Camera azimuth angle in degrees clockwise from North (+Z). |
| `pitch` | Float | `15.0` | Camera tilt in degrees (positive angles look downwards). |
| `env` | String | `Clear` | Valheim environment to force (`Clear`, `Misty`, `Rain`, etc.). |
| `time` | Float | `0.64` | Day cycle fraction from `0.0` to `1.0` (`0.64` = afternoon sun). |
| `aim_x,y,z` | Float | `-400, 80, 1270` | 3D focal point coordinates the lens focuses towards. |
| `label` | String | `main_gate` | Descriptive filename slug used in the output PNG name. |
| `mode` | String | `photo` | Operational mode (`photo` for stills, `orbit` for sweeps). |
| `fires` | Boolean | `true` | When true, sweeps and lights nearby fireplaces and sconces. |
| `flash` | Boolean | `false` | When true, holds lightning strike lighting during shutter exposure. |

---

## 🎯 Deriving Coordinates from the Live Gallery

If you browse the [Valheim Era Archive Public Gallery](https://fx99.tail8e749c.ts.net/valheim/), clicking any photo's **"Open 3D Scene"** link reveals the exact `cam_*`, `yaw`, and `pitch` values used to produce that photograph. You can copy those coordinates directly into your own TSV to re-shoot any build!
