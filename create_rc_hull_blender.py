"""Erzeugt einen druckbaren RC-Schiffsrumpf aus Spanten in Blender.

Benutzung
---------
1. Blender oeffnen -> Scripting -> New, dieses Skript laden und Run Script.
2. Unten SPANTEN und SPANT_ABSTAND_MM durch die Daten des Bauplans ersetzen.
3. In der Szene liegt danach eine Collection "RC_Hull_Segments". Bei
   EXPORT_STL=True wird fuer jedes Segment auch eine STL geschrieben.

Koordinatenkonvention
---------------------
* Ein Spant ist eine geschlossene Kontur als [(x, y), ...] in Millimetern.
* x: Backbord(-) nach Steuerbord(+); y: Kiel/unten(-) nach Deck/oben(+).
* Die Spanten werden vom Heck zum Bug entlang +Z angeordnet.
* Die Punkte eines Spants muessen den Rand einmal umlaufen, ohne sich selbst
  zu schneiden. Der erste Punkt darf, muss aber nicht, am Ende wiederholt sein.

Die Aussenhaut entsteht als durchgehendes Loft. Jeder Druckabschnitt bekommt
eine nach innen versetzte Wand und an beiden Stirnseiten geschlossene Ringe;
dadurch ist jedes einzelne STL wasserdicht/manifold und die Segmente koennen
stumpf miteinander verklebt werden. An den gemeinsamen Schnittflaechen gibt es
keine konstruktiv vorgesehenen Spalten.

Hinweis: Ein 0,4-mm-Drucker erreicht mit 1,2 mm Wand meist drei Perimeter.
Vor dem Druck Masseinheit und maximalen Bauraum im Slicer pruefen.
"""

import bpy
import math
import os


# ---------------------------------------------------------------------------
# Eingabe: Beispielrumpf. Alle Abmessungen sind Millimeter.
# Ersetze diese Liste durch die Spanten aus deinem Bauplan.
# ---------------------------------------------------------------------------
SPANT_ABSTAND_MM = 35.0
SPANTEN = [
    # x, y: geschlossene Kontur; hier ein einfaches, symmetrisches Beispiel
    [(-8, 0), (-7, 8), (-4, 15), (0, 18), (4, 15), (7, 8), (8, 0),
     (5, -7), (0, -10), (-5, -7)],
    [(-26, 0), (-24, 16), (-16, 31), (0, 37), (16, 31), (24, 16), (26, 0),
     (17, -15), (0, -22), (-17, -15)],
    [(-38, 0), (-35, 24), (-24, 43), (0, 50), (24, 43), (35, 24), (38, 0),
     (26, -24), (0, -34), (-26, -24)],
    [(-42, 0), (-39, 27), (-27, 48), (0, 55), (27, 48), (39, 27), (42, 0),
     (30, -29), (0, -40), (-30, -29)],
    [(-34, 0), (-31, 23), (-21, 41), (0, 48), (21, 41), (31, 23), (34, 0),
     (23, -25), (0, -35), (-23, -25)],
    [(-12, 0), (-11, 10), (-7, 20), (0, 25), (7, 20), (11, 10), (12, 0),
     (8, -10), (0, -16), (-8, -10)],
]

# Druck- und Konstruktionsparameter
MAX_SEGMENT_LAENGE_MM = 180.0  # fuer 200-mm-Druckbett mit Sicherheitsrand
WANDSTAERKE_MM = 1.2
KONTUR_PUNKTE = 96             # identische Punktzahl fuer sauberes Loft
EXPORT_STL = True
EXPORT_ORDNER = "//rc_hull_segments"  # relativ zur gespeicherten .blend-Datei

# Leere Liste = keine Versteifungen. Beispiele: [1, 3] erzeugt an diesen
# Spant-Indizes geschlossene, volle Querschotten in dem jeweiligen Segment.
VERSTEIFUNGS_SPANT_INDIZES = []
VERSTEIFUNGS_DICKE_MM = 1.6


def clean_profile(points):
    """Entfernt eine eventuelle doppelte Abschlusskoordinate und prueft Daten."""
    result = [(float(x), float(y)) for x, y in points]
    if len(result) > 1 and result[0] == result[-1]:
        result.pop()
    if len(result) < 3:
        raise ValueError("Jeder Spant braucht mindestens drei unterschiedliche Punkte.")
    return result


def resample_closed(points, count):
    """Verteilt count Punkte gleichmaessig entlang des geschlossenen Polygons."""
    points = clean_profile(points)
    edges = []
    total = 0.0
    for i, point in enumerate(points):
        nxt = points[(i + 1) % len(points)]
        length = math.dist(point, nxt)
        edges.append(length)
        total += length
    if total == 0:
        raise ValueError("Ein Spant hat keine Ausdehnung.")

    output = []
    edge = 0
    consumed = 0.0
    for n in range(count):
        wanted = total * n / count
        while edge < len(edges) - 1 and wanted > consumed + edges[edge]:
            consumed += edges[edge]
            edge += 1
        a = points[edge]
        b = points[(edge + 1) % len(points)]
        ratio = 0.0 if edges[edge] == 0 else (wanted - consumed) / edges[edge]
        output.append((a[0] + (b[0] - a[0]) * ratio,
                       a[1] + (b[1] - a[1]) * ratio))
    return output


def section_at(z, station_z, profiles):
    """Interpoliert eine Kontur auf einer beliebigen Laengsposition z."""
    if z <= station_z[0]:
        return profiles[0]
    if z >= station_z[-1]:
        return profiles[-1]
    for i in range(len(station_z) - 1):
        if station_z[i] <= z <= station_z[i + 1]:
            t = (z - station_z[i]) / (station_z[i + 1] - station_z[i])
            return [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                    for a, b in zip(profiles[i], profiles[i + 1])]
    raise RuntimeError("Keine Spantposition gefunden.")


def make_outer_surface(name, z_values, station_z, profiles, collection):
    """Erzeugt nur die aeussere Mantelflaeche; Solidify schliesst die Enden."""
    rings = [section_at(z, station_z, profiles) for z in z_values]
    n = len(rings[0])
    vertices = [(x, y, z) for z, ring in zip(z_values, rings) for x, y in ring]
    faces = []
    for ring in range(len(rings) - 1):
        first = ring * n
        second = (ring + 1) * n
        for p in range(n):
            q = (p + 1) % n
            faces.append((first + p, first + q, second + q, second + p))

    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)

    # Negative offset behaelt die eingegebene Spantkontur als Aussenmass.
    solidify = obj.modifiers.new("Wasserdichte Wand", "SOLIDIFY")
    solidify.thickness = WANDSTAERKE_MM
    solidify.offset = -1.0
    solidify.use_even_offset = True
    solidify.use_quality_normals = True
    solidify.use_rim = True  # verschliesst Bug- und Heckseite des Segments

    # Modifier anwenden: Die exportierte STL ist ein echtes, geschlossenes Mesh.
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=solidify.name)
    bpy.ops.object.shade_smooth_by_angle()
    obj.select_set(False)
    return obj


def make_bulkhead(name, z, profile, collection):
    """Optionales volles, geschlossenes Querschott im Rumpfinneren."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    vertices = [(x, y, z) for x, y in profile]
    mesh.from_pydata(vertices, [], [tuple(range(len(vertices)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mod = obj.modifiers.new("Geschlossenes Schott", "SOLIDIFY")
    mod.thickness = VERSTEIFUNGS_DICKE_MM
    mod.offset = 0.0
    mod.use_rim = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)
    return obj


def export_stl(obj, filepath):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # Blender 4.x bzw. aeltere Blender-Versionen unterstuetzen beide Wege.
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=filepath, export_selected_objects=True)
    else:
        bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True)


def main():
    if len(SPANTEN) < 2:
        raise ValueError("Mindestens zwei Spanten sind erforderlich.")
    if WANDSTAERKE_MM <= 0 or MAX_SEGMENT_LAENGE_MM <= 0:
        raise ValueError("Wandstaerke und Segmentlaenge muessen groesser als null sein.")

    # Millimeter als Blender-Einheiten, damit STL und Slicer die Werte direkt nutzen.
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001

    old = bpy.data.collections.get("RC_Hull_Segments")
    if old:
        for obj in list(old.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old)
    collection = bpy.data.collections.new("RC_Hull_Segments")
    scene.collection.children.link(collection)

    profiles = [resample_closed(frame, KONTUR_PUNKTE) for frame in SPANTEN]
    station_z = [i * SPANT_ABSTAND_MM for i in range(len(profiles))]
    hull_length = station_z[-1]

    # Schnitte liegen exakt zusammen. An einer Schnittposition wird dieselbe
    # interpolierte Kontur fuer beide Nachbarsegmente verwendet.
    boundaries = [0.0]
    z = MAX_SEGMENT_LAENGE_MM
    while z < hull_length - 0.0001:
        boundaries.append(z)
        z += MAX_SEGMENT_LAENGE_MM
    boundaries.append(hull_length)

    segment_objects = []
    for index, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:]), 1):
        z_values = [start] + [s for s in station_z if start < s < end] + [end]
        obj = make_outer_surface(f"Rumpfsegment_{index:02d}", z_values,
                                 station_z, profiles, collection)
        segment_objects.append(obj)

    # Versteifungen werden den Segmenten als separate, geschlossene Koerper
    # hinzugefuegt. Beim Slicen mit 'ueberlappende Volumen vereinigen' werden
    # sie mit der Wand verschmolzen; sie durchbrechen die Aussenhaut nicht.
    for i in VERSTEIFUNGS_SPANT_INDIZES:
        if not 0 <= i < len(profiles):
            raise ValueError(f"Ungueltiger Versteifungs-Spantindex: {i}")
        make_bulkhead(f"Versteifung_{i:02d}", station_z[i], profiles[i], collection)

    if EXPORT_STL:
        folder = bpy.path.abspath(EXPORT_ORDNER)
        os.makedirs(folder, exist_ok=True)
        for obj in segment_objects:
            export_stl(obj, os.path.join(folder, obj.name + ".stl"))
        print("STL-Export abgeschlossen:", folder)

    print(f"Fertig: {len(segment_objects)} wasserdichte Rumpfsegmente, "
          f"Laenge {hull_length:.1f} mm.")


main()
