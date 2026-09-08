# Approved fixed Blender script for the Self Image relay.
# PURPOSE: reversible broad-form proportion study from the untouched audited CC0 body.
# This is NOT a registered photographic fit, Stage-A promotion, or production UV source.

import bpy
import json
import math
import os
from mathutils import Vector

OUTPUT_DIR = globals().get("OUTPUT_DIR")
if not OUTPUT_DIR:
    raise RuntimeError("Relay did not provide OUTPUT_DIR.")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_NAME = "GEO-body_female_realistic"
CANDIDATE_NAME = "VERA_PROPORTION_STUDY_V1"
EXPECTED_VERTICES = 42342
EXPECTED_POLYGONS = 84680

body = bpy.data.objects.get(BASE_NAME)
if body is None or body.type != "MESH":
    raise RuntimeError("Untouched audited CC0 body is not present.")
if len(body.data.vertices) != EXPECTED_VERTICES or len(body.data.polygons) != EXPECTED_POLYGONS:
    raise RuntimeError("Baseline topology/count guard failed.")
if any(abs(v) > 1e-8 for v in body.location):
    raise RuntimeError("Baseline location is not identity.")
if any(abs(v) > 1e-8 for v in body.rotation_euler):
    raise RuntimeError("Baseline rotation is not identity.")
if any(abs(float(v) - 1.0) > 1e-8 for v in body.scale):
    raise RuntimeError("Baseline scale is not identity.")

# Reruns are deterministic and may replace ONLY the exact study candidate.
old = bpy.data.objects.get(CANDIDATE_NAME)
if old is not None:
    old_mesh = old.data if old.type == "MESH" else None
    bpy.data.objects.remove(old, do_unlink=True)
    if old_mesh is not None and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

candidate = body.copy()
candidate.data = body.data.copy()
candidate.name = CANDIDATE_NAME
candidate.data.name = CANDIDATE_NAME + "_MESH"
bpy.context.scene.collection.objects.link(candidate)

coords = [v.co.copy() for v in body.data.vertices]
zmin = min(v.z for v in coords)
zmax = max(v.z for v in coords)
height = zmax - zmin
if not (1.60 < height < 1.68):
    raise RuntimeError("Unexpected baseline height; refusing proportion study.")
height_factor = height / 1.70


def clamp01(t):
    return max(0.0, min(1.0, float(t)))


def smoother(t):
    # quintic smoothstep
    t = clamp01(t)
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def window(z, a, b, c, d):
    return smoother((z - a) / (b - a)) * (1.0 - smoother((z - c) / (d - c)))


CURVE_Z = [0.00, 0.48, 0.60, 0.72, 0.82, 0.92, 1.035, 1.12, 1.24, 1.34, 1.42, 1.70]
CURVE_X = [0.00, 0.00, 0.005, 0.065, 0.14, 0.19, 0.30, 0.20, 0.08, 0.025, 0.00, 0.00]


def smooth_curve(z):
    if z <= CURVE_Z[0]:
        return CURVE_X[0]
    if z >= CURVE_Z[-1]:
        return CURVE_X[-1]
    for i in range(len(CURVE_Z) - 1):
        a, b = CURVE_Z[i], CURVE_Z[i + 1]
        if a <= z <= b:
            t = smoother((z - a) / (b - a))
            return CURVE_X[i] * (1.0 - t) + CURVE_X[i + 1] * t
    return 0.0


def deform(co):
    x, y, z = float(co.x), float(co.y), float(co.z)
    zn = (z - zmin) / height * 1.70

    # Central-body mask protects arms/hands. It is broad across torso/pelvis,
    # but fades to zero before the relaxed arm columns.
    torso = 1.0 - smoother((abs(x) - 0.17) / 0.13)

    # Broad lateral fullness. This intentionally increases BOTH absolute hip
    # width and waist width, with the waist/hip ratio rising versus baseline.
    sx = smooth_curve(zn)
    pelvic = smoother((zn - 0.69) / 0.12)
    dx = x * sx * torso * pelvic

    # Modest thigh fullness, centered on each leg rather than translating legs.
    thigh = window(zn, 0.48, 0.58, 0.70, 0.84) * (1.0 - smoother((abs(x) - 0.19) / 0.10))
    leg_center = 0.098 * math.tanh(x / 0.035)
    dx += 0.08 * (x - leg_center) * thigh

    # Blender scene orientation: front/anterior is negative Y; rear is +Y.
    # Expand thigh/abdomen depth broadly around their sagittal centres.
    dy = 0.06 * (y + 0.012 * height_factor) * thigh
    abdomen = window(zn, 0.82, 0.94, 1.08, 1.19) * torso
    dy += 0.075 * (y + 0.025 * height_factor) * abdomen

    # Broad paired breast fields: larger projection, wider root/lower pole,
    # and a small lowering consistent with the supplied natural geometry refs.
    breast_z = math.exp(-0.5 * ((zn - 1.215) / 0.064) ** 2) * window(zn, 1.07, 1.12, 1.32, 1.39)
    breast_x = math.exp(-0.5 * ((x - 0.089 * height_factor) / (0.060 * height_factor)) ** 2)
    breast_x += math.exp(-0.5 * ((x + 0.089 * height_factor) / (0.060 * height_factor)) ** 2)
    anterior = smoother(((-y) - 0.025 * height_factor) / (0.090 * height_factor))
    breast = breast_z * breast_x * anterior
    dy -= 0.062 * height_factor * breast
    dx += 0.007 * height_factor * math.tanh(x / (0.040 * height_factor)) * breast
    dz = -0.013 * height_factor * breast

    # Glute projection is distributed across each cheek with a lower-thigh
    # transition; the cleft is deliberately not filled flat.
    rear = 1.0 - smoother(((-y) + 0.085 * height_factor) / (0.090 * height_factor))
    glute_z = math.exp(-0.5 * ((zn - 0.835) / 0.090) ** 2) * window(zn, 0.61, 0.70, 0.96, 1.08)
    sigma_x = 0.083 * height_factor
    xcentre = 0.092 * height_factor
    norm = 1.0 + math.exp(-0.5 * ((2.0 * xcentre) / sigma_x) ** 2)
    glute_x = (
        math.exp(-0.5 * ((x - xcentre) / sigma_x) ** 2)
        + math.exp(-0.5 * ((x + xcentre) / sigma_x) ** 2)
    ) / norm
    cleft = 0.30 + 0.70 * smoother(abs(x) / (0.045 * height_factor))
    glute = rear * glute_z * glute_x * cleft
    dy += 0.052 * height_factor * glute

    return Vector((x + dx, y + dy, z + dz))


max_disp = 0.0
sum_sq = 0.0
moved = 0
for src_v, dst_v in zip(body.data.vertices, candidate.data.vertices):
    new_co = deform(src_v.co)
    d = (new_co - src_v.co).length
    if d > 1e-8:
        moved += 1
    max_disp = max(max_disp, d)
    sum_sq += d * d
    dst_v.co = new_co
candidate.data.update()
rms_disp = math.sqrt(sum_sq / len(candidate.data.vertices))


def band_width(obj, zn_target, half_band=0.008, x_limit=0.32):
    vals = []
    for v in obj.data.vertices:
        zn = (v.co.z - zmin) / height * 1.70
        if abs(zn - zn_target) <= half_band and abs(v.co.x) < x_limit:
            vals.append(v.co.x)
    return (max(vals) - min(vals)) if vals else None


def envelope(obj, zlo, zhi, xlim, mode):
    vals = []
    for v in obj.data.vertices:
        zn = (v.co.z - zmin) / height * 1.70
        if zlo <= zn <= zhi and abs(v.co.x) <= xlim:
            vals.append(v.co.y)
    if not vals:
        return None
    return min(vals) if mode == "front" else max(vals)


before = {
    "waist_width_m": band_width(body, 1.035, x_limit=0.24),
    "hip_width_m": band_width(body, 0.815, x_limit=0.28),
    "upper_thigh_width_m": band_width(body, 0.690, x_limit=0.30),
    "breast_front_envelope_y_m": envelope(body, 1.10, 1.35, 0.20, "front"),
    "glute_rear_envelope_y_m": envelope(body, 0.66, 1.00, 0.24, "rear"),
}
after = {
    "waist_width_m": band_width(candidate, 1.035, x_limit=0.30),
    "hip_width_m": band_width(candidate, 0.815, x_limit=0.34),
    "upper_thigh_width_m": band_width(candidate, 0.690, x_limit=0.34),
    "breast_front_envelope_y_m": envelope(candidate, 1.10, 1.35, 0.22, "front"),
    "glute_rear_envelope_y_m": envelope(candidate, 0.66, 1.00, 0.27, "rear"),
}
if before["waist_width_m"] and before["hip_width_m"]:
    before["waist_hip_width_ratio"] = before["waist_width_m"] / before["hip_width_m"]
if after["waist_width_m"] and after["hip_width_m"]:
    after["waist_hip_width_ratio"] = after["waist_width_m"] / after["hip_width_m"]

# Matched neutral five-view render: baseline and study share exact cameras/lights/material.
scene = bpy.context.scene
orig_camera = scene.camera
orig_engine = scene.render.engine
orig_res = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
orig_filepath = scene.render.filepath
orig_format = scene.render.image_settings.file_format
orig_transparent = scene.render.film_transparent
orig_world_color = tuple(scene.world.color) if scene.world else None
orig_hide = {o.name: bool(o.hide_render) for o in scene.objects}
render_meshes = [o for o in scene.objects if o.type == "MESH" and (o.name.startswith(BASE_NAME) or o.name == CANDIDATE_NAME)]
orig_materials = {o.name: list(o.data.materials) for o in render_meshes}
created_objects = []
neutral = None
rendered = []

try:
    neutral = bpy.data.materials.new("__VERA_STUDY_NEUTRAL__")
    neutral.use_nodes = True
    bsdf = neutral.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (0.52, 0.52, 0.52, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.72
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    for obj in render_meshes:
        obj.data.materials.clear()
        obj.data.materials.append(neutral)

    corners = [body.matrix_world @ Vector(c) for c in body.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    center = Vector(((min(xs)+max(xs))*0.5, (min(ys)+max(ys))*0.5, (min(zs)+max(zs))*0.5))

    cam_data = bpy.data.cameras.new("__VERA_STUDY_CAMERA_DATA__")
    cam = bpy.data.objects.new("__VERA_STUDY_CAMERA__", cam_data)
    scene.collection.objects.link(cam)
    created_objects.append(cam)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = height * 1.10
    cam_data.lens = 70
    scene.camera = cam

    def add_area(name, loc, energy, size):
        data = bpy.data.lights.new(name + "_DATA", type="AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = ((center - obj.location).to_track_quat("-Z", "Y")).to_euler()
        created_objects.append(obj)

    add_area("__VERA_STUDY_KEY__", center + Vector((-1.8, -2.4, 2.1)), 850.0, 2.3)
    add_area("__VERA_STUDY_FILL__", center + Vector((2.2, -0.5, 1.1)), 500.0, 2.6)
    add_area("__VERA_STUDY_RIM__", center + Vector((0.0, 2.4, 1.8)), 650.0, 2.0)

    if scene.world is not None:
        scene.world.color = (0.08, 0.08, 0.08)
    scene.render.resolution_x = 600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False

    distance = 3.0
    views = [
        ("FRONT", Vector((0.0, -distance, 0.0))),
        ("FRONT_3Q", Vector((-2.15, -2.15, 0.0))),
        ("SIDE", Vector((-distance, 0.0, 0.0))),
        ("REAR_3Q", Vector((-2.15, 2.15, 0.0))),
        ("REAR", Vector((0.0, distance, 0.0))),
    ]

    # Keep original eyes with both body renders, but toggle the two body surfaces.
    for label, show_candidate in (("BASELINE", False), ("STUDY", True)):
        body.hide_render = show_candidate
        candidate.hide_render = not show_candidate
        for name, offset in views:
            cam.location = center + offset
            cam.rotation_euler = ((center - cam.location).to_track_quat("-Z", "Y")).to_euler()
            path = os.path.join(OUTPUT_DIR, f"{label}_{name}.png")
            scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            rendered.append(path)
finally:
    for obj in render_meshes:
        obj.data.materials.clear()
        for mat in orig_materials.get(obj.name, []):
            obj.data.materials.append(mat)
    for name, state in orig_hide.items():
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.hide_render = state
    scene.camera = orig_camera
    scene.render.engine = orig_engine
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = orig_res
    scene.render.filepath = orig_filepath
    scene.render.image_settings.file_format = orig_format
    scene.render.film_transparent = orig_transparent
    if scene.world is not None and orig_world_color is not None:
        scene.world.color = orig_world_color
    for obj in created_objects:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if isinstance(data, bpy.types.Camera):
            bpy.data.cameras.remove(data)
        elif isinstance(data, bpy.types.Light):
            bpy.data.lights.remove(data)
    if neutral is not None:
        bpy.data.materials.remove(neutral)

# Save a copy with both untouched baseline and reversible candidate.
blend_path = os.path.join(OUTPUT_DIR, "VERA_PROPORTION_STUDY_V1.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=True)

metrics = {
    "schema": "VERA_PROPORTION_STUDY_BLENDER_V1",
    "status": "EXECUTED_STUDY / NOT_REGISTERED_FIT / NOT_VERA_ACCEPTED / NO_STAGE_A_PASS",
    "source_object": BASE_NAME,
    "candidate_object": CANDIDATE_NAME,
    "vertices": len(candidate.data.vertices),
    "polygons": len(candidate.data.polygons),
    "height_m": height,
    "moved_vertices": moved,
    "max_displacement_m": max_disp,
    "rms_displacement_m": rms_disp,
    "before": before,
    "after": after,
    "parameter_authority": "Patrick 2026-09-08 direct correction + exact Prime/Hailey reference inspection; deformation magnitudes remain explicit study hypotheses",
    "target_direction": {
        "breasts": "materially larger, broad natural lower-pole fullness",
        "glutes": "materially larger, more projection and roundness",
        "hips": "wider without lateral spikes",
        "thighs": "modestly fuller",
        "waist": "wider and less hourglass; waist/hip width ratio must increase"
    },
    "rendered": [os.path.basename(p) for p in rendered],
    "saved_blend_copy": os.path.basename(blend_path),
    "nonclaims": [
        "No registered photographic fit",
        "No identity/face acceptance",
        "No final anatomy or Stage-A promotion",
        "No UV or texture-production qualification"
    ]
}
metrics_path = os.path.join(OUTPUT_DIR, "VERA_PROPORTION_STUDY_V1_METRICS.json")
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2, sort_keys=True)
    f.write("\n")

print(json.dumps(metrics, sort_keys=True))
