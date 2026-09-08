# V3R2: Blender-local execution of Vera SI's current corrected thorax field.
# Source binding:
#   selfimage/vera-parametric-body-construction-v1@b4ec68580c35800cf0dcbf2fb0e5f57e0fb1ed35
#   build_v3_underbust_thorax_correction_v1.py blob
#   sha256 6886c0a9f1ac63ee3d8528ac34778fa19f09924b
#
# The exact V2 parent is transformed into Vera's project coordinates
# (X lateral / +Y anterior / +Z up), the field is applied there, then the
# candidate is transformed back to Blender-local coordinates for rendering.
# Diagnostic study only. No Stage-A, stable-parent, or UV qualification.

import bpy, hashlib, json, math, os
from collections import Counter
from mathutils import Vector
import numpy as np

OUTPUT_DIR = globals().get('OUTPUT_DIR')
if not OUTPUT_DIR:
    raise RuntimeError('Relay did not provide OUTPUT_DIR')
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE='GEO-body_female_realistic'
V2='VERA_PROPORTION_STUDY_V2'
V3='VERA_THORAX_CORRECTION_STUDY_V3R2'
NV=42342
NP=84680
EXPECTED_V2_COORD_HASH='1357fe99a4458c499dcd16d3f442c22d3e9aa92625b7dc7ab08924737bcdf7e6'
SOURCE_COMMIT='b4ec68580c35800cf0dcbf2fb0e5f57e0fb1ed35'
SOURCE_BUILDER_SHA256='6886c0a9f1ac63ee3d8528ac34778fa19f09924b'

# Exact constants from Vera SI current builder.
Z_RISE_0,Z_RISE_1,Z_FALL_0,Z_FALL_1=0.625,0.645,0.695,0.720
WAIST_T=0.615
LATERAL_CONTRACTION=0.045
MAX_ANTERIOR_RETRACTION_H=0.025
PLUMB_ALLOWANCE_H=0.003
TORSO_FULL_X_H,TORSO_ZERO_X_H=0.10,0.17
BREAST_PROTECT_Z0,BREAST_PROTECT_Z1=0.675,0.705
BREAST_PROTECT_FRONT0_H,BREAST_PROTECT_FRONT1_H=0.008,0.043

base=bpy.data.objects.get(BASE)
v2=bpy.data.objects.get(V2)
if not base or not v2 or base.type!='MESH' or v2.type!='MESH':
    raise RuntimeError('Expected baseline and exact V2 parent are not both present')
for o in (base,v2):
    if len(o.data.vertices)!=NV or len(o.data.polygons)!=NP:
        raise RuntimeError('Topology/count guard failed')

# Verify the in-scene V2 coordinates against the exact retrievable artifact.
local_v2=np.asarray([[float(v.co.x),float(v.co.y),float(v.co.z)] for v in v2.data.vertices],dtype=np.float64)
coord_hash=hashlib.sha256(np.round(local_v2,9).astype('<f8',copy=False).tobytes(order='C')).hexdigest()
if coord_hash!=EXPECTED_V2_COORD_HASH:
    raise RuntimeError(f'V2 coordinate hash mismatch: expected {EXPECTED_V2_COORD_HASH}, got {coord_hash}')

old=bpy.data.objects.get(V3)
if old:
    mesh=old.data if old.type=='MESH' else None
    bpy.data.objects.remove(old,do_unlink=True)
    if mesh and mesh.users==0:
        bpy.data.meshes.remove(mesh)
v3=v2.copy();v3.data=v2.data.copy();v3.name=V3;v3.data.name=V3+'_MESH';bpy.context.scene.collection.objects.link(v3)

# Determinant-positive mapping from Blender local (-Y anterior) to Vera project
# coordinates (+Y anterior): project X=-local X; project Y=-local Y; Z unchanged.
proj=np.column_stack((-local_v2[:,0],-local_v2[:,1],local_v2[:,2]))

# Context values were derived from this exact V2 artifact using Vera's own
# triangle-section context method. They are valid only under the verified hash.
CTX={
 'zmin':0.00197131699,
 'zmax':1.641345143318,
 'height':1.639373826328,
 'center_x':4.7281384499997525e-05,
 'waist_center_y':0.04485522612693412,
 'waist_anterior':0.14907801330000453,
 'waist_width':0.3125336529222503,
 'waist_depth':0.19088395835797234,
}

def smooth01(t):
    t=np.clip(t,0.,1.)
    return t*t*t*(10.+t*(-15.+6.*t))

def vertical_window(t):
    return smooth01((t-Z_RISE_0)/(Z_RISE_1-Z_RISE_0))*(1.-smooth01((t-Z_FALL_0)/(Z_FALL_1-Z_FALL_0)))

x,y,z=proj.T;h=CTX['height'];cx=CTX['center_x'];waist_cy=CTX['waist_center_y'];waist_front=CTX['waist_anterior']
t=(z-CTX['zmin'])/h;wz=vertical_window(t)
xh=np.abs(x-cx)/h;torso=1.-smooth01((xh-TORSO_FULL_X_H)/(TORSO_ZERO_X_H-TORSO_FULL_X_H))
frontness=smooth01((y-waist_cy)/(0.09*h))
protect_z=smooth01((t-BREAST_PROTECT_Z0)/(BREAST_PROTECT_Z1-BREAST_PROTECT_Z0))
protect_front=smooth01((((y-waist_front)/h)-BREAST_PROTECT_FRONT0_H)/(BREAST_PROTECT_FRONT1_H-BREAST_PROTECT_FRONT0_H))
breast_protect=protect_z*protect_front
lateral_field=1.-0.90*breast_protect
dx=-(x-cx)*LATERAL_CONTRACTION*wz*torso*lateral_field
overhang=np.maximum(y-(waist_front+PLUMB_ALLOWANCE_H*h),0.)
retract=np.minimum(overhang,MAX_ANTERIOR_RETRACTION_H*h)
dy=-retract*wz*torso*frontness*(1.-breast_protect)
disp=np.column_stack([dx,dy,np.zeros_like(dx)])
proj_v3=proj+disp
local_v3=np.column_stack((-proj_v3[:,0],-proj_v3[:,1],proj_v3[:,2]))
for co,dst in zip(local_v3,v3.data.vertices):
    dst.co=(float(co[0]),float(co[1]),float(co[2]))
v3.data.update()

dnorm=np.linalg.norm(disp,axis=1)

# Structural local guard.
usage=Counter()
for poly in v3.data.polygons:
    ids=list(poly.vertices)
    for i in range(len(ids)):
        a,b=ids[i],ids[(i+1)%len(ids)]
        if a>b:a,b=b,a
        usage[(a,b)]+=1
nonmanifold_edges=sum(1 for n in usage.values() if n!=2)
nonpositive_faces=sum(1 for p in v3.data.polygons if p.area<=0.)

# Export project-coordinate V2 and V3 bytes directly for Vera hostile gate.
def write_project_obj(vertices, obj, path):
    with open(path,'w',encoding='utf-8',newline='\n') as f:
        f.write('# Self Image project coordinates: X lateral / +Y anterior / +Z up\n')
        for q in vertices:
            f.write('v %.12f %.12f %.12f\n' % (q[0],q[1],q[2]))
        for poly in obj.data.polygons:
            ids=[int(i)+1 for i in poly.vertices]
            f.write('f '+' '.join(str(i) for i in ids)+'\n')

v2_project=os.path.join(OUTPUT_DIR,'V2_PARENT_PROJECT.obj')
v3_project=os.path.join(OUTPUT_DIR,'V3R2_THORAX_CANDIDATE_PROJECT.obj')
write_project_obj(proj,v2,v2_project)
write_project_obj(proj_v3,v3,v3_project)

# Full matched five-view neutral renders.
scene=bpy.context.scene
orig_camera=scene.camera
orig_res=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)
orig_filepath=scene.render.filepath
orig_format=scene.render.image_settings.file_format
orig_transparent=scene.render.film_transparent
orig_world=tuple(scene.world.color) if scene.world else None
orig_hide={o.name:bool(o.hide_render) for o in scene.objects}
render_objs=[v2,v3]
orig_mats={o.name:list(o.data.materials) for o in render_objs}
created=[];neutral=None;rendered=[]
try:
    neutral=bpy.data.materials.new('__VERA_V3R2_NEUTRAL__');neutral.use_nodes=True
    bsdf=neutral.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(.52,.52,.52,1.);bsdf.inputs['Roughness'].default_value=.72
        if 'Metallic' in bsdf.inputs:bsdf.inputs['Metallic'].default_value=0.
    for o in render_objs:o.data.materials.clear();o.data.materials.append(neutral)
    corners=[base.matrix_world@Vector(c) for c in base.bound_box]
    xs=[p.x for p in corners];ys=[p.y for p in corners];zs=[p.z for p in corners]
    center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2))
    cd=bpy.data.cameras.new('__VERA_V3R2_CAM_DATA__');cam=bpy.data.objects.new('__VERA_V3R2_CAM__',cd);scene.collection.objects.link(cam);created.append(cam);cd.type='ORTHO';cd.ortho_scale=CTX['height']*1.10;scene.camera=cam
    def light(name,loc,energy,size):
        ld=bpy.data.lights.new(name+'_DATA',type='AREA');ld.energy=energy;ld.shape='DISK';ld.size=size
        o=bpy.data.objects.new(name,ld);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=((center-o.location).to_track_quat('-Z','Y')).to_euler();created.append(o)
    light('__V3R2_KEY__',center+Vector((-1.8,-2.4,2.1)),850,2.3)
    light('__V3R2_FILL__',center+Vector((2.2,-.5,1.1)),500,2.6)
    light('__V3R2_RIM__',center+Vector((0,2.4,1.8)),650,2.)
    if scene.world:scene.world.color=(.08,.08,.08)
    scene.render.resolution_x=600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    views=[('FRONT',Vector((0,-3.,0))),('FRONT_3Q',Vector((-2.15,-2.15,0))),('SIDE',Vector((-3.,0,0))),('REAR_3Q',Vector((-2.15,2.15,0))),('REAR',Vector((0,3.,0)))]
    for label,shown in [('V2',v2),('V3R2',v3)]:
        for o in render_objs:o.hide_render=(o is not shown)
        for view_name,view_offset in views:
            cam.location=center+view_offset;cam.rotation_euler=((center-cam.location).to_track_quat('-Z','Y')).to_euler()
            path=os.path.join(OUTPUT_DIR,f'{label}_{view_name}.png');scene.render.filepath=path;bpy.ops.render.render(write_still=True);rendered.append(path)
finally:
    for o in render_objs:
        o.data.materials.clear()
        for mat in orig_mats[o.name]:o.data.materials.append(mat)
    for name,state in orig_hide.items():
        obj=bpy.data.objects.get(name)
        if obj:obj.hide_render=state
    scene.camera=orig_camera;scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=orig_res;scene.render.filepath=orig_filepath;scene.render.image_settings.file_format=orig_format;scene.render.film_transparent=orig_transparent
    if scene.world and orig_world is not None:scene.world.color=orig_world
    for o in created:
        data=o.data;bpy.data.objects.remove(o,do_unlink=True)
        if isinstance(data,bpy.types.Camera):bpy.data.cameras.remove(data)
        elif isinstance(data,bpy.types.Light):bpy.data.lights.remove(data)
    if neutral:bpy.data.materials.remove(neutral)

blend_path=os.path.join(OUTPUT_DIR,'VERA_THORAX_CORRECTION_STUDY_V3R2.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path,copy=True)
metrics={
 'schema':'VERA_THORAX_CORRECTION_STUDY_BLENDER_V3R2',
 'status':'EXECUTED_VERA_FIELD / HOSTILE_REVIEW_REQUIRED / NOT_ACCEPTED / NO_STAGE_A_PASS',
 'source_binding':{'commit':SOURCE_COMMIT,'builder_sha256':SOURCE_BUILDER_SHA256},
 'v2_coordinate_hash':coord_hash,'v2_expected_coordinate_hash':EXPECTED_V2_COORD_HASH,
 'parent':V2,'candidate':V3,'vertices':NV,'polygons':NP,
 'topology_counts_preserved':len(v3.data.vertices)==len(v2.data.vertices) and len(v3.data.polygons)==len(v2.data.polygons),
 'candidate_nonmanifold_edges_by_face_use':nonmanifold_edges,'candidate_nonpositive_faces':nonpositive_faces,
 'changed_vertex_count':int(np.count_nonzero(dnorm>1e-12)),'max_displacement_m':float(dnorm.max()),'rms_displacement_m':float(math.sqrt(float(np.mean(dnorm*dnorm)))),
 'strongly_protected_breast_vertex_count':int(np.count_nonzero(breast_protect>=.95)),
 'strongly_protected_breast_max_displacement_m':float(dnorm[breast_protect>=.95].max()) if np.any(breast_protect>=.95) else None,
 'field':{'vertical_band_t':[Z_RISE_0,Z_RISE_1,Z_FALL_0,Z_FALL_1],'lateral_contraction':LATERAL_CONTRACTION,'max_anterior_retraction_height_fraction':MAX_ANTERIOR_RETRACTION_H,'plumb_allowance_height_fraction':PLUMB_ALLOWANCE_H,'breast_protect_z_t':[BREAST_PROTECT_Z0,BREAST_PROTECT_Z1]},
 'mesh_exports':[os.path.basename(v2_project),os.path.basename(v3_project)],'rendered':[os.path.basename(p) for p in rendered],'saved_blend_copy':os.path.basename(blend_path),
 'required_next':['run Vera SI hostile scalar gate on exact project-coordinate exports','Vera SI hostile visual review of matched views','reject regardless of metrics if visible anatomy is wrong'],
 'promotion_ceiling':'WORKSHOP_STUDY_ONLY / NO_STAGE_A / NO_STABLE_PARENT / NO_CANON'
}
with open(os.path.join(OUTPUT_DIR,'VERA_THORAX_CORRECTION_STUDY_V3R2_METRICS.json'),'w',encoding='utf-8') as f:json.dump(metrics,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(metrics,sort_keys=True))
