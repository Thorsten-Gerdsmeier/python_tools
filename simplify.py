blender --background --python simplify_for_3d_print.py -- model.blend printable_model.blend --voxel-size 0.4

"""
Simplify a Blender scene for 3D printing.

Example:
    blender --background --python simplify_for_3d_print.py -- \
        input.blend output.blend --voxel-size 0.4 --decimate-ratio 0.7

Voxel remeshing removes surface features smaller than the specified voxel size
and can repair small gaps. Decimation further lowers polygon count afterward.
"""

import argparse
import os
import sys
import bpy


def parse_args():
    command_args = (
        sys.argv[sys.argv.index("--") + 1:]
        if "--" in sys.argv
        else []
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("input_blend", help="Source Blender file")
    parser.add_argument("output_blend", help="Simplified Blender file")
    parser.add_argument(
        "--voxel-size",
        type=float,
        default=0.4,
        help="Smallest retained feature size in scene units; default: 0.4",
    )
    parser.add_argument(
        "--decimate-ratio",
        type=float,
        default=1.0,
        help="Keep this fraction of faces after remeshing; default: 1.0",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Also process mesh objects hidden in the viewport",
    )
    return parser.parse_args(command_args)


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def simplify_object(obj, voxel_size, decimate_ratio):
    """Replace tiny mesh detail with a printable-resolution mesh."""
    activate(obj)

    # Give linked instances independent geometry before altering them.
    if obj.data.users > 1:
        obj.data = obj.data.copy()

    # Shape keys cannot survive a remesh; they are not useful in a static print.
    if obj.data.shape_keys:
        obj.shape_key_clear()

    # Ensure the voxel size is evaluated consistently in world dimensions.
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    remesh = obj.modifiers.new("Print detail filter", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = voxel_size
    if hasattr(remesh, "use_smooth_shade"):
        remesh.use_smooth_shade = True

    bpy.ops.object.modifier_apply(modifier=remesh.name)

    # Optional post-filter: reduce triangle count while retaining the new form.
    if decimate_ratio < 1.0:
        decimate = obj.modifiers.new("Polygon reduction", "DECIMATE")
        decimate.ratio = decimate_ratio
        bpy.ops.object.modifier_apply(modifier=decimate.name)

    # Final cleanup and normal correction.
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.00001)
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def main():
    options = parse_args()

    if options.voxel_size <= 0:
        raise ValueError("--voxel-size must be greater than zero")
    if not 0 < options.decimate_ratio <= 1:
        raise ValueError("--decimate-ratio must be greater than 0 and at most 1")

    source = os.path.abspath(options.input_blend)
    output = os.path.abspath(options.output_blend)

    if not os.path.isfile(source):
        raise FileNotFoundError(f"Input file not found: {source}")

    bpy.ops.wm.open_mainfile(filepath=source)

    meshes = [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH"
        and (options.include_hidden or not obj.hide_get())
    ]

    if not meshes:
        raise RuntimeError("No eligible mesh objects were found.")

    for obj in meshes:
        simplify_object(obj, options.voxel_size, options.decimate_ratio)
        print(f"Simplified: {obj.name}")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=output)
    print(f"Saved printable model: {output}")


if __name__ == "__main__":
    main()