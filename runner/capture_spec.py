"""The portable selfiestick-capture/v1 contract. Standard library only."""
import copy
import hashlib
import json
import math
import re
from pathlib import Path

SCHEMA = "selfiestick-capture/v1"
PLUGIN_VERSION = "0.3.1"
FRAMES = ((16, 9), (1, 1), (9, 16))
HEADER = "# cluster_id\tshot\tcam_x\tcam_y\tcam_z\tyaw\tpitch\tenv\ttime\taim_x\taim_y\taim_z\tlabel\tmode\tfires\tflash\tlens_x\tlens_y\tlens_z\tvertical_fov\twidth\theight\troll\n"


def number(value, name, low=-1000000, high=1000000):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{name}: finite number in [{low}, {high}] required")
    return value


def vector(value, name):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{name}: three coordinates required")
    return [number(v, name) for v in value]


def dimensions(frame, longest=1920):
    if tuple(frame) not in FRAMES or longest not in (1920, 3840):
        raise ValueError("unsupported frame or size")
    return [round(longest * v / max(frame)) for v in frame]


def validate_camera(camera):
    if not isinstance(camera, dict):
        raise ValueError("camera required")
    vector(camera.get("lens"), "camera.lens")
    number(camera.get("yaw"), "camera.yaw", -360, 360)
    number(camera.get("pitch"), "camera.pitch", -89.9, 89.9)
    number(camera.get("roll", 0), "camera.roll", -180, 180)
    number(camera.get("verticalFov"), "camera.verticalFov", 1, 179)
    number(camera.get("targetDistance", 40), "camera.targetDistance", .1, 10000)
    if [camera.get("width"), camera.get("height")] not in [dimensions(f, s) for f in FRAMES for s in (1920, 3840)]:
        raise ValueError("unsupported capture dimensions")
    return camera


def validate(spec):
    if not isinstance(spec, dict) or spec.get("schema") != SCHEMA:
        raise ValueError("unsupported capture specification; expected " + SCHEMA)
    validate_camera(spec.get("camera"))
    source = spec.get("source", {})
    for key in ("photoId", "buildKey"):
        if not isinstance(source.get(key), str) or not source[key] or len(source[key]) > 256:
            raise ValueError("source." + key + " required")
    world = source.get("world", {})
    if not isinstance(world.get("id"), str) or not re.fullmatch(r'[^\\/:*?"<>|\x00-\x1f]{1,128}', world["id"]) or world["id"] in (".", ".."):
        raise ValueError("archive world identity required")
    for key in ("db", "fwl"):
        entry = world.get(key, {})
        if not re.fullmatch(r"[a-f0-9]{64}", str(entry.get("sha256", ""))) or type(entry.get("bytes")) is not int or entry["bytes"] <= 0:
            raise ValueError("archive " + key + " byte count and SHA-256 required")
    settings = spec.get("settings", {})
    if not re.fullmatch(r"[A-Za-z0-9_ -]{1,80}", str(settings.get("environment", ""))):
        raise ValueError("recorded environment required")
    number(settings.get("timeOfDay"), "settings.timeOfDay", 0, 1)
    if type(settings.get("fires")) is not bool:
        raise ValueError("settings.fires must be boolean")
    if settings.get("flashBearing") is not None:
        number(settings["flashBearing"], "settings.flashBearing", -360, 360)
    if spec.get("requiredPluginVersion") != PLUGIN_VERSION:
        raise ValueError("incompatible plugin contract; requires " + PLUGIN_VERSION)
    return spec


def from_photo(photo, camera):
    """Identity/settings are always resolved from the catalog, never supplied by a browser."""
    return validate({"schema": SCHEMA, "requiredPluginVersion": PLUGIN_VERSION,
                     "source": copy.deepcopy(photo["source"]), "camera": copy.deepcopy(camera),
                     "settings": copy.deepcopy(photo["settings"])})


def shot_list(spec):
    validate(spec)
    c, s = spec["camera"], spec["settings"]
    x, y, z = c["lens"]
    yaw, pitch = math.radians(c["yaw"]), math.radians(c["pitch"])
    distance = c.get("targetDistance", 40)
    aim = [x + math.sin(yaw) * math.cos(pitch) * distance,
           y - math.sin(pitch) * distance, z + math.cos(yaw) * math.cos(pitch) * distance]
    # Feet support streaming only. The plugin places the lens independently, without another offset.
    row = [0, "capture", x, y - 1.7, z, c["yaw"], c["pitch"], s["environment"], s["timeOfDay"],
           *aim, "Gallery capture", "exact", int(s["fires"]),
           "" if s.get("flashBearing") is None else s["flashBearing"],
           x, y, z, c["verticalFov"], c["width"], c["height"], c.get("roll", 0)]
    return HEADER + "\t".join(str(v) for v in row) + "\n"


def file_record(path):
    path = Path(path)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"bytes": path.stat().st_size, "sha256": digest}


def verify_world(spec, db, fwl):
    validate(spec)
    for key, path in (("db", db), ("fwl", fwl)):
        expected = spec["source"]["world"][key]
        if file_record(path) != {k: expected[k] for k in ("bytes", "sha256")}:
            raise ValueError("wrong archive world: " + key + " identity mismatch")


def verify_observed(spec, receipt, png_dimensions):
    """Reject a successful-looking image unless the game measured the authored projection."""
    c = spec["camera"]
    if receipt.get("plugin_version") != spec["requiredPluginVersion"]:
        raise ValueError("incompatible plugin version in capture receipt")
    if receipt.get("skipped") or not receipt.get("exact"):
        raise ValueError("exact capture failed: " + str(receipt.get("skipped", "missing exact receipt")))
    observed = receipt.get("observed", {})
    lens = vector(observed.get("lens"), "observed.lens")
    if math.dist(lens, c["lens"]) > .01:
        raise ValueError("lens placement mismatch")
    for key in ("yaw", "pitch", "roll"):
        actual = number(observed.get(key), "observed." + key)
        if abs((actual - c.get(key, 0) + 180) % 360 - 180) > .02:
            raise ValueError("orientation mismatch: " + key)
    if abs(number(observed.get("verticalFov"), "observed.verticalFov") - c["verticalFov"]) > .01:
        raise ValueError("vertical field of view mismatch")
    if png_dimensions != [c["width"], c["height"]] or [observed.get("width"), observed.get("height")] != png_dimensions:
        raise ValueError("capture dimensions mismatch")
    if receipt.get("camera_restored") is not True:
        raise ValueError("camera restoration not verified")
    return True
