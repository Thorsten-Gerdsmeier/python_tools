"""Erzeugt einen geschlossenen, rechteckigen 3D-Rahmen in Blender.

Ausfuehren: Blender > Scripting > dieses Skript laden > Run Script.
Alle Masse sind Millimeter. Laenge verlaeuft entlang X, Breite entlang Y,
die Materialhoehe (Dicke) entlang Z.

ECKEN_GRAD ist der Mittelpunktswinkel jedes Kreissegments. Bei 90 Grad
entsteht die klassische, tangentiale Viertelkreis-Rundung. Andere Werte
erzeugen ebenfalls ein echtes Kreissegment, das die jeweilige Ecke ersetzt.
"""

import bpy
import math


# --------------------------- Parameter ------------------------------------
LAENGE_MM = 160.0             # Aussenmass X
BREITE_MM = 100.0             # Aussenmass Y
DICKE_MM = 5.0                # Materialhoehe Z
RAHMENSTEG_BREITE_MM = 10.0   # Breite des umlaufenden Rahmens im Grundriss

ECKEN_ABRUNDEN = True
ECKEN_RADIUS_MM = 18.0        # Radius des Kreissegments an der Aussenecke
ECKEN_GRAD = 90.0             # 0...unter 180 Grad, 90 = Viertelkreis
KREIS_SEGMENT_PUNKTE = 12     # mehr Punkte = glattere Rundung
KONTUR_PUNKTE = 160           # gleiche Punktzahl fuer Innen-/Aussenkontur

OBJEKT_NAME = "Rechteckrahmen"


def resample_closed(points, count):
    """Gibt count aequidistante Punkte einer geschlossenen Polygonlinie zurueck."""
    lengths = []
    total = 0.0
    for i, point in enumerate(points):
        nxt = points[(i + 1) % len(points)]
        distance = math.dist(point, nxt)
        lengths.append(distance)
        total += distance
    result, edge, travelled = [], 0, 0.0
    for i in range(count):
        target = total * i / count
        while edge < len(points) - 1 and target > travelled + lengths[edge]:
            travelled += lengths[edge]
            edge += 1
        a, b = points[edge], points[(edge + 1) % len(points)]
        ratio = 0.0 if lengths[edge] == 0 else (target - travelled) / lengths[edge]
        result.append((a[0] + (b[0] - a[0]) * ratio,
                       a[1] + (b[1] - a[1]) * ratio))
    return result


def rounded_rectangle(length, width, radius, angle_degrees, arc_points):
    """CCW-Kontur; die Ecken sind Kreisbogen mit Radius und Mittelpunktswinkel."""
    half_x, half_y = length / 2, width / 2
    if radius <= 0 or angle_degrees <= 0:
        return [(-half_x, -half_y), (half_x, -half_y),
                (half_x, half_y), (-half_x, half_y)]
    if not 0 < angle_degrees < 180:
        raise ValueError("ECKEN_GRAD muss groesser 0 und kleiner 180 sein.")

    theta = math.radians(angle_degrees)
    # Abstand der Bogenenden von der geometrischen Rechteckecke.
    cutback = math.sqrt(2) * radius * math.sin(theta / 2)
    if 2 * cutback >= min(length, width):
        raise ValueError("Radius/Grad sind fuer diese Laenge oder Breite zu gross.")

    # Kreismittelpunkt liegt auf der Winkelhalbierenden im Rechteckinneren.
    center_offset = (cutback / 2 + radius * math.cos(theta / 2) / math.sqrt(2))
    corners = [
        ((half_x, -half_y), (-center_offset, center_offset), (-cutback, 0), (0, cutback)),
        ((half_x, half_y), (-center_offset, -center_offset), (0, -cutback), (-cutback, 0)),
        ((-half_x, half_y), (center_offset, -center_offset), (cutback, 0), (0, -cutback)),
        ((-half_x, -half_y), (center_offset, center_offset), (0, cutback), (cutback, 0)),
    ]
    contour = []
    # Die vier Boegen schliessen sich ueber die geraden Seiten an; Startpunkt
    # eines Bogens wird nicht erneut geschrieben, damit keine Doppelpunkte entstehen.
    for corner, offset, start_offset, _end_offset in corners:
        cx, cy = corner[0] + offset[0], corner[1] + offset[1]
        sx, sy = corner[0] + start_offset[0], corner[1] + start_offset[1]
        start_angle = math.atan2(sy - cy, sx - cx)
        for i in range(arc_points):
            a = start_angle + theta * i / (arc_points - 1)
            point = (cx + radius * math.cos(a), cy + radius * math.sin(a))
            if contour and i == 0:
                continue
            contour.append(point)
    return contour


def create_frame(name, length, width, height, rail_width, rounded, radius, degrees):
    if min(length, width, height, rail_width) <= 0:
        raise ValueError("Laenge, Breite, Dicke und Rahmensteg-Breite muessen positiv sein.")
    if 2 * rail_width >= min(length, width):
        raise ValueError("Der Rahmensteg ist fuer die Aussenmasse zu breit.")

    outer_radius = radius if rounded else 0.0
    # Eine Innenrundung mit negativem Radius ist geometrisch nicht moeglich;
    # dann wird die Innenkante rechtwinklig. Das ergibt einen druckbaren Rahmen.
    inner_radius = max(0.0, outer_radius - rail_width)
    outer = rounded_rectangle(length, width, outer_radius, degrees, KREIS_SEGMENT_PUNKTE)
    inner = rounded_rectangle(length - 2 * rail_width, width - 2 * rail_width,
                              inner_radius, degrees, KREIS_SEGMENT_PUNKTE)
    outer = resample_closed(outer, KONTUR_PUNKTE)
    inner = resample_closed(inner, KONTUR_PUNKTE)
    n = KONTUR_PUNKTE

    # Vier Ringe: Aussen unten/oben, Innen unten/oben. Daraus entsteht ein
    # wasser- bzw. luftdichter Volumenkoerper ohne offene Flaechen.
    vertices = ([(x, y, 0) for x, y in outer] + [(x, y, 0) for x, y in inner] +
                [(x, y, height) for x, y in outer] + [(x, y, height) for x, y in inner])
    bottom_outer, bottom_inner, top_outer, top_inner = 0, n, 2 * n, 3 * n
    faces = []
    for i in range(n):
        j = (i + 1) % n
        # Oberseite, Unterseite, Aussenwand und Innenwand
        faces.append((top_outer + i, top_outer + j, top_inner + j, top_inner + i))
        faces.append((bottom_outer + j, bottom_outer + i, bottom_inner + i, bottom_inner + j))
        faces.append((bottom_outer + i, bottom_outer + j, top_outer + j, top_outer + i))
        faces.append((bottom_inner + j, bottom_inner + i, top_inner + i, top_inner + j))

    existing = bpy.data.objects.get(name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Recalculate sorgt auch bei ungewoehnlichen Kreissegmentwinkeln fuer nach aussen
    # gerichtete Normalen.
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    return obj


def main():
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
    bpy.context.scene.unit_settings.scale_length = 0.001
    frame = create_frame(OBJEKT_NAME, LAENGE_MM, BREITE_MM, DICKE_MM,
                         RAHMENSTEG_BREITE_MM, ECKEN_ABRUNDEN,
                         ECKEN_RADIUS_MM, ECKEN_GRAD)
    print(f"{frame.name}: {LAENGE_MM} x {BREITE_MM} x {DICKE_MM} mm erstellt.")


main()
