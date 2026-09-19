blender --background --python stl_to_blender.py -- input.stl output.blend


"""Import an STL, prepare its mesh, and save it as a Blender scene."""

import argparse
import os
import sys
import bpy


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("input_stl")
    parser.add_argument("output_blend")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--voxel-size", type=float, default=0.25)
    parser.add_argument("--no-remesh", action="store_true")
    parser.add_argument("--export-stl", default=None)
    return parser.parse_args(argv)


def main():
    opt = args()
    source = os.path.abspath(opt.input_stl)
    destination = os.path.abspath(opt.output_blend)

    if not os.path.isfile(source):
        raise FileNotFoundError(f"Input STL not found: {source}")
    if opt.scale <= 0 or opt.voxel_size <= 0:
        raise ValueError("Scale and voxel size must be positive.")

    # Start with an empty scene.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Import supports Blender 4.x and legacy Blender 3.x add-on API.
    try:
        bpy.ops.wm.stl_import(filepath=source, global_scale=opt.scale)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=source, global_scale=opt.scale)

    meshes = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("STL import produced no mesh.")

    # Combine multiple STL shells into one model.
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()

    model = bpy.context.active_object
    model.name = "STL_Model"

    # Basic mesh repair / cleanup.
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.00001)
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    for polygon in model.data.polygons:
        polygon.use_smooth = True

    # Voxel remesh is useful for a solid, printable-looking result.
    if not opt.no_remesh:
        remesh = model.modifiers.new("Watertight voxel remesh", "REMESH")
        remesh.mode = "VOXEL"
        remesh.voxel_size = opt.voxel_size
        remesh.use_smooth_shade = True

    bevel = model.modifiers.new("Edge softening", "BEVEL")
    bevel.width = max(opt.voxel_size * 0.15, 0.001)
    bevel.segments = 2
    bevel.limit_method = "ANGLE"

    material = bpy.data.materials.new("STL Material")
    material.diffuse_color = (0.28, 0.55, 0.82, 1.0)
    model.data.materials.append(material)

    # Save the editable Blender model.
    os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=destination)

    # Optional export of the cleaned model as a new STL.
    if opt.export_stl:
        bpy.ops.object.select_all(action="DESELECT")
        model.select_set(True)
        bpy.context.view_layer.objects.active = model
        try:
            bpy.ops.wm.stl_export(
                filepath=os.path.abspath(opt.export_stl),
                export_selected_objects=True,
            )
        except AttributeError:
            bpy.ops.export_mesh.stl(
                filepath=os.path.abspath(opt.export_stl),
                use_selection=True,
            )

    print(f"Created Blender file: {destination}")


if __name__ == "__main__":
    main()




# STL dimensions are millimetres; convert to Blender metres
blender --background --python stl_to_blender.py -- input.stl output.blend --scale 0.001

# Preserve the exact original triangulated topology
blender --background --python stl_to_blender.py -- input.stl output.blend --no-remesh

# Also export the prepared mesh as STL
blender --background --python stl_to_blender.py -- input.stl output.blend --export-stl cleaned.stl