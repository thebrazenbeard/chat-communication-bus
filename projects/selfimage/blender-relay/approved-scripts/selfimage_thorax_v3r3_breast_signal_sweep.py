# V3R3: breast-signal-protected lower-thorax sweep from exact V2.
# Diagnostic Blender study only. No Stage-A/stable/canon promotion.
import bpy, hashlib, json, math, os
from mathutils import Vector
import numpy as np

OUTPUT_DIR=globals().get('OUTPUT_DIR')
if not OUTPUT_DIR: raise RuntimeError('Relay did not provide OUTPUT_DIR')
os.makedirs(OUTPUT_DIR,exist_ok=True)
BASE='GEO-body_female_realistic'; V2='VERA_PROPORTION_STUDY_V2'
NV=42342; NP=84680
# Live self-hosted Blender scene readback on failed run 34292555197 / job 102282052868
# established this exact rounded local-coordinate hash before any deformation.
EXPECTED_V2_COORD_HASH='da66d975e49864c496ebbb0ec957a332ffed7d6ef544bf5db9f2adfb554fb10f'
STRENGTHS=(0.55,0.80,1.00)
NAMES=('VERA_THORAX_V3R3_S055','VERA_THORAX_V3R3_S080','VERA_THORAX_V3R3_S100')
Z_RISE_0,Z_RISE_1,Z_FALL_0,Z_FALL_1=.615,.632,.662,.690
LATERAL_CONTRACTION=.030
MAX_ANTERIOR_RETRACTION_H=.018
PLUMB_ALLOWANCE_H=.0015
TORSO_FULL_X_H,TORSO_ZERO_X_H=.105,.175
BREAST_PROTECT_START,BREAST_PROTECT_FULL=.002,.025

base=bpy.data.objects.get(BASE); v2=bpy.data.objects.get(V2)
if not base or not v2 or base.type!='MESH' or v2.type!='MESH': raise RuntimeError('Expected baseline and V2 missing')
for o in (base,v2):
    if len(o.data.vertices)!=NV or len(o.data.polygons)!=NP: raise RuntimeError('Topology/count guard failed')
local_base=np.asarray([[float(v.co.x),float(v.co.y),float(v.co.z)] for v in base.data.vertices],dtype=np.float64)
local_v2=np.asarray([[float(v.co.x),float(v.co.y),float(v.co.z)] for v in v2.data.vertices],dtype=np.float64)
coord_hash=hashlib.sha256(np.round(local_v2,9).astype('<f8',copy=False).tobytes(order='C')).hexdigest()
if coord_hash!=EXPECTED_V2_COORD_HASH: raise RuntimeError(f'V2 coordinate hash mismatch: {coord_hash}')
# Determinant-positive mapping; Blender local -Y is anterior, project +Y is anterior.
base_p=np.column_stack((-local_base[:,0],-local_base[:,1],local_base[:,2]))
v2_p=np.column_stack((-local_v2[:,0],-local_v2[:,1],local_v2[:,2]))
x,y,z=v2_p.T; zmin=float(z.min()); zmax=float(z.max()); h=zmax-zmin; cx=float((x.min()+x.max())*.5); t=(z-zmin)/h

def smooth01(a):
    a=np.clip(a,0.,1.); return a*a*a*(10.+a*(-15.+6.*a))
def window(a,b,c,d): return smooth01((t-a)/(b-a))*(1.-smooth01((t-c)/(d-c)))
# Recover V2 breast membership from the actual baseline->V2 vertical deformation.
# In the source proportion field, breast soft-tissue addition is the only intentional negative-Z component.
raw=np.maximum(0.,-(v2_p[:,2]-base_p[:,2])); raw_max=float(raw.max())
if raw_max<0.001: raise RuntimeError(f'Breast signal unexpectedly weak: {raw_max}')
norm=raw/raw_max
strong=norm>=0.20
breast_band=(t>=.62)&(t<=.82)&(np.abs(x-cx)<=.22*h)
purity=float(np.count_nonzero(strong & breast_band)/max(1,np.count_nonzero(strong)))
if np.count_nonzero(strong)<100 or purity<0.90: raise RuntimeError(f'Breast signal guard failed: strong={np.count_nonzero(strong)}, purity={purity}')
breast_protect=smooth01((norm-BREAST_PROTECT_START)/(BREAST_PROTECT_FULL-BREAST_PROTECT_START))
# Waist front reference from V2 itself, below the correction band, excluding breast-signal vertices.
waist_mask=(t>=.585)&(t<=.615)&(np.abs(x-cx)<=.11*h)&(breast_protect<.05)
if np.count_nonzero(waist_mask)<50: raise RuntimeError('Too few waist reference vertices')
waist_cy=float(np.median(y[waist_mask])); waist_front=float(np.quantile(y[waist_mask],.95))
allowed_front=waist_front+PLUMB_ALLOWANCE_H*h
wz=window(Z_RISE_0,Z_RISE_1,Z_FALL_0,Z_FALL_1)
xh=np.abs(x-cx)/h; torso=1.-smooth01((xh-TORSO_FULL_X_H)/(TORSO_ZERO_X_H-TORSO_FULL_X_H))
frontness=smooth01((y-waist_cy)/(.085*h))
chest=(1.-breast_protect)*wz*torso
overhang=np.maximum(y-allowed_front,0.); retract=np.minimum(overhang,MAX_ANTERIOR_RETRACTION_H*h)
base_dx=-(x-cx)*LATERAL_CONTRACTION*chest
base_dy=-retract*frontness*chest
base_disp=np.column_stack((base_dx,base_dy,np.zeros_like(base_dx)))
# Candidate objects; remove stale diagnostic names first.
for name in NAMES:
    old=bpy.data.objects.get(name)
    if old:
        mesh=old.data if old.type=='MESH' else None; bpy.data.objects.remove(old,do_unlink=True)
        if mesh and mesh.users==0:bpy.data.meshes.remove(mesh)

candidates=[]; metrics=[]
def write_project(vertices,obj,path):
    with open(path,'w',encoding='utf-8',newline='\n') as f:
        f.write('# project X lateral / +Y anterior / +Z up\n')
        for q in vertices:f.write('v %.12f %.12f %.12f\n'%(q[0],q[1],q[2]))
        for poly in obj.data.polygons:
            ids=[int(i)+1 for i in poly.vertices]; f.write('f '+' '.join(str(i) for i in ids)+'\n')

def band_stats(vertices):
    xx,yy,zz=vertices.T; tt=(zz-zmin)/h
    m=(tt>=.635)&(tt<=.655)&(np.abs(xx-cx)<=.12*h)&(breast_protect<.10)
    if np.count_nonzero(m)<20:return {}
    return {'count':int(np.count_nonzero(m)),'front_q90_m':float(np.quantile(yy[m],.90)),'front_over_waist_mm':float((np.quantile(yy[m],.90)-waist_front)*1000.),'width_q95_abs_mm':float(np.quantile(np.abs(xx[m]-cx),.95)*2000.)}

# Persist the exact project-coordinate parent used for this sweep so peers can
# run structural comparisons against candidate outputs without reconstructing it.
v2_project_path=os.path.join(OUTPUT_DIR,'V2_PARENT_PROJECT.obj')
write_project(v2_p,v2,v2_project_path)

for strength,name in zip(STRENGTHS,NAMES):
    proj=v2_p+strength*base_disp
    local=np.column_stack((-proj[:,0],-proj[:,1],proj[:,2]))
    obj=v2.copy(); obj.data=v2.data.copy(); obj.name=name; obj.data.name=name+'_MESH'; bpy.context.scene.collection.objects.link(obj)
    for co,dst in zip(local,obj.data.vertices):dst.co=(float(co[0]),float(co[1]),float(co[2]))
    obj.data.update(); candidates.append(obj)
    dnorm=np.linalg.norm(strength*base_disp,axis=1)
    breast_core=breast_protect>=.95; lower=t<=Z_RISE_0; upper=t>=Z_FALL_1
    path=os.path.join(OUTPUT_DIR,name+'.obj'); write_project(proj,obj,path)
    metrics.append({'name':name,'strength':strength,'project_obj':os.path.basename(path),'project_obj_sha256':hashlib.sha256(open(path,'rb').read()).hexdigest(),'changed_vertices':int(np.count_nonzero(dnorm>1e-12)),'max_displacement_mm':float(dnorm.max()*1000.),'breast_core_vertices':int(np.count_nonzero(breast_core)),'breast_core_max_displacement_mm':float(dnorm[breast_core].max()*1000.) if np.any(breast_core) else None,'lower_body_max_displacement_mm':float(dnorm[lower].max()*1000.) if np.any(lower) else 0.,'above_band_max_displacement_mm':float(dnorm[upper].max()*1000.) if np.any(upper) else 0.,'band_stats':band_stats(proj)})

# Clean matched renders: V2 plus three candidates; FRONT/FRONT_3Q/SIDE.
scene=bpy.context.scene; orig_camera=scene.camera; orig_res=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage); orig_filepath=scene.render.filepath; orig_format=scene.render.image_settings.file_format; orig_transparent=scene.render.film_transparent; orig_world=tuple(scene.world.color) if scene.world else None; orig_hide={o.name:bool(o.hide_render) for o in scene.objects}
subjects=[v2]+candidates; orig_mats={o.name:list(o.data.materials) for o in subjects}; created=[]; neutral=None; rendered=[]; hidden=[]
try:
    for o in scene.objects:
        if o.type!='MESH':continue
        if o in subjects:continue
        if o.name.startswith('GEO-body_female_realistic.eye.'):
            o.hide_render=False;continue
        if o.name==BASE or o.name.startswith('VERA_'):
            o.hide_render=True;hidden.append(o.name)
    neutral=bpy.data.materials.new('__VERA_V3R3_NEUTRAL__'); neutral.use_nodes=True; bsdf=neutral.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(.52,.52,.52,1.); bsdf.inputs['Roughness'].default_value=.72
        if 'Metallic' in bsdf.inputs:bsdf.inputs['Metallic'].default_value=0.
    for o in subjects:o.data.materials.clear();o.data.materials.append(neutral)
    corners=[base.matrix_world@Vector(c) for c in base.bound_box]; xs=[p.x for p in corners];ys=[p.y for p in corners];zs=[p.z for p in corners]; center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2))
    cd=bpy.data.cameras.new('__VERA_V3R3_CAM_DATA__'); cam=bpy.data.objects.new('__VERA_V3R3_CAM__',cd); scene.collection.objects.link(cam);created.append(cam);cd.type='ORTHO';cd.ortho_scale=h*1.10;scene.camera=cam
    def light(name,loc,energy,size):
        ld=bpy.data.lights.new(name+'_DATA',type='AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;o=bpy.data.objects.new(name,ld);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=((center-o.location).to_track_quat('-Z','Y')).to_euler();created.append(o)
    light('__V3R3_KEY__',center+Vector((-1.8,-2.4,2.1)),850,2.3);light('__V3R3_FILL__',center+Vector((2.2,-.5,1.1)),500,2.6);light('__V3R3_RIM__',center+Vector((0,2.4,1.8)),650,2.)
    if scene.world:scene.world.color=(.08,.08,.08)
    scene.render.resolution_x=600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    views=[('FRONT',Vector((0,-3.,0))),('FRONT_3Q',Vector((-2.15,-2.15,0))),('SIDE',Vector((-3.,0,0)))]
    labels=['V2','S055','S080','S100']
    for label,shown in zip(labels,subjects):
        for o in subjects:o.hide_render=(o is not shown)
        for view,offset in views:
            cam.location=center+offset;cam.rotation_euler=((center-cam.location).to_track_quat('-Z','Y')).to_euler(); p=os.path.join(OUTPUT_DIR,f'{label}_{view}.png');scene.render.filepath=p;bpy.ops.render.render(write_still=True);rendered.append(p)
finally:
    for o in subjects:
        o.data.materials.clear()
        for m in orig_mats[o.name]:o.data.materials.append(m)
    for name,state in orig_hide.items():
        o=bpy.data.objects.get(name)
        if o:o.hide_render=state
    scene.camera=orig_camera;scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=orig_res;scene.render.filepath=orig_filepath;scene.render.image_settings.file_format=orig_format;scene.render.film_transparent=orig_transparent
    if scene.world and orig_world is not None:scene.world.color=orig_world
    for o in created:
        data=o.data;bpy.data.objects.remove(o,do_unlink=True)
        if isinstance(data,bpy.types.Camera):bpy.data.cameras.remove(data)
        elif isinstance(data,bpy.types.Light):bpy.data.lights.remove(data)
    if neutral:bpy.data.materials.remove(neutral)

receipt={'schema':'SELFIMAGE_V3R3_BREAST_SIGNAL_PROTECTED_THORAX_SWEEP_V1','status':'EXECUTED_SWEEP / HOSTILE_VISUAL_REVIEW_REQUIRED','v2_coordinate_hash':coord_hash,'v2_project_obj':{'name':os.path.basename(v2_project_path),'sha256':hashlib.sha256(open(v2_project_path,'rb').read()).hexdigest()},'breast_signal':{'max_negative_z_m':raw_max,'strong_vertex_count':int(np.count_nonzero(strong)),'strong_signal_purity_in_breast_band':purity,'protected_core_count':int(np.count_nonzero(breast_protect>=.95))},'field':{'vertical_band_t':[Z_RISE_0,Z_RISE_1,Z_FALL_0,Z_FALL_1],'lateral_contraction':LATERAL_CONTRACTION,'max_anterior_retraction_height_fraction':MAX_ANTERIOR_RETRACTION_H,'plumb_allowance_height_fraction':PLUMB_ALLOWANCE_H,'breast_protect_norm_start_full':[BREAST_PROTECT_START,BREAST_PROTECT_FULL]},'waist_reference':{'waist_front_m':waist_front,'allowed_front_m':allowed_front,'sample_count':int(np.count_nonzero(waist_mask))},'candidates':metrics,'rendered':[os.path.basename(p) for p in rendered],'hidden_competing_body_meshes':hidden,'promotion_ceiling':'WORKSHOP_SWEEP_ONLY / NO_STAGE_A / NO_STABLE_PARENT / NO_CANON'}
with open(os.path.join(OUTPUT_DIR,'SWEEP_RECEIPT.json'),'w',encoding='utf-8') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(receipt,sort_keys=True))
# Clean diagnostic candidate objects from live scene after evidence is written.
for obj in candidates:
    mesh=obj.data; bpy.data.objects.remove(obj,do_unlink=True)
    if mesh.users==0:bpy.data.meshes.remove(mesh)