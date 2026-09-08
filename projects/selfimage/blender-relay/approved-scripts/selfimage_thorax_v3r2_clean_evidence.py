# Clean evidence renderer for V2 vs V3R2. No geometry mutation.
# Hides all competing body-study meshes so silhouette/shading cannot be
# contaminated by overlapping baseline/V1/failed-study objects.

import bpy, json, os
from mathutils import Vector

OUTPUT_DIR=globals().get('OUTPUT_DIR')
if not OUTPUT_DIR: raise RuntimeError('Relay did not provide OUTPUT_DIR')
os.makedirs(OUTPUT_DIR,exist_ok=True)
V2='VERA_PROPORTION_STUDY_V2'; V3='VERA_THORAX_CORRECTION_STUDY_V3R2'; BASE='GEO-body_female_realistic'
v2=bpy.data.objects.get(V2);v3=bpy.data.objects.get(V3);base=bpy.data.objects.get(BASE)
if not v2 or not v3 or not base: raise RuntimeError('V2/V3R2/baseline missing')
if any(o.type!='MESH' for o in (v2,v3,base)): raise RuntimeError('Body object type guard failed')
if len(v2.data.vertices)!=42342 or len(v3.data.vertices)!=42342 or len(v2.data.polygons)!=84680 or len(v3.data.polygons)!=84680: raise RuntimeError('Topology/count guard failed')

scene=bpy.context.scene
orig_camera=scene.camera;orig_res=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage);orig_filepath=scene.render.filepath;orig_format=scene.render.image_settings.file_format;orig_transparent=scene.render.film_transparent;orig_world=tuple(scene.world.color) if scene.world else None
orig_hide={o.name:bool(o.hide_render) for o in scene.objects}
orig_mats={o.name:list(o.data.materials) for o in (v2,v3)}
created=[];neutral=None;rendered=[];hidden_competitors=[]
try:
    # Hide every body-study mesh except the selected body and preserve the two
    # dedicated eye objects. This prevents overlapping meshes from corrupting
    # the visual gate while retaining facial eye geometry.
    for o in scene.objects:
        if o.type!='MESH': continue
        if o.name in (V2,V3): continue
        if o.name.startswith('GEO-body_female_realistic.eye.'):
            o.hide_render=False; continue
        if o.name==BASE or o.name.startswith('VERA_'):
            o.hide_render=True; hidden_competitors.append(o.name)

    neutral=bpy.data.materials.new('__VERA_V3R2_CLEAN_NEUTRAL__');neutral.use_nodes=True
    bsdf=neutral.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(.52,.52,.52,1.);bsdf.inputs['Roughness'].default_value=.72
        if 'Metallic' in bsdf.inputs:bsdf.inputs['Metallic'].default_value=0.
    for o in (v2,v3):o.data.materials.clear();o.data.materials.append(neutral)

    corners=[base.matrix_world@Vector(c) for c in base.bound_box];xs=[p.x for p in corners];ys=[p.y for p in corners];zs=[p.z for p in corners]
    center=Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,(min(zs)+max(zs))/2));height=max(zs)-min(zs)
    cd=bpy.data.cameras.new('__VERA_V3R2_CLEAN_CAM_DATA__');cam=bpy.data.objects.new('__VERA_V3R2_CLEAN_CAM__',cd);scene.collection.objects.link(cam);created.append(cam);cd.type='ORTHO';cd.ortho_scale=height*1.10;scene.camera=cam
    def light(name,loc,energy,size):
        ld=bpy.data.lights.new(name+'_DATA',type='AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;o=bpy.data.objects.new(name,ld);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=((center-o.location).to_track_quat('-Z','Y')).to_euler();created.append(o)
    light('__V3R2C_KEY__',center+Vector((-1.8,-2.4,2.1)),850,2.3);light('__V3R2C_FILL__',center+Vector((2.2,-.5,1.1)),500,2.6);light('__V3R2C_RIM__',center+Vector((0,2.4,1.8)),650,2.)
    if scene.world:scene.world.color=(.08,.08,.08)
    scene.render.resolution_x=600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    views=[('FRONT',Vector((0,-3.,0))),('FRONT_3Q',Vector((-2.15,-2.15,0))),('SIDE',Vector((-3.,0,0))),('REAR_3Q',Vector((-2.15,2.15,0))),('REAR',Vector((0,3.,0)))]
    for label,shown,other in [('V2',v2,v3),('V3R2',v3,v2)]:
        shown.hide_render=False;other.hide_render=True
        for view_name,offset in views:
            cam.location=center+offset;cam.rotation_euler=((center-cam.location).to_track_quat('-Z','Y')).to_euler();path=os.path.join(OUTPUT_DIR,f'{label}_{view_name}_CLEAN.png');scene.render.filepath=path;bpy.ops.render.render(write_still=True);rendered.append(path)
finally:
    for o in (v2,v3):
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
receipt={'schema':'SELFIMAGE_V3R2_CLEAN_VISUAL_EVIDENCE_V1','status':'RENDERED / HOSTILE_VISUAL_REVIEW_REQUIRED','geometry_mutated':False,'subjects':[V2,V3],'hidden_competing_body_meshes':hidden_competitors,'views':['FRONT','FRONT_3Q','SIDE','REAR_3Q','REAR'],'outputs':[os.path.basename(p) for p in rendered]}
with open(os.path.join(OUTPUT_DIR,'CLEAN_RENDER_RECEIPT.json'),'w',encoding='utf-8') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(receipt,sort_keys=True))
