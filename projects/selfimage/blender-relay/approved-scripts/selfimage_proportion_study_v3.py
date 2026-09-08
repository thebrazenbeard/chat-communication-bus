# Fixed V3 refinement: preserve V2 macro proportions; improve breast lower-pole/root
# breadth and sacrum->glute->upper-thigh continuity from exact supplied references.
# Reversible study only; no registered fit, Stage-A, or UV qualification.

import bpy, json, math, os
from mathutils import Vector
OUTPUT_DIR=globals().get('OUTPUT_DIR')
if not OUTPUT_DIR: raise RuntimeError('Relay did not provide OUTPUT_DIR')
os.makedirs(OUTPUT_DIR,exist_ok=True)
BASE='GEO-body_female_realistic'; V2='VERA_PROPORTION_STUDY_V2'; V3='VERA_PROPORTION_STUDY_V3'
NV=42342; NP=84680
base=bpy.data.objects.get(BASE); v2=bpy.data.objects.get(V2)
if not base or not v2 or base.type!='MESH' or v2.type!='MESH': raise RuntimeError('Baseline or V2 missing')
for o in (base,v2):
    if len(o.data.vertices)!=NV or len(o.data.polygons)!=NP: raise RuntimeError('Topology guard failed')
old=bpy.data.objects.get(V3)
if old:
    m=old.data if old.type=='MESH' else None; bpy.data.objects.remove(old,do_unlink=True)
    if m and m.users==0: bpy.data.meshes.remove(m)
v3=v2.copy(); v3.data=v2.data.copy(); v3.name=V3; v3.data.name=V3+'_MESH'; bpy.context.scene.collection.objects.link(v3)
coords=[v.co.copy() for v in base.data.vertices]; zmin=min(p.z for p in coords); zmax=max(p.z for p in coords); height=zmax-zmin; hf=height/1.70

def cl(t): return max(0.,min(1.,float(t)))
def sm(t):
    t=cl(t); return t*t*t*(t*(t*6.-15.)+10.)
def win(z,a,b,c,d): return sm((z-a)/(b-a))*(1.-sm((z-c)/(d-c)))
def g(q,c,s): return math.exp(-.5*((q-c)/s)**2)
maxd=0.; ss=0.; moved=0
for b,src,dst in zip(base.data.vertices,v2.data.vertices,v3.data.vertices):
    x,y,z=map(float,b.co); zn=(z-zmin)/height*1.70; d=Vector((0.,0.,0.))
    # Breast: distal-mass-only gating keeps the root comparatively stable;
    # wider paired fields preserve medial separation and favor lower-pole mass.
    pair=g(x,.087*hf,.090*hf)+g(x,-.087*hf,.090*hf)
    medial=sm((abs(x)-.018*hf)/(.032*hf))
    front=sm(((-y)-.015*hf)/(.100*hf))
    rootz=g(zn,1.175,.105)*win(zn,1.00,1.07,1.32,1.41)
    lower=g(zn,1.105,.070)*win(zn,.99,1.05,1.22,1.31)
    mass=pair*medial*front*rootz; low=pair*medial*front*lower
    d.x += .008*hf*math.tanh(x/(.035*hf))*mass
    d.y -= .006*hf*mass + .007*hf*low
    d.z -= .008*hf*mass*(.55+.45*sm((1.23-zn)/.15))

    # Glute: fill the abrupt V2 sacral-to-cheek slope with a shallow broad
    # transition, then enlarge lower/lateral cheek support without a local lobe.
    rear=sm((y-.005*hf)/(.105*hf))
    sacrum=rear*g(zn,.965,.115)*g(x,0.,.175*hf)
    cheekpair=(g(x,.102*hf,.112*hf)+g(x,-.102*hf,.112*hf))
    cheek=rear*cheekpair*g(zn,.775,.125)*win(zn,.53,.61,.93,1.05)
    cleft=.38+.62*sm(abs(x)/(.052*hf)); cheek*=cleft
    transition=rear*cheekpair*g(zn,.655,.080)*win(zn,.50,.56,.75,.82)*cleft
    d.y += .009*hf*sacrum + .009*hf*cheek + .004*hf*transition
    d.x += .007*hf*math.tanh(x/(.048*hf))*cheek
    d.z -= .003*hf*cheek
    dst.co=src.co+d
    m=d.length
    if m>1e-8: moved+=1
    maxd=max(maxd,m); ss+=m*m
v3.data.update(); rms=math.sqrt(ss/NV)

scene=bpy.context.scene; oc=scene.camera; ores=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage); of=scene.render.filepath; off=scene.render.image_settings.file_format; ot=scene.render.film_transparent; ow=tuple(scene.world.color) if scene.world else None; oh={o.name:bool(o.hide_render) for o in scene.objects}
objs=[base,v2,v3]; om={o.name:list(o.data.materials) for o in objs}; created=[]; neutral=None; rendered=[]
try:
    neutral=bpy.data.materials.new('__VERA_V3_NEUTRAL__'); neutral.use_nodes=True; bs=neutral.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Base Color'].default_value=(.52,.52,.52,1.); bs.inputs['Roughness'].default_value=.72
        if 'Metallic' in bs.inputs: bs.inputs['Metallic'].default_value=0.
    for o in objs: o.data.materials.clear(); o.data.materials.append(neutral)
    cs=[base.matrix_world@Vector(c) for c in base.bound_box]; xs=[p.x for p in cs]; ys=[p.y for p in cs]; zs=[p.z for p in cs]; center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2))
    cd=bpy.data.cameras.new('__VERA_V3_CAM_DATA__'); cam=bpy.data.objects.new('__VERA_V3_CAM__',cd); scene.collection.objects.link(cam); created.append(cam); cd.type='ORTHO'; cd.ortho_scale=height*1.10; scene.camera=cam
    def light(n,loc,e,s):
        ld=bpy.data.lights.new(n+'_DATA',type='AREA'); ld.energy=e; ld.shape='DISK'; ld.size=s; o=bpy.data.objects.new(n,ld); scene.collection.objects.link(o); o.location=loc; o.rotation_euler=((center-o.location).to_track_quat('-Z','Y')).to_euler(); created.append(o)
    light('__V3_KEY__',center+Vector((-1.8,-2.4,2.1)),850,2.3); light('__V3_FILL__',center+Vector((2.2,-.5,1.1)),500,2.6); light('__V3_RIM__',center+Vector((0,2.4,1.8)),650,2.)
    if scene.world: scene.world.color=(.08,.08,.08)
    scene.render.resolution_x=600; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    views=[('FRONT',Vector((0,-3.,0))),('FRONT_3Q',Vector((-2.15,-2.15,0))),('SIDE',Vector((-3.,0,0))),('REAR_3Q',Vector((-2.15,2.15,0))),('REAR',Vector((0,3.,0)))]
    for label,shown in [('BASELINE',base),('V2',v2),('V3',v3)]:
        for o in objs:o.hide_render=(o is not shown)
        for name,off in views:
            cam.location=center+off; cam.rotation_euler=((center-cam.location).to_track_quat('-Z','Y')).to_euler(); p=os.path.join(OUTPUT_DIR,f'{label}_{name}.png'); scene.render.filepath=p; bpy.ops.render.render(write_still=True); rendered.append(p)
finally:
    for o in objs:
        o.data.materials.clear()
        for m in om[o.name]: o.data.materials.append(m)
    for n,state in oh.items():
        o=bpy.data.objects.get(n)
        if o:o.hide_render=state
    scene.camera=oc; scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=ores; scene.render.filepath=of; scene.render.image_settings.file_format=off; scene.render.film_transparent=ot
    if scene.world and ow is not None: scene.world.color=ow
    for o in created:
        dat=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if isinstance(dat,bpy.types.Camera): bpy.data.cameras.remove(dat)
        elif isinstance(dat,bpy.types.Light): bpy.data.lights.remove(dat)
    if neutral:bpy.data.materials.remove(neutral)
blend=os.path.join(OUTPUT_DIR,'VERA_PROPORTION_STUDY_V3.blend'); bpy.ops.wm.save_as_mainfile(filepath=blend,copy=True)
metrics={'schema':'VERA_PROPORTION_STUDY_BLENDER_V3','status':'EXECUTED_REFINEMENT / VISUAL_REVIEW_REQUIRED / NOT_REGISTERED_FIT / NO_STAGE_A_PASS','baseline':BASE,'parent':V2,'candidate':V3,'vertices':NV,'polygons':NP,'delta_moved_vertices':moved,'delta_max_m':maxd,'delta_rms_m':rms,'intent':['preserve V2 wider hips/modestly fuller thighs/less-hourglass waist','wider lower gravity-loaded breast mass with medial separation','soften high breast sphere','continuous sacrum-to-cheek-to-upper-thigh glute transition','broader lower glute support without shelf/lobe'],'rendered':[os.path.basename(p) for p in rendered],'saved_blend_copy':os.path.basename(blend),'nonclaims':['No photo registration','No final anatomy','No Stage-A promotion','No UV/texture production qualification']}
with open(os.path.join(OUTPUT_DIR,'VERA_PROPORTION_STUDY_V3_METRICS.json'),'w',encoding='utf-8') as f: json.dump(metrics,f,indent=2,sort_keys=True); f.write('\n')
print(json.dumps(metrics,sort_keys=True))
