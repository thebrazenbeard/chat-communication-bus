"""Self Image Blender scene audit V1.

Pure scene inspection for execution through the local Blender-MCP bridge.
No filesystem, network, subprocess, package-install, save, import, export, or
scene mutation is performed.

The script prints one machine-readable line prefixed with:
  SELFIMAGE_BLENDER_SCENE_AUDIT_V1::
"""

import json

import bmesh
import bpy


def mesh_audit(obj):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    try:
        boundary_edges = 0
        nonmanifold_edges = 0
        wire_edges = 0
        for e in bm.edges:
            linked = len(e.link_faces)
            if linked == 1:
                boundary_edges += 1
            if linked != 2:
                nonmanifold_edges += 1
            if linked == 0:
                wire_edges += 1
    finally:
        bm.free()

    return {
        "name": obj.name,
        "data_name": me.name,
        "vertices": len(me.vertices),
        "edges": len(me.edges),
        "polygons": len(me.polygons),
        "loops": len(me.loops),
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "wire_edges": wire_edges,
        "uv_layers": [layer.name for layer in me.uv_layers],
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
        "modifiers": [
            {
                "name": mod.name,
                "type": mod.type,
                "show_viewport": bool(mod.show_viewport),
                "show_render": bool(mod.show_render),
            }
            for mod in obj.modifiers
        ],
        "vertex_groups": [group.name for group in obj.vertex_groups],
        "dimensions": [float(v) for v in obj.dimensions],
        "location": [float(v) for v in obj.location],
        "rotation_euler": [float(v) for v in obj.rotation_euler],
        "scale": [float(v) for v in obj.scale],
        "hide_viewport": bool(obj.hide_viewport),
        "hide_render": bool(obj.hide_render),
    }


def main():
    scene = bpy.context.scene
    objects = []
    for obj in scene.objects:
        row = {
            "name": obj.name,
            "type": obj.type,
            "selected": bool(obj.select_get()),
            "hide_viewport": bool(obj.hide_viewport),
            "hide_render": bool(obj.hide_render),
        }
        if obj.type == "MESH":
            row["mesh"] = mesh_audit(obj)
        objects.append(row)

    expected_name = "GEO-body_female_realistic"
    body = scene.objects.get(expected_name)
    expected_body = {
        "object_name": expected_name,
        "present": body is not None,
        "expected_vertices_on_selected_mirror_transport": 42342,
        "expected_triangles_on_selected_mirror_transport": 84680,
    }
    if body is not None and body.type == "MESH":
        expected_body.update(
            {
                "actual_vertices": len(body.data.vertices),
                "actual_polygons": len(body.data.polygons),
                "vertex_count_matches_selected_transport": len(body.data.vertices) == 42342,
                "polygon_count_matches_selected_transport": len(body.data.polygons) == 84680,
                "uv_layer_count": len(body.data.uv_layers),
            }
        )

    payload = {
        "schema": "SELFIMAGE_BLENDER_SCENE_AUDIT_V1",
        "status": "READ_ONLY_SCENE_AUDIT",
        "blender_version": list(bpy.app.version),
        "blender_version_string": bpy.app.version_string,
        "scene": scene.name,
        "render_engine": scene.render.engine,
        "active_object": bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
        "camera": scene.camera.name if scene.camera else None,
        "object_count": len(scene.objects),
        "objects": objects,
        "selected_cc0_body_check": expected_body,
        "nonclaims": [
            "No source-file hash verified by this scene-only script",
            "No object or scene mutation performed",
            "No morphology acceptance or Stage-A promotion",
        ],
    }
    print("SELFIMAGE_BLENDER_SCENE_AUDIT_V1::" + json.dumps(payload, sort_keys=True))


main()
