# Duerkopp windows
import sys
import os
import math
from mathutils import Vector
from typing import Tuple
import bpy
import bmesh

# --- Determine script directory ---
try:
    # works if the .py file has been saved to disk
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # fallback: if run from Blender Text Editor unsaved
    script_dir = bpy.path.abspath("//")

if script_dir not in sys.path:
    sys.path.append(script_dir)

from svg_gen_window_with_description import WindowSpec

def create_wedge(p1, p2, p3, depth, frame_width, frame_depth):
    """
    Creates a prism with a triangular base and a specified depth.
    
    Parameters:
        name (str): Name of the new object.
        p1, p2, p3 (tuple): Three (x, y, z) points defining the triangle.
        depth (float): Depth to extrude the triangle along the Y-axis.
    """
    # Convert to Vector for math operations
    p1 = Vector(p1)
    p2 = Vector(p2)
    p3 = Vector(p3)

    # Extrude direction (along Y axis)
    offset = Vector((0, depth, 0))

    # Define vertices of the prism
    verts = [
        p1, p2, p3,                 # base
        p1 + offset,
        p2 + offset,
        p3 + offset                 # top face
    ]

    # Define faces by vertex indices
    faces = [
        (0, 1, 2),  # base
        (3, 4, 5),  # top
        (0, 1, 4, 3),  # side
        (1, 2, 5, 4),  # side
        (2, 0, 3, 5),  # side
    ]

    # Create mesh and object
    mesh = bpy.data.meshes.new("wedge" + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("wedge", mesh)
    bpy.context.collection.objects.link(obj)
    
    rotation_radians = math.radians(90)    
    obj.rotation_euler[2] += rotation_radians
    obj.name = "obj1"
    bpy.ops.object.transform_apply(scale=True)
    obj.location = (depth/2, -frame_depth/2-1, -1)
    
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj2 = bpy.context.active_object
    obj2.name = "obj2"
    obj2.scale = (depth, frame_depth, 1)
    obj2.location = (0, 0, -0.5)
    bpy.ops.object.transform_apply(scale=True)

    obj.select_set(True)
    obj2.select_set(True)
    #bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()

    return obj



def create_triangular_prism(base_width=30.0, height=40.0, depth=50.0, location=(0.0, 0.0, 0.0)):
    """Deletes all objects and creates a triangular prism in Blender.

    Parameters:
    - base_width_mm: Width of the triangle base (X axis) in millimeters
    - height_mm: Height of the triangle (Y axis) in millimeters
    - depth_mm: Length of the prism along the Z axis in millimeters
    - location: Tuple of (x, y, z) coordinates for prism location in meters
    """

    # --- Step 1: Delete all objects ---
    #bpy.ops.object.select_all(action='SELECT')
    #bpy.ops.object.delete(use_global=False)
    #bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

   
    # --- Step 3: Define vertices and faces ---
    verts = [
        Vector((0, 0, 0)),
        Vector((base_width, 0, 0)),
        Vector((base_width / 2, height, 0)),

        Vector((0, 0, depth)),
        Vector((base_width, 0, depth)),
        Vector((base_width / 2, height, depth)),
    ]

    faces = [
        (0, 1, 2),      # Front triangle
        (3, 5, 4),      # Back triangle (reverse winding)
        (0, 2, 5, 3),   # Side face 1
        (2, 1, 4, 5),   # Side face 2
        (1, 0, 3, 4),   # Bottom face
    ]

    # --- Step 4: Create mesh and object ---
    mesh = bpy.data.meshes.new(name="TriangularPrismMesh")
    obj = bpy.data.objects.new("TriangularPrism", mesh)
    bpy.context.collection.objects.link(obj)

    # Create geometry
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Set object location
    obj.location = Vector(location)
    
    # Select and focus on the object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_selected(override)
                    break
    obj.select_set(True)
    

def create_window_frame(
    width=30.0,
    height=40.0,
    frame_width=1.0,
    frame_depth=2.0,
    triangle_height=10,
    export_path=None
):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
        
    base_height = height 
        
    cutout_width = width - 2 * frame_width
    cutout_height = base_height + 2

    # Outer base frame
    bpy.ops.mesh.primitive_cube_add(size=2)
    base_outer = bpy.context.active_object
    base_outer.name = "Base_Outer"
    base_outer.scale = (width / 2, frame_depth / 2, base_height / 2)
    base_outer.location = (0, 0, base_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Inner base cutout
    bpy.ops.mesh.primitive_cube_add(size=2)
    base_inner = bpy.context.active_object
    base_inner.name = "Base_Inner"
    """
    The following lines are options for a window with no upper frame
    base_inner.scale = (cutout_width / 2, frame_depth, cutout_height / 2)
    base_inner.location = (0, 0, frame_width + cutout_height / 2)
    """
    base_inner.scale = (cutout_width / 2, frame_depth, (base_height- 2 * frame_width) / 2)
    base_inner.location = (0, 0, base_height  / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Boolean difference for base
    mod = base_outer.modifiers.new(name="CutBase", type='BOOLEAN')
    mod.object = base_inner
    mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = base_outer
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(base_inner)
    base_outer.select_set(True)
    
    rotate_active_object('X', -90)
    create_triangular_prism(base_width=width, height=triangle_height, depth=frame_depth, location=(-width/2, height, -frame_depth/2))
    bpy.ops.object.join()
    

def rotate_active_object(rotation_axis='X', rotation_degrees = 90):
    # Define rotation parameters
    # axis =  'X', 'Y', or 'Z'

    # Convert degrees to radians
    rotation_radians = math.radians(rotation_degrees)

    # Get the active object
    obj = bpy.context.active_object

    # Apply rotation
    if obj:
       if rotation_axis == 'X':
           obj.rotation_euler[0] += rotation_radians
       elif rotation_axis == 'Y':
           obj.rotation_euler[1] += rotation_radians
       elif rotation_axis == 'Z':
           obj.rotation_euler[2] += rotation_radians
       else:
           print("Invalid axis. Use 'X', 'Y', or 'Z'.")
    else:
        print("No active object selected.")

"""
# Example usage
# Set the unit system to 'METRIC'
bpy.context.scene.unit_settings.system = 'METRIC'
# Set the unit scale so 1 Blender unit = 1 mm
bpy.context.scene.unit_settings.scale_length = 0.001
# Optional: set the unit display to millimeters
bpy.context.scene.unit_settings.use_separate = True  # Use subunits like mm, cm, etc.

create_window_frame(width=30, height=40,frame_width=2.0, frame_depth=2.0, triangle_height=10, export_path=None)
"""

"""
obj = create_wedge(
    p1=(0, 0, 0),
    p2=(1, 0, 0),
    p3=(1, 0, 1),
    depth=3,
    frame_width=30,
    frame_depth=2
)
"""

# generate arched window  

def x_at_arch_height_y(chord: float, sagitta: float, y: float) -> Tuple[float, float]: 
    """ 
    Compute x1 and x2 of an arch at vertical coordinate y, 
    given the chord length and sagitta. 
    Args: 
    chord (float): Total chord length (distance between arch ends). 
    sagitta (float): Maximum height (sagitta) of the arch at midpoint. 
    y (float): Vertical coordinate of the arc in [0..sagitta]. 
    Returns: 
    float: x1 and float:x2 of the arch at y. 
    """  
    # Calculate the distance from the center of the arch to the point x
    # Radius of the circle that forms the arch 
    r = ((chord/2)**2 + sagitta**2) / (2 * sagitta) 

    if (y > sagitta) or (y < 0): 
        raise ValueError("x must be within the range of the chord length.")

    y_center = y + (r - sagitta)
    # Compute y(x) from the circle equation: x^2 + y^2 = r^2 
    x = math.sqrt(r ** 2 - y_center ** 2) 
    x1 = chord / 2 - x
    x2 = chord / 2 + x 
    
    return x1, x2



def arch_height_at_x(chord: float, sagitta: float, x: float) -> float: 
    """ 
    Compute the height of an arch at horizontal coordinate x, 
    given the chord length and sagitta. Args: chord (float): 
    Total chord length (distance between arch ends). 
    sagitta (float): Maximum height (sagitta) of the arch at midpoint. 
    x (float): Horizontal coordinate from center (-chord/2 to +chord/2). 
    Returns: float: Height of the arch at x. 
    """  
    # Calculate the distance from the center of the arch to the point x
    # Radius of the circle that forms the arch 
    if sagitta == 0:
        return 0
    else: 
        r = ((chord/2)**2 + sagitta**2) / (2 * sagitta) 
        if (x < 0) or (x > chord): 
            raise ValueError("x must be within the range of the chord length.")
        if x > chord / 2:   
            x1 = x - chord / 2
            y = math.sqrt(r ** 2 - x1 ** 2) 
        if x < chord / 2: 
            x1 = chord - x - chord / 2
            y = math.sqrt(r ** 2 - x1 ** 2)      
        if x == chord / 2: 
            x1 = 0  
    
        # Distance from center to arc base along y-axis (arch base is at y = 0) 
        y_center = r - sagitta 
        # Compute y(x) from the circle equation: x^2 + y^2 = r^2 
        y = math.sqrt(r ** 2 - x1 ** 2) 
        y = y - y_center
        print("x:", x, " x1:",x1, " y:",y)  # Debugging line
        return y

def create_arch_cut(chord, sagitta, thickness, depth, segments=64, for_cut=False):
    if sagitta < 2:
        raise ValueError("sagitta must be greater equal than 2.")
    else:    
        radius = (sagitta / 2.0) + (chord ** 2) / (8.0 * sagitta)
        angle_rad = 2.0 * math.asin(chord / (2.0 * radius))

        angle_step = angle_rad / segments
        verts = []

        offset = -thickness if for_cut else 0

        for i in range(segments + 1):
            angle = -angle_rad / 2 + i * angle_step
            x = radius * math.sin(angle)
            z = radius * math.cos(angle) + offset
            verts.append(Vector((x, depth/2, z)))

        for i in range(segments + 1):
            angle = angle_rad / 2 - i * angle_step
            inner_radius = radius - thickness
            x = inner_radius * math.sin(angle)
            z = inner_radius * math.cos(angle) + offset
            verts.append(Vector((x, depth/2, z)))

        mesh = bpy.data.meshes.new("ArchCutMesh" if for_cut else "ArchMesh")
        obj = bpy.data.objects.new("ArchCut" if for_cut else "Arch", mesh)
        bpy.context.collection.objects.link(obj)

        faces = [list(range(len(verts)))]
        mesh.from_pydata(verts, [], faces)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, depth, 0)})
        bpy.ops.object.editmode_toggle()

        return obj


def create_arched_window_type_1(
    width=30.0,
    height=40.0,
    arch_height=10.0,
    frame_width=1.0,
    frame_depth=2.0,
    num_horizontal_bars=2,
    num_vertical_bars=1,
    bar_width_x=0.5,
    bar_width_z=0.5
):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    if (arch_height < 2):
        arch_height = 0
        
    base_height = height - arch_height
        
    cutout_width = width - 2 * frame_width
    cutout_height = base_height + 2

    # Outer base frame
    bpy.ops.mesh.primitive_cube_add(size=2)
    base_outer = bpy.context.active_object
    base_outer.name = "Base_Outer"
    base_outer.scale = (width / 2, frame_depth / 2, base_height / 2)
    base_outer.location = (0, 0, base_height / 2)
    bpy.ops.object.transform_apply(scale=True)
    
    # Inner base cutout
    bpy.ops.mesh.primitive_cube_add(size=2)
    base_inner = bpy.context.active_object
    base_inner.name = "Base_Inner"
    base_inner.scale = (cutout_width / 2, frame_depth / 2 + 0.01, cutout_height / 2)
    base_inner.location = (0, 0, frame_width + cutout_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Boolean difference for base
    mod = base_outer.modifiers.new(name="CutBase", type='BOOLEAN')
    mod.object = base_inner
    mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = base_outer
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(base_inner)

    # Arch frame and cutout
    if arch_height >= 2: 
        arch_outer = create_arch_cut(width, arch_height, frame_width, frame_depth, for_cut=False)
        arch_radius = (arch_height / 2.0) + (width ** 2) / (8.0 * arch_height)
        arch_outer.location.z = base_height - arch_radius + arch_height
        arch_outer.location.y = -1
        """
        arch_inner = create_arch_cut(width - 2 * frame_width, arch_height - frame_width, frame_width, frame_depth + 0.01, for_cut=True)
        arch_inner.location.z = base_height + frame_width - arch_radius + arch_height
        arch_inner.location.y = -1

        # Boolean cut for arch
        mod2 = arch_outer.modifiers.new(name="CutArch", type='BOOLEAN')
        mod2.object = arch_inner
        mod2.operation = 'DIFFERENCE'
        bpy.context.view_layer.objects.active = arch_outer
        bpy.ops.object.modifier_apply(modifier=mod2.name)
        bpy.data.objects.remove(arch_inner)
        """
        # Join base and arch
        bpy.ops.object.select_all(action='DESELECT')
        base_outer.select_set(True)
        arch_outer.select_set(True)
        bpy.context.view_layer.objects.active = base_outer
        bpy.ops.object.join()
    else:
        bpy.ops.mesh.primitive_cube_add(size=1)
        frame_bar       = bpy.context.active_object
        frame_bar.name  = "Upper straight frame bar"
        frame_bar.scale = (width, frame_depth, frame_width)
        frame_bar.location = (0, 0, base_height)
        bpy.ops.object.transform_apply(scale=True)
        # Join base and upper straight frame bar
        bpy.ops.object.select_all(action='DESELECT')
        base_outer.select_set(True)
        frame_bar.select_set(True)
        bpy.context.view_layer.objects.active = base_outer
        bpy.ops.object.join()

    # Add sash bars to base
    sash_objects = []
    cutout_height = height - 2 * frame_width + bar_width_z
    
    for i in range(num_vertical_bars):
        x = -cutout_width / 2 - bar_width_x / 2 + (i + 1) * ((cutout_width + bar_width_x) / (num_vertical_bars + 1))
        bar_height = base_height + arch_height_at_x(cutout_width, arch_height , x+cutout_width/2)   
        bpy.ops.mesh.primitive_cube_add(size=2)
        bar = bpy.context.active_object
        bar.scale = (bar_width_x / 2, frame_depth / 2 + 0.01, bar_height / 2)
        bar.location = (x, 0, bar_height / 2)
        bpy.ops.object.transform_apply(scale=True)
        sash_objects.append(bar)
    
    for i in range(num_horizontal_bars):
        z = frame_width - bar_width_z / 2 + (i + 1) * ((cutout_height) / (num_horizontal_bars + 1))
        if z > base_height:
            x1, x2 = x_at_arch_height_y(cutout_width, arch_height, z-base_height) 
            bar_length = x2 - x1 
        else:
            bar_length = cutout_width
        bpy.ops.mesh.primitive_cube_add(size=2)
        bar = bpy.context.active_object
        bar.scale = (bar_length / 2, frame_depth / 2 + 0.01, bar_width_z / 2)
        bar.location = (0, 0, z)
        bpy.ops.object.transform_apply(scale=True)
        sash_objects.append(bar)
      
    # Join all sash bars with frame
    for obj in sash_objects:
        obj.select_set(True)
    base_outer.select_set(True)
    bpy.context.view_layer.objects.active = base_outer
    bpy.ops.object.join()

    return base_outer

def create_arched_window_type_2(
    width=30.0,
    height=40.0,
    arch_height=10.0,
    frame_width=1.0,
    frame_depth=2.0,
    num_horizontal_bars=2,
    num_vertical_bars=1,
    bar_width_x=0.5,
    bar_width_z=0.5,
    export_path=None
):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    if (arch_height > 2):
        base_height = height - arch_height
    else:
        base_height = height 
        arch_height = 0
        
    cutout_width = width - 2 * frame_width
    cutout_height = base_height - 2 * frame_width

    # Outer base frame
    bpy.ops.mesh.primitive_cube_add(size=2)
    base_outer = bpy.context.active_object
    base_outer.name = "Base_Outer"
    base_outer.scale = (width / 2, frame_depth / 2, base_height / 2)
    base_outer.location = (0, 0, base_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Inner base cutout
    bpy.ops.mesh.primitive_cube_add(size=2)
    base_inner = bpy.context.active_object
    base_inner.name = "Base_Inner"
    base_inner.scale = (cutout_width / 2, frame_depth / 2 + 0.01, cutout_height / 2)
    base_inner.location = (0, 0, frame_width + cutout_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Boolean difference for base
    mod = base_outer.modifiers.new(name="CutBase", type='BOOLEAN')
    mod.object = base_inner
    mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = base_outer
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(base_inner)

    # Arch frame and cutout
    if arch_height >= 2: 
        arch_outer = create_arch_cut(width, arch_height, frame_width, frame_depth, for_cut=False)
        arch_radius = (arch_height / 2.0) + (width ** 2) / (8.0 * arch_height)
        arch_outer.location.z = base_height - arch_radius + arch_height
        arch_outer.location.y = -1
        """
        arch_inner = create_arch_cut(width - 2 * frame_width, arch_height - frame_width, frame_width, frame_depth + 0.01, for_cut=True)
        arch_inner.location.z = base_height + frame_width - arch_radius + arch_height
        arch_inner.location.y = -1

        # Boolean cut for arch
        mod2 = arch_outer.modifiers.new(name="CutArch", type='BOOLEAN')
        mod2.object = arch_inner
        mod2.operation = 'DIFFERENCE'
        bpy.context.view_layer.objects.active = arch_outer
        bpy.ops.object.modifier_apply(modifier=mod2.name)
        bpy.data.objects.remove(arch_inner)
        """
        # Join base and arch
        bpy.ops.object.select_all(action='DESELECT')
        base_outer.select_set(True)
        arch_outer.select_set(True)
        bpy.context.view_layer.objects.active = base_outer
        bpy.ops.object.join()
    else:
        bpy.ops.mesh.primitive_cube_add(size=1)
        frame_bar       = bpy.context.active_object
        frame_bar.name  = "Upper straight frame bar"
        frame_bar.scale = (width, frame_depth, frame_width)
        frame_bar.location = (0, 0, base_height)
        bpy.ops.object.transform_apply(scale=True)
        # Join base and upper straight frame bar
        bpy.ops.object.select_all(action='DESELECT')
        base_outer.select_set(True)
        frame_bar.select_set(True)
        bpy.context.view_layer.objects.active = base_outer
        bpy.ops.object.join()

    frame = bpy.context.active_object

    # Add sash bars to base
    sash_objects = []
    
    for i in range(num_vertical_bars):
        x = -cutout_width / 2 - bar_width_x / 2 + (i + 1) * ((cutout_width + bar_width_x) / (num_vertical_bars + 1))
        bpy.ops.mesh.primitive_cube_add(size=2)
        bar = bpy.context.active_object
        bar.scale = (bar_width_x / 2, frame_depth / 2 + 0.01, cutout_height / 2)
        bar.location = (x, 0, frame_width + cutout_height / 2)
        bpy.ops.object.transform_apply(scale=True)
        sash_objects.append(bar)
    # horizontal_bar_distance is the distance between the center of two bars
    horizontal_bar_distance = (base_height - 2 * frame_width + bar_width_z) / (num_horizontal_bars + 1)    
    for i in range(num_horizontal_bars):
        z = frame_width - bar_width_z/2 + (i+1) * (horizontal_bar_distance)
        bpy.ops.mesh.primitive_cube_add(size=2)
        bar = bpy.context.active_object
        bar.scale = (cutout_width / 2, frame_depth / 2 + 0.01, bar_width_z / 2)
        bar.location = (0, 0, z)
        bpy.ops.object.transform_apply(scale=True)
        sash_objects.append(bar)
      
    # Add sash bars to arch
    if arch_height >= 2:
        for i in range(num_vertical_bars):
            x = -cutout_width / 2 - bar_width_x / 2 + (i + 1) * ((cutout_width + bar_width_x) / (num_vertical_bars + 1))
         # x = -cutout_width / 2 - bar_width_x / 2 + (i + 1) * ((cutout_width + bar_width_x) / (num_vertical_bars + 1))
            x_on_arch = x + cutout_width / 2
            y_on_arch = arch_height_at_x(cutout_width, arch_height , x+cutout_width/2)
        
            bpy.ops.mesh.primitive_cube_add(size=2)
            bar = bpy.context.active_object
            #bar.scale = (bar_width_x / 2, frame_depth / 2 + 0.01, bar_height / 2)
            #bar.location = (x, 0, frame_width + bar_height / 2)
            bar.scale = (bar_width_x / 2, frame_depth / 2 + 0.01, y_on_arch / 2)
            bar.location = (x, 0, (base_height + y_on_arch/2))
            bpy.ops.object.transform_apply(scale=True)
            sash_objects.append(bar)
        
        num_arch_horizontal_bars = math.floor((arch_height - frame_width) / (horizontal_bar_distance + bar_width_z)) 
    
        for i in range(num_arch_horizontal_bars + 1):
            z = -bar_width_z / 2 + (i+1) * (horizontal_bar_distance)
        
            x1, x2 = x_at_arch_height_y(cutout_width, arch_height, z) 
        
            bpy.ops.mesh.primitive_cube_add(size=2)
            bar = bpy.context.active_object
        
            bar.scale = ((x2-x1) / 2, frame_depth / 2 + 0.01, bar_width_z / 2)
            bar.location = (0, 0, base_height - bar_width_z/2 + z)
            bpy.ops.object.transform_apply(scale=True)
            sash_objects.append(bar)
    
    # Join all sash bars with frame
    for obj in sash_objects:
        obj.select_set(True)
    frame.select_set(True)
    bpy.context.view_layer.objects.active = frame
    bpy.ops.object.join()

    return frame


def create_and_save_arched_window(
    width=30.0,
    height=40.0,
    arch_height=10.0,
    frame_width=1.0,
    frame_depth=2.0,
    num_horizontal_bars=2,
    num_vertical_bars=1,
    bar_width_x=0.5,
    bar_width_z=0.5,
    windowsill = 'y',
    window_type = '1',
    save_path_name = './Users/thorstengerdsmeier/Documents/Modellbahn/python_scripts/'
):
    
    # Set the unit system to 'METRIC'
    bpy.context.scene.unit_settings.system = 'METRIC'
    # Set the unit scale so 1 Blender unit = 1 mm
    bpy.context.scene.unit_settings.scale_length = 0.001
    # Optional: set the unit display to millimeters
    bpy.context.scene.unit_settings.use_separate = True  # Use subunits like mm, cm, etc.

    sys.path.append('/Users/thorstengerdsmeier/Documents/Modellbahn/python_scripts')

    if window_type == '1':
        frame = create_arched_window_type_1(width,height,arch_height,
                                frame_width,frame_depth,
                                num_horizontal_bars,num_vertical_bars,
                                bar_width_x, bar_width_z)
    else:
        frame = create_arched_window_type_2(width,height,arch_height,
                                frame_width,frame_depth,
                                num_horizontal_bars,num_vertical_bars,
                                bar_width_x, bar_width_z)
        
    if windowsill == 'y':
        p1=(0, 0, 0)
        p2=(1, 0, 0)
        p3=(1, 0, 1)
              
        obj = create_wedge(p1,p2,p3,width,frame_width,frame_depth)

        frame.select_set(True)
        bpy.context.view_layer.objects.active = frame
        bpy.ops.object.join()
        
    # ensure object is selected and active
    frame.select_set(True)
    bpy.context.view_layer.objects.active = frame

    # rotate by +90° around X
    frame.rotation_euler[0] = math.radians(-90)

    # apply rotation (use operator on the active object)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
     
    # save file
    save_file_name = "Window" + "_W" + str(width) + "_H" + str(height) + "_AH" + str(arch_height) + "_hbars" + str(num_horizontal_bars) + "_vbars" + str(num_vertical_bars) + "_Type" + window_type
    save_file_name_blend = save_file_name.replace(".", "_") + '.blend'
    save_path = save_path_name + save_file_name_blend
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    
    save_file_name_stl = save_file_name.replace(".", "_") + '.stl'
    save_path = save_path_name + save_file_name_stl

    # export to stl
    bpy.ops.wm.stl_export(
        filepath=save_path,
        use_scene_unit=False,    # ignore scene scale
        global_scale=1.0
        )
    print(f"Exported to {save_path}")


# All Augustiner windows are defined in one place.  Values are in millimetres.
AUGUSTINER_WINDOW_SPECS: list[WindowSpec] = [
    WindowSpec(10, 15, 1.0, 1, 2, 0.5, arch_height_mm=2),
    WindowSpec(10, 20, 1.0, 1, 3, 0.5, arch_height_mm=2),
    WindowSpec(9, 35, 1.0, 1, 6, 0.5, arch_height_mm=2),
    WindowSpec(12, 35, 1.0, 1, 6, 0.5, arch_height_mm=2),
    WindowSpec(10, 5, 1.0, 1, 1, 0.5),
    WindowSpec(10, 15, 1.0, 1, 2, 0.5),
    WindowSpec(20, 20, 1.0, 2, 2, 0.5),
    WindowSpec(10, 20, 1.0, 1, 2, 0.5),
    WindowSpec(25, 10, 1.0, 4, 1, 0.5),
    WindowSpec(20, 10, 1.0, 4, 1, 0.5),
]


def generate_augustiner_windows(
    window_specs: list[WindowSpec],
    save_path_name: str = "/Users/thorstengerdsmeier/Documents/Modellbahn/python_scripts/generated_windows/Augustiner",
) -> None:
    """Create and export one Blender window for every supplied WindowSpec."""
    for index, spec in enumerate(window_specs):
        create_and_save_arched_window(
            width=spec.width_mm,
            height=spec.height_mm,
            arch_height=spec.arch_height_mm,
            frame_width=spec.frame_width_mm,
            frame_depth=1.0,
            num_horizontal_bars=spec.num_horizontal_bars,
            num_vertical_bars=spec.num_vertical_bars,
            bar_width_x=spec.sash_bar_width_mm,
            bar_width_z=spec.sash_bar_width_mm,
            # The first facade window was intentionally generated without a sill.
            windowsill="n" if index == 0 else "y",
            window_type="1",
            save_path_name=save_path_name,
        )


generate_augustiner_windows(AUGUSTINER_WINDOW_SPECS)
