# Approved fixed Blender script: visual refinement of V1 broad proportion study.
# Uses untouched CC0 + deterministic V1 candidate already present in scene.
# V2 remains a reversible study, never a registered fit or Stage-A promotion.

import bpy, json, math, os
from mathutils import Vector

OUTPUT_DIR = globals().get("OUTPUT_DIR")
if not OUTPUT_DIR:
    raise RuntimeError("Relay did not provide OUTPUT_DIR")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE = "GEO-body_female_realistic"
V1 = "VERA_PROPORTION_STUDY_V1"
V2 = "VERA_PROPORTION_STUDY_V2"
COUNT_V = 42342
COUNT_P = 84680

base = bpy.data.objects.get(BASE)
v1 = bpy.data.objects.get(V1)
if base is None or v1 is None or base.type != 'MESH' or v1.type != 'MESH':
    raise RuntimeError("Expected untouched baseline and V1 study candidate are not both present")
for obj in (base, v1):
    if len(obj.data.vertices) != COUNT_V or len(obj.data.polygons) != COUNT_P:
        raise RuntimeError("Topology/count guard failed")

old = bpy.data.objects.get(V2)
if old is not None:
    mesh = old.data if old.type == 'MESH' else None
    bpy.data.objects.remove(old, do_unlink=True)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)

v2 = v1.copy()
v2.data = v1.data.copy()
v2.name = V2
v2.data.name = V2 + "_MESH"
bpy.context.scene.collection.objects.link(v2)

base_coords = [v.co.copy() for v in base.data.vertices]
zmin = min(p.z for p in base_coords)
zmax = max(p.z for p in base_coords)
height = zmax-zmin
hf = height/1.70


def clamp01(t): return max(0.0, min(1.0, float(t)))
def smooth(t):
    t=clamp01(t)
    return t*t*t*(t*(t*6.0-15.0)+10.0)
def window(z,a,b,c,d): return smooth((z-a)/(b-a))*(1.0-smooth((z-c)/(d-c)))
def gauss(q,c,s): return math.exp(-0.5*((q-c)/s)**2)

max_delta = 0.0
sum_sq = 0.0
moved = 0
for b, a, dst in zip(base.data.vertices, v1.data.vertices, v2.data.vertices):
    x,y,z = map(float, b.co)
    zn = (z-zmin)/height*1.70
    p = a.co.copy()
    delta = Vector((0.0,0.0,0.0))

    # V1 hit the requested direction but made the torso too blocky. Preserve a
    # clearly wider-than-baseline waist while backing off 15% of V1's lateral
    # waist-only delta. Hip width is not reduced here.
    waist = window(zn,0.86,0.94,1.10,1.19) * (1.0-smooth((abs(x)-0.17)/0.13))
    delta.x -= 0.15*(a.co.x-b.co.x)*waist

    # Breast refinement from the supplied natural-geometry references:
    # broaden root/lower pole, lower the mass slightly, move projection downward
    # instead of simply inflating a high spherical tip.
    bx = gauss(x, 0.086*hf, 0.078*hf) + gauss(x, -0.086*hf, 0.078*hf)
    front = smooth(((-y)-0.005*hf)/(0.105*hf))
    rootz = gauss(zn,1.185,0.090)*window(zn,1.02,1.08,1.31,1.40)
    lowerz = gauss(zn,1.135,0.060)*window(zn,1.02,1.07,1.23,1.31)
    upperz = gauss(zn,1.255,0.055)*window(zn,1.15,1.19,1.33,1.39)
    breast = bx*front*rootz
    lower = bx*front*lowerz
    upper = bx*front*upperz
    delta.x += (0.010*hf)*math.tanh(x/(0.035*hf))*breast
    delta.y += (0.008*hf)*upper        # reduce high-pole tip projection
    delta.y -= (0.014*hf)*lower        # add lower-pole projection
    delta.z -= (0.012*hf)*breast*(0.60+0.40*smooth((1.24-zn)/0.14))

    # Glute refinement: reduce the high shelf slightly and redistribute volume
    # into broader/lower cheek support plus a smoother upper-thigh transition.
    rear = smooth((y-0.005*hf)/(0.105*hf))
    gx = (gauss(x,0.100*hf,0.100*hf)+gauss(x,-0.100*hf,0.100*hf))
    lowerg = gx*rear*gauss(zn,0.765,0.105)*window(zn,0.55,0.63,0.91,1.02)
    upperg = gx*rear*gauss(zn,0.885,0.075)*window(zn,0.72,0.78,1.00,1.08)
    cleft = 0.35+0.65*smooth(abs(x)/(0.050*hf))
    lowerg *= cleft
    upperg *= cleft
    delta.y -= (0.007*hf)*upperg
    delta.y += (0.015*hf)*lowerg
    delta.x += (0.006*hf)*math.tanh(x/(0.045*hf))*lowerg
    delta.z -= (0.004*hf)*lowerg

    # Slight additional upper-thigh fullness to connect the larger glute/hip
    # mass without translating the whole leg sideways.
    thigh = window(zn,0.50,0.57,0.72,0.84)*(1.0-smooth((abs(x)-0.20)/0.10))
    leg_center = 0.098*hf*math.tanh(x/(0.035*hf))
    delta.x += 0.018*(x-leg_center)*thigh
    delta.y += 0.010*(y+0.012*hf)*thigh

    dst.co = p + delta
    mag = delta.length
    if mag > 1e-8: moved += 1
    max_delta=max(max_delta,mag)
    sum_sq += mag*mag
v2.data.update()
rms_delta=math.sqrt(sum_sq/COUNT_V)

# Matched neutral renders for untouched baseline, V1, and V2.
scene=bpy.context.scene
orig_camera=scene.camera
orig_res=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)
orig_filepath=scene.render.filepath
orig_format=scene.render.image_settings.file_format
orig_transparent=scene.render.film_transparent
orig_world=tuple(scene.world.color) if scene.world else None
orig_hide={o.name:bool(o.hide_render) for o in scene.objects}
render_objs=[base,v1,v2]
orig_mats={o.name:list(o.data.materials) for o in render_objs}
created=[]
neutral=None
rendered=[]
try:
    neutral=bpy.data.materials.new('__VERA_V2_NEUTRAL__'); neutral.use_nodes=True
    bsdf=neutral.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(0.52,0.52,0.52,1.0)
        bsdf.inputs['Roughness'].default_value=0.72
        if 'Metallic' in bsdf.inputs: bsdf.inputs['Metallic'].default_value=0.0
    for o in render_objs:
        o.data.materials.clear(); o.data.materials.append(neutral)

    corners=[base.matrix_world@Vector(c) for c in base.bound_box]
    xs=[p.x for p in corners]; ys=[p.y for p in corners]; zs=[p.z for p in corners]
    center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2))
    cd=bpy.data.cameras.new('__VERA_V2_CAMERA_DATA__')
    cam=bpy.data.objects.new('__VERA_V2_CAMERA__',cd); scene.collection.objects.link(cam); created.append(cam)
    cd.type='ORTHO'; cd.ortho_scale=height*1.10; scene.camera=cam
    def light(name,loc,energy,size):
        d=bpy.data.lights.new(name+'_DATA',type='AREA'); d.energy=energy; d.shape='DISK'; d.size=size
        o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc
        o.rotation_euler=((center-o.location).to_track_quat('-Z','Y')).to_euler(); created.append(o)
    light('__VERA_V2_KEY__',center+Vector((-1.8,-2.4,2.1)),850,2.3)
    light('__VERA_V2_FILL__',center+Vector((2.2,-0.5,1.1)),500,2.6)
    light('__VERA_V2_RIM__',center+Vector((0,2.4,1.8)),650,2.0)
    if scene.world: scene.world.color=(0.08,0.08,0.08)
    scene.render.resolution_x=600; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    distance=3.0
    views=[('FRONT',Vector((0,-distance,0))),('FRONT_3Q',Vector((-2.15,-2.15,0))),('SIDE',Vector((-distance,0,0))),('REAR_3Q',Vector((-2.15,2.15,0))),('REAR',Vector((0,distance,0)))]
    for label,shown in [('BASELINE',base),('V1',v1),('V2',v2)]:
        for o in render_objs: o.hide_render=(o is not shown)
        for name,offset in views:
            cam.location=center+offset; cam.rotation_euler=((center-cam.location).to_track_quat('-Z','Y')).to_euler()
            path=os.path.join(OUTPUT_DIR,f'{label}_{name}.png'); scene.render.filepath=path
            bpy.ops.render.render(write_still=True); rendered.append(path)
finally:
    for o in render_objs:
        o.data.materials.clear()
        for m in orig_mats[o.name]: o.data.materials.append(m)
    for name,state in orig_hide.items():
        o=bpy.data.objects.get(name)
        if o: o.hide_render=state
    scene.camera=orig_camera
    scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=orig_res
    scene.render.filepath=orig_filepath; scene.render.image_settings.file_format=orig_format; scene.render.film_transparent=orig_transparent
    if scene.world and orig_world is not None: scene.world.color=orig_world
    for o in created:
        d=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if isinstance(d,bpy.types.Camera): bpy.data.cameras.remove(d)
        elif isinstance(d,bpy.types.Light): bpy.data.lights.remove(d)
    if neutral: bpy.data.materials.remove(neutral)

blend=os.path.join(OUTPUT_DIR,'VERA_PROPORTION_STUDY_V2.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend,copy=True)
metrics={
    'schema':'VERA_PROPORTION_STUDY_BLENDER_V2',
    'status':'EXECUTED_REFINEMENT / VISUAL_REVIEW_REQUIRED / NOT_REGISTERED_FIT / NO_STAGE_A_PASS',
    'baseline':BASE,'v1':V1,'v2':V2,'vertices':COUNT_V,'polygons':COUNT_P,
    'v2_delta_moved_vertices':moved,'v2_delta_max_m':max_delta,'v2_delta_rms_m':rms_delta,
    'refinement_intent':['preserve wider/less-hourglass macro target','reduce V1 blocky waist slightly while remaining wider than baseline','broaden/lower natural breast mass rather than high spherical inflation','redistribute glute projection into lower/broader cheek support','slightly fuller upper-thigh transition'],
    'rendered':[os.path.basename(p) for p in rendered],
    'saved_blend_copy':os.path.basename(blend),
    'nonclaims':['No photographic registration','No final anatomy','No Stage-A promotion','No UV/texture production qualification']
}
with open(os.path.join(OUTPUT_DIR,'VERA_PROPORTION_STUDY_V2_METRICS.json'),'w',encoding='utf-8') as f:
    json.dump(metrics,f,indent=2,sort_keys=True); f.write('\n')
print(json.dumps(metrics,sort_keys=True))
