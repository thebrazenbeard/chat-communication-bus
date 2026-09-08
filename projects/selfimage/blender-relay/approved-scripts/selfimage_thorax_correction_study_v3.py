# Thorax-only V3 correction from V2.
# Purpose: reduce the lower-underbust ribcage shell while preserving V2 breast
# envelope and the accepted wider-waist / wider-hip / fuller-thigh / glute gains.
# Reversible diagnostic study only. No registered fit, Stage-A, or UV claim.

import bpy, json, math, os
from collections import Counter
from mathutils import Vector

OUTPUT_DIR = globals().get("OUTPUT_DIR")
if not OUTPUT_DIR:
    raise RuntimeError("Relay did not provide OUTPUT_DIR")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE = "GEO-body_female_realistic"
V2 = "VERA_PROPORTION_STUDY_V2"
V3 = "VERA_THORAX_CORRECTION_STUDY_V3"
COUNT_V = 42342
COUNT_P = 84680

base = bpy.data.objects.get(BASE)
v2 = bpy.data.objects.get(V2)
if base is None or v2 is None or base.type != 'MESH' or v2.type != 'MESH':
    raise RuntimeError("Expected untouched baseline and V2 parent are not both present")
for obj in (base, v2):
    if len(obj.data.vertices) != COUNT_V or len(obj.data.polygons) != COUNT_P:
        raise RuntimeError("Topology/count guard failed")

old = bpy.data.objects.get(V3)
if old is not None:
    mesh = old.data if old.type == 'MESH' else None
    bpy.data.objects.remove(old, do_unlink=True)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)

v3 = v2.copy()
v3.data = v2.data.copy()
v3.name = V3
v3.data.name = V3 + "_MESH"
bpy.context.scene.collection.objects.link(v3)

base_coords = [v.co.copy() for v in base.data.vertices]
zmin = min(p.z for p in base_coords)
zmax = max(p.z for p in base_coords)
height = zmax - zmin
hf = height / 1.70


def clamp01(t):
    return max(0.0, min(1.0, float(t)))

def smooth(t):
    t = clamp01(t)
    return t*t*t*(t*(t*6.0 - 15.0) + 10.0)

def window(z, a, b, c, d):
    return smooth((z-a)/(b-a)) * (1.0 - smooth((z-c)/(d-c)))

# Derive V2's anterior waist plane from central torso vertices, rather than
# inventing an anthropometric absolute target. Front is -Y in this scene.
waist_front_samples = []
for b, p in zip(base.data.vertices, v2.data.vertices):
    x, _, z = map(float, b.co)
    zn = (z-zmin)/height*1.70
    if 0.88 <= zn <= 0.99 and abs(x) <= 0.16*hf:
        waist_front_samples.append(float(p.co.y))
if not waist_front_samples:
    raise RuntimeError("Could not derive V2 waist anterior plane")
# A low percentile is robust to sparse local extrema while still representing
# the anterior waist shell. V3 chest wall is allowed only ~2 mm farther forward.
waist_front_samples.sort()
waist_front = waist_front_samples[max(0, int(round(0.05*(len(waist_front_samples)-1))))]
allowed_underbust_front = waist_front - 0.002*hf

max_delta = 0.0
sum_sq = 0.0
moved = 0
protected_breast_vertices = 0
for b, src, dst in zip(base.data.vertices, v2.data.vertices, v3.data.vertices):
    x, y0, z = map(float, b.co)
    p = src.co.copy()
    zn = (z-zmin)/height*1.70

    # Broad lower-thorax band. It peaks below the breast root and fades into
    # both the breast attachment and the already-approved wider waist.
    zband = window(zn, 0.96, 1.00, 1.105, 1.165)
    torso = 1.0 - smooth((abs(x)-0.155*hf)/(0.115*hf))
    anterior = smooth(((-float(p.y))-0.020*hf)/(0.085*hf))

    # Protect the actual V2 breast envelope/root mass from being reduced along
    # with the chest wall. Strong anterior prominence in the breast-height band
    # fades the shell operator to zero instead of shrinking the breast.
    breast_height = window(zn, 1.015, 1.055, 1.285, 1.355)
    breast_prominence = smooth(((-float(p.y))-0.105*hf)/(0.040*hf))
    breast_protect = breast_height * breast_prominence
    if breast_protect > 0.95:
        protected_breast_vertices += 1

    shell = zband * torso * anterior * (1.0 - breast_protect)
    delta = Vector((0.0, 0.0, 0.0))

    # AP correction: move only an overly-forward lower-thorax shell toward the
    # V2 waist plane. Cap the local change to keep the pass broad and reversible.
    need = max(0.0, allowed_underbust_front - float(p.y))
    delta.y += min(0.022*hf, need) * shell

    # Lateral circumference correction: modest broad reduction in the same
    # underbust band. This does not touch the waist/hip/thigh regions.
    delta.x -= 0.045 * float(p.x) * shell

    dst.co = p + delta
    mag = delta.length
    if mag > 1e-8:
        moved += 1
    max_delta = max(max_delta, mag)
    sum_sq += mag*mag
v3.data.update()
rms_delta = math.sqrt(sum_sq / COUNT_V)


def edge_usage(obj):
    counts = Counter()
    for poly in obj.data.polygons:
        ids = list(poly.vertices)
        for i in range(len(ids)):
            a, b = ids[i], ids[(i+1) % len(ids)]
            if a > b:
                a, b = b, a
            counts[(a,b)] += 1
    return counts

usage = edge_usage(v3)
nonmanifold_edges = sum(1 for n in usage.values() if n != 2)
nonpositive_faces = sum(1 for p in v3.data.polygons if p.area <= 0.0)

# Write exact local-coordinate triangle meshes for independent hostile gating.
def write_obj(obj, path):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Self Image diagnostic mesh; local coordinates; no UV/material authority\n')
        for v in obj.data.vertices:
            f.write('v %.12f %.12f %.12f\n' % (v.co.x, v.co.y, v.co.z))
        for poly in obj.data.polygons:
            ids = [int(i)+1 for i in poly.vertices]
            f.write('f ' + ' '.join(str(i) for i in ids) + '\n')

v2_obj = os.path.join(OUTPUT_DIR, 'V2_PARENT.obj')
v3_obj = os.path.join(OUTPUT_DIR, 'V3_THORAX_CANDIDATE.obj')
write_obj(v2, v2_obj)
write_obj(v3, v3_obj)

# Matched neutral renders, V2 versus V3. Full five views for hostile review.
scene = bpy.context.scene
orig_camera = scene.camera
orig_res = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
orig_filepath = scene.render.filepath
orig_format = scene.render.image_settings.file_format
orig_transparent = scene.render.film_transparent
orig_world = tuple(scene.world.color) if scene.world else None
orig_hide = {o.name: bool(o.hide_render) for o in scene.objects}
render_objs = [v2, v3]
orig_mats = {o.name: list(o.data.materials) for o in render_objs}
created = []
neutral = None
rendered = []
try:
    neutral = bpy.data.materials.new('__VERA_V3_THORAX_NEUTRAL__')
    neutral.use_nodes = True
    bsdf = neutral.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.52,0.52,0.52,1.0)
        bsdf.inputs['Roughness'].default_value = 0.72
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = 0.0
    for o in render_objs:
        o.data.materials.clear()
        o.data.materials.append(neutral)

    corners = [base.matrix_world @ Vector(c) for c in base.bound_box]
    xs=[p.x for p in corners]; ys=[p.y for p in corners]; zs=[p.z for p in corners]
    center = Vector(((min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2))
    cam_data = bpy.data.cameras.new('__VERA_V3_THORAX_CAMERA_DATA__')
    cam = bpy.data.objects.new('__VERA_V3_THORAX_CAMERA__', cam_data)
    scene.collection.objects.link(cam); created.append(cam)
    cam_data.type = 'ORTHO'; cam_data.ortho_scale = height*1.10; scene.camera = cam

    def add_light(name, loc, energy, size):
        ld = bpy.data.lights.new(name+'_DATA', type='AREA')
        ld.energy = energy; ld.shape = 'DISK'; ld.size = size
        o = bpy.data.objects.new(name, ld); scene.collection.objects.link(o)
        o.location = loc
        o.rotation_euler = ((center-o.location).to_track_quat('-Z','Y')).to_euler()
        created.append(o)

    add_light('__V3T_KEY__', center+Vector((-1.8,-2.4,2.1)), 850, 2.3)
    add_light('__V3T_FILL__', center+Vector((2.2,-0.5,1.1)), 500, 2.6)
    add_light('__V3T_RIM__', center+Vector((0,2.4,1.8)), 650, 2.0)
    if scene.world:
        scene.world.color = (0.08,0.08,0.08)
    scene.render.resolution_x = 600; scene.render.resolution_y = 900; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'; scene.render.film_transparent = False
    views = [
        ('FRONT', Vector((0,-3.0,0))),
        ('FRONT_3Q', Vector((-2.15,-2.15,0))),
        ('SIDE', Vector((-3.0,0,0))),
        ('REAR_3Q', Vector((-2.15,2.15,0))),
        ('REAR', Vector((0,3.0,0))),
    ]
    for label, shown in [('V2',v2),('V3',v3)]:
        for o in render_objs:
            o.hide_render = (o is not shown)
        for view_name, view_offset in views:
            cam.location = center + view_offset
            cam.rotation_euler = ((center-cam.location).to_track_quat('-Z','Y')).to_euler()
            path = os.path.join(OUTPUT_DIR, f'{label}_{view_name}.png')
            scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            rendered.append(path)
finally:
    for o in render_objs:
        o.data.materials.clear()
        for mat in orig_mats[o.name]:
            o.data.materials.append(mat)
    for name, state in orig_hide.items():
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = state
    scene.camera = orig_camera
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = orig_res
    scene.render.filepath = orig_filepath
    scene.render.image_settings.file_format = orig_format
    scene.render.film_transparent = orig_transparent
    if scene.world and orig_world is not None:
        scene.world.color = orig_world
    for o in created:
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(data, bpy.types.Camera):
            bpy.data.cameras.remove(data)
        elif isinstance(data, bpy.types.Light):
            bpy.data.lights.remove(data)
    if neutral:
        bpy.data.materials.remove(neutral)

blend_path = os.path.join(OUTPUT_DIR, 'VERA_THORAX_CORRECTION_STUDY_V3.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=True)

metrics = {
    'schema': 'VERA_THORAX_CORRECTION_STUDY_BLENDER_V3',
    'status': 'EXECUTED_THORAX_ONLY / HOSTILE_REVIEW_REQUIRED / NOT_REGISTERED_FIT / NO_STAGE_A_PASS',
    'baseline': BASE,
    'parent': V2,
    'candidate': V3,
    'vertices': COUNT_V,
    'polygons': COUNT_P,
    'topology_counts_preserved': len(v3.data.vertices)==len(v2.data.vertices) and len(v3.data.polygons)==len(v2.data.polygons),
    'candidate_nonmanifold_edges_by_face_use': nonmanifold_edges,
    'candidate_nonpositive_faces': nonpositive_faces,
    'delta_moved_vertices': moved,
    'delta_max_m': max_delta,
    'delta_rms_m': rms_delta,
    'protected_breast_vertices_strong_mask': protected_breast_vertices,
    'derived_v2_waist_front_y_m': waist_front,
    'allowed_underbust_front_y_m': allowed_underbust_front,
    'intent': [
        'preserve V2 breast size/envelope',
        'reduce lower-underbust thorax AP projection toward V2 waist plane',
        'reduce lower-underbust lateral circumference without narrowing V2 waist',
        'preserve V2 hips, thighs, and glute projection',
        'avoid inframammary dent/shelf/kink via broad smooth support',
    ],
    'rendered': [os.path.basename(p) for p in rendered],
    'mesh_exports': [os.path.basename(v2_obj), os.path.basename(v3_obj)],
    'saved_blend_copy': os.path.basename(blend_path),
    'nonclaims': ['No final anatomy','No Stage-A promotion','No UV/texture production qualification','Scalar checks do not override hostile visual review'],
}
with open(os.path.join(OUTPUT_DIR,'VERA_THORAX_CORRECTION_STUDY_V3_METRICS.json'),'w',encoding='utf-8') as f:
    json.dump(metrics,f,indent=2,sort_keys=True); f.write('\n')
print(json.dumps(metrics,sort_keys=True))
