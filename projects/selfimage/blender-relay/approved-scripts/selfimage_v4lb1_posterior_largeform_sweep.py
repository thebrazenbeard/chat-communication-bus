# V4LB1: broad posterior pelvis/glute/hip/thigh sweep from exact V3R3-S100 workshop parent.
# Diagnostic Blender study only. No Stage-A/stable/canon promotion.
import bpy, hashlib, json, os
from mathutils import Vector
import numpy as np

OUTPUT_DIR=globals().get('OUTPUT_DIR')
if not OUTPUT_DIR:
    raise RuntimeError('Relay did not provide OUTPUT_DIR')
os.makedirs(OUTPUT_DIR,exist_ok=True)

BASE='GEO-body_female_realistic'
V2='VERA_PROPORTION_STUDY_V2'
NV=42342
NP=84680
EXPECTED_V2_COORD_HASH='da66d975e49864c496ebbb0ec957a332ffed7d6ef544bf5db9f2adfb554fb10f'
EXPECTED_S100_OBJ_SHA256='aee38b8613c4226f1bc83d928fde7fef55ed5faab877db0710485b9ddb61e7cf'

PARAMS=(
    ('VERA_V4LB1_S060',0.015,0.010,0.008),
    ('VERA_V4LB1_S085',0.025,0.016,0.014),
    ('VERA_V4LB1_S110',0.035,0.022,0.020),
)

base=bpy.data.objects.get(BASE)
v2=bpy.data.objects.get(V2)
if not base or not v2 or base.type!='MESH' or v2.type!='MESH':
    raise RuntimeError('Expected untouched baseline and V2 missing')
for o in (base,v2):
    if len(o.data.vertices)!=NV or len(o.data.polygons)!=NP:
        raise RuntimeError('Topology/count guard failed')

local_base=np.asarray([[float(v.co.x),float(v.co.y),float(v.co.z)] for v in base.data.vertices],dtype=np.float64)
local_v2=np.asarray([[float(v.co.x),float(v.co.y),float(v.co.z)] for v in v2.data.vertices],dtype=np.float64)
coord_hash=hashlib.sha256(np.round(local_v2,9).astype('<f8',copy=False).tobytes(order='C')).hexdigest()
if coord_hash!=EXPECTED_V2_COORD_HASH:
    raise RuntimeError(f'V2 coordinate hash mismatch: {coord_hash}')

base_p=np.column_stack((-local_base[:,0],-local_base[:,1],local_base[:,2]))
v2_p=np.column_stack((-local_v2[:,0],-local_v2[:,1],local_v2[:,2]))
x2,y2,z2=v2_p.T
zmin=float(z2.min()); zmax=float(z2.max()); h=zmax-zmin
cx=float((x2.min()+x2.max())*.5)
t=(z2-zmin)/h

def smooth01(a):
    a=np.clip(a,0.,1.)
    return a*a*a*(10.+a*(-15.+6.*a))

def window(tt,a,b,c,d):
    return smooth01((tt-a)/(b-a))*(1.-smooth01((tt-c)/(d-c)))

raw=np.maximum(0.,-(v2_p[:,2]-base_p[:,2]))
raw_max=float(raw.max())
if raw_max<0.001:
    raise RuntimeError(f'Breast signal unexpectedly weak: {raw_max}')
norm=raw/raw_max
strong=norm>=0.20
breast_band=(t>=.62)&(t<=.82)&(np.abs(x2-cx)<=.22*h)
purity=float(np.count_nonzero(strong & breast_band)/max(1,np.count_nonzero(strong)))
if np.count_nonzero(strong)<100 or purity<0.90:
    raise RuntimeError(f'Breast signal guard failed: strong={np.count_nonzero(strong)}, purity={purity}')
breast_protect=smooth01((norm-.002)/(.025-.002))
waist_mask=(t>=.585)&(t<=.615)&(np.abs(x2-cx)<=.11*h)&(breast_protect<.05)
if np.count_nonzero(waist_mask)<50:
    raise RuntimeError('Too few V3R3 waist reference vertices')
waist_cy=float(np.median(y2[waist_mask]))
waist_front=float(np.quantile(y2[waist_mask],.95))
allowed_front=waist_front+.0015*h
wz=window(t,.615,.632,.662,.690)
xh=np.abs(x2-cx)/h
torso=1.-smooth01((xh-.105)/(.175-.105))
frontness=smooth01((y2-waist_cy)/(.085*h))
chest=(1.-breast_protect)*wz*torso
overhang=np.maximum(y2-allowed_front,0.)
retract=np.minimum(overhang,.018*h)
parent_dx=-(x2-cx)*.030*chest
parent_dy=-retract*frontness*chest
s100=v2_p+np.column_stack((parent_dx,parent_dy,np.zeros_like(parent_dx)))

def write_project(vertices,obj,path):
    with open(path,'w',encoding='utf-8',newline='\n') as f:
        f.write('# project X lateral / +Y anterior / +Z up\n')
        for q in vertices:
            f.write('v %.12f %.12f %.12f\n'%(q[0],q[1],q[2]))
        for poly in obj.data.polygons:
            ids=[int(i)+1 for i in poly.vertices]
            f.write('f '+' '.join(str(i) for i in ids)+'\n')

parent_path=os.path.join(OUTPUT_DIR,'V3R3_S100_PARENT_PROJECT.obj')
write_project(s100,v2,parent_path)
parent_obj_sha=hashlib.sha256(open(parent_path,'rb').read()).hexdigest()
if parent_obj_sha!=EXPECTED_S100_OBJ_SHA256:
    raise RuntimeError(f'V3R3-S100 parent OBJ hash mismatch: {parent_obj_sha}')

x,y,z=s100.T
t=(z-zmin)/h
xh=np.abs(x-cx)/h
body_support=1.-smooth01((xh-.135)/(.195-.135))
w_hip=window(t,.390,.430,.545,.590)*body_support
w_glute=window(t,.350,.400,.525,.575)*body_support
backness=smooth01(((-y/h)+.005)/.075)
w_thigh=window(t,.180,.240,.400,.455)*body_support

thigh_center_band=(t>=.270)&(t<=.370)&(xh<.140)
thigh_centers={}
for side in (-1,1):
    m=thigh_center_band & (((x-cx)*side)>0.)
    if np.count_nonzero(m)<50:
        raise RuntimeError(f'Too few vertices to derive thigh center for side {side}')
    thigh_centers[side]=(float(np.median(x[m])),float(np.median(y[m])))

hip_metric_mask=(t>=.430)&(t<=.540)&(xh<.160)
glute_metric_mask=(t>=.400)&(t<=.530)&(xh<.140)
thigh_metric_mask=(t>=.250)&(t<=.390)&(xh<.140)
thorax_preserve_mask=(t>=.615)&(t<=.690)
breast_core=breast_protect>=.95
lowerbody_support=(w_hip>1e-12)|(w_glute*backness>1e-12)|(w_thigh>1e-12)

for name,_,_,_ in PARAMS:
    old=bpy.data.objects.get(name)
    if old:
        mesh=old.data if old.type=='MESH' else None
        bpy.data.objects.remove(old,do_unlink=True)
        if mesh and mesh.users==0:
            bpy.data.meshes.remove(mesh)

candidates=[]
metrics=[]

def hip_width(vertices):
    return float(2.*np.quantile(np.abs(vertices[hip_metric_mask,0]-cx),.95))

def glute_projection(vertices):
    return float(-np.quantile(vertices[glute_metric_mask,1],.05))

def thigh_stats(vertices):
    widths=[]; depths=[]
    for side,(lx,ly) in thigh_centers.items():
        m=thigh_metric_mask & (((x-cx)*side)>0.)
        widths.append(float(2.*np.quantile(np.abs(vertices[m,0]-lx),.95)))
        depths.append(float(np.quantile(vertices[m,1],.95)-np.quantile(vertices[m,1],.05)))
    return float(np.mean(widths)),float(np.mean(depths))

parent_hip=hip_width(s100)
parent_glute=glute_projection(s100)
parent_thigh_w,parent_thigh_d=thigh_stats(s100)

for name,hip_fraction,glute_gain,thigh_fraction in PARAMS:
    dx_hip=(x-cx)*hip_fraction*w_hip
    dy_glute=-glute_gain*w_glute*backness
    dx_thigh=np.zeros_like(x)
    dy_thigh=np.zeros_like(y)
    for side,(lx,ly) in thigh_centers.items():
        m=((x-cx)*side)>0.
        dx_thigh[m]=(x[m]-lx)*thigh_fraction*w_thigh[m]
        dy_thigh[m]=(y[m]-ly)*thigh_fraction*w_thigh[m]
    disp=np.column_stack((dx_hip+dx_thigh,dy_glute+dy_thigh,np.zeros_like(x)))
    proj=s100+disp
    local=np.column_stack((-proj[:,0],-proj[:,1],proj[:,2]))
    obj=v2.copy(); obj.data=v2.data.copy(); obj.name=name; obj.data.name=name+'_MESH'
    bpy.context.scene.collection.objects.link(obj)
    for co,dst in zip(local,obj.data.vertices):
        dst.co=(float(co[0]),float(co[1]),float(co[2]))
    obj.data.update(); candidates.append(obj)
    out_path=os.path.join(OUTPUT_DIR,name+'.obj')
    write_project(proj,obj,out_path)
    dnorm=np.linalg.norm(disp,axis=1)
    hip=hip_width(proj); gp=glute_projection(proj); tw,td=thigh_stats(proj)
    metrics.append({
        'name':name,
        'hip_fraction':hip_fraction,
        'glute_gain_hypothesis_mm':glute_gain*1000.,
        'proximal_thigh_fraction':thigh_fraction,
        'project_obj':os.path.basename(out_path),
        'project_obj_sha256':hashlib.sha256(open(out_path,'rb').read()).hexdigest(),
        'changed_vertices':int(np.count_nonzero(dnorm>1e-12)),
        'max_displacement_mm':float(dnorm.max()*1000.),
        'max_displacement_outside_lowerbody_support_mm':float(dnorm[~lowerbody_support].max()*1000.) if np.any(~lowerbody_support) else 0.,
        'breast_core_max_displacement_mm':float(dnorm[breast_core].max()*1000.) if np.any(breast_core) else 0.,
        'thorax_band_max_displacement_mm':float(dnorm[thorax_preserve_mask].max()*1000.) if np.any(thorax_preserve_mask) else 0.,
        'hip_width_delta_mm':float((hip-parent_hip)*1000.),
        'glute_posterior_projection_delta_mm':float((gp-parent_glute)*1000.),
        'proximal_thigh_width_delta_mm':float((tw-parent_thigh_w)*1000.),
        'proximal_thigh_depth_delta_mm':float((td-parent_thigh_d)*1000.),
    })

scene=bpy.context.scene
orig_camera=scene.camera
orig_res=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)
orig_filepath=scene.render.filepath
orig_format=scene.render.image_settings.file_format
orig_transparent=scene.render.film_transparent
orig_world=tuple(scene.world.color) if scene.world else None
orig_hide={o.name:bool(o.hide_render) for o in scene.objects}

parent_local=np.column_stack((-s100[:,0],-s100[:,1],s100[:,2]))
parent_obj=v2.copy(); parent_obj.data=v2.data.copy(); parent_obj.name='VERA_V3R3_S100_RENDER_PARENT'; parent_obj.data.name=parent_obj.name+'_MESH'
bpy.context.scene.collection.objects.link(parent_obj)
for co,dst in zip(parent_local,parent_obj.data.vertices):
    dst.co=(float(co[0]),float(co[1]),float(co[2]))
parent_obj.data.update()
subjects=[parent_obj]+candidates
orig_mats={o.name:list(o.data.materials) for o in subjects}
created=[]; neutral=None; rendered=[]; hidden=[]
try:
    for o in scene.objects:
        if o.type!='MESH':
            continue
        if o in subjects:
            continue
        if o.name.startswith('GEO-body_female_realistic.eye.'):
            o.hide_render=False
            continue
        if o.name==BASE or o.name.startswith('VERA_'):
            o.hide_render=True; hidden.append(o.name)
    neutral=bpy.data.materials.new('__VERA_V4LB1_NEUTRAL__'); neutral.use_nodes=True
    bsdf=neutral.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(.52,.52,.52,1.)
        bsdf.inputs['Roughness'].default_value=.72
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value=0.
    for o in subjects:
        o.data.materials.clear(); o.data.materials.append(neutral)
    corners=[base.matrix_world@Vector(c) for c in base.bound_box]
    xs=[p.x for p in corners]; ys=[p.y for p in corners]; zs=[p.z for p in corners]
    center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2))
    cd=bpy.data.cameras.new('__VERA_V4LB1_CAM_DATA__')
    cam=bpy.data.objects.new('__VERA_V4LB1_CAM__',cd); scene.collection.objects.link(cam); created.append(cam)
    cd.type='ORTHO'; cd.ortho_scale=h*1.10; scene.camera=cam
    def add_light(name,loc,energy,size):
        ld=bpy.data.lights.new(name+'_DATA',type='AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
        o=bpy.data.objects.new(name,ld); scene.collection.objects.link(o); o.location=loc
        o.rotation_euler=((center-o.location).to_track_quat('-Z','Y')).to_euler(); created.append(o)
    add_light('__V4LB1_KEY__',center+Vector((-1.8,-2.4,2.1)),850,2.3)
    add_light('__V4LB1_FILL__',center+Vector((2.2,-.5,1.1)),500,2.6)
    add_light('__V4LB1_RIM__',center+Vector((0,2.4,1.8)),650,2.)
    if scene.world:
        scene.world.color=(.08,.08,.08)
    scene.render.resolution_x=600; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    views=[
        ('FRONT',Vector((0,-3.,0))),
        ('FRONT_3Q',Vector((-2.15,-2.15,0))),
        ('SIDE',Vector((-3.,0,0))),
        ('REAR_3Q',Vector((-2.15,2.15,0))),
        ('REAR',Vector((0,3.,0))),
    ]
    labels=['PARENT','S060','S085','S110']
    for label,shown in zip(labels,subjects):
        for o in subjects:
            o.hide_render=(o is not shown)
        for view,offset in views:
            cam.location=center+offset
            cam.rotation_euler=((center-cam.location).to_track_quat('-Z','Y')).to_euler()
            path=os.path.join(OUTPUT_DIR,f'{label}_{view}.png')
            scene.render.filepath=path; bpy.ops.render.render(write_still=True); rendered.append(path)
finally:
    for o in subjects:
        o.data.materials.clear()
        for m in orig_mats[o.name]:
            o.data.materials.append(m)
    for name,state in orig_hide.items():
        o=bpy.data.objects.get(name)
        if o:
            o.hide_render=state
    scene.camera=orig_camera
    scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=orig_res
    scene.render.filepath=orig_filepath; scene.render.image_settings.file_format=orig_format; scene.render.film_transparent=orig_transparent
    if scene.world and orig_world is not None:
        scene.world.color=orig_world
    for o in created:
        data=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if isinstance(data,bpy.types.Camera):
            bpy.data.cameras.remove(data)
        elif isinstance(data,bpy.types.Light):
            bpy.data.lights.remove(data)
    if neutral:
        bpy.data.materials.remove(neutral)

receipt={
    'schema':'SELFIMAGE_V4LB1_POSTERIOR_LARGE_FORM_SWEEP_V1',
    'status':'EXECUTED_SWEEP / HOSTILE_VISUAL_AND_STRUCTURAL_REVIEW_REQUIRED',
    'v2_coordinate_hash':coord_hash,
    'v3r3_s100_parent_project_obj_sha256':parent_obj_sha,
    'breast_signal':{
        'protected_core_count':int(np.count_nonzero(breast_core)),
        'strong_vertex_count':int(np.count_nonzero(strong)),
        'strong_signal_purity_in_breast_band':purity,
    },
    'field':{
        'hip_vertical_window_t':[.390,.430,.545,.590],
        'glute_vertical_window_t':[.350,.400,.525,.575],
        'thigh_vertical_window_t':[.180,.240,.400,.455],
        'body_support_abs_x_over_h_full_zero':[.135,.195],
        'posterior_backness_neg_y_over_h_offset_span':[.005,.075],
        'thigh_centers_project_m':{str(k):[v[0],v[1]] for k,v in thigh_centers.items()},
    },
    'parent_metrics':{
        'hip_width_m':parent_hip,
        'glute_posterior_projection_m':parent_glute,
        'proximal_thigh_width_m':parent_thigh_w,
        'proximal_thigh_depth_m':parent_thigh_d,
    },
    'candidates':metrics,
    'rendered':[os.path.basename(p) for p in rendered],
    'hidden_competing_body_meshes':hidden,
    'reference_scope':'Prime whole-person + current Patrick directional correction; Aug18 posterior only for buttock/projection/cheek-thigh continuity; no identity/breast/face transfer',
    'promotion_ceiling':'DIRECTIONAL_WORKSHOP_SWEEP_ONLY / NO_STAGE_A / NO_STABLE_PARENT / NO_CANON',
}
with open(os.path.join(OUTPUT_DIR,'SWEEP_RECEIPT.json'),'w',encoding='utf-8') as f:
    json.dump(receipt,f,indent=2,sort_keys=True); f.write('\n')
print(json.dumps(receipt,sort_keys=True))

for obj in [parent_obj]+candidates:
    mesh=obj.data; bpy.data.objects.remove(obj,do_unlink=True)
    if mesh.users==0:
        bpy.data.meshes.remove(mesh)
