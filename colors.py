import bpy
from mathutils import Euler
from math import radians

# === Szene leeren ===
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)
for block in bpy.data.lights:
    if block.users == 0:
        bpy.data.lights.remove(block)
for block in bpy.data.images:
    if block.users == 0:
        bpy.data.images.remove(block)


# === Schritt 1: Lade XYZ-Datei ===
xyz_path = "/Users/sarahbernart/calc/Kinetics/Cluster/Pt4_CeO2/Blender/M1.xyz"
bpy.ops.import_mesh.xyz(filepath=xyz_path)

# === Schritt 2: Viewport auf RENDERED & ORTHO ===
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'RENDERED'
                space.region_3d.view_perspective = 'ORTHO'
                space.region_3d.view_rotation = Euler((radians(40), radians(0), radians(40)), 'XYZ').to_quaternion()

# === Schritt 3: Mache Instanzen real ===
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.name.startswith(("Oxygen", "Palladium", "Platinum", "Cerium", "Carbon",)): #, "Carbon", "Platinum")):
        obj.select_set(True)
bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
bpy.ops.object.duplicates_make_real()

# === Schritt 4: Stelle sicher, dass genau eine SUN vorhanden ist ===
# === Stelle sicher, dass eine Sun-Lichtquelle existiert und konfiguriert ist ===
sun = None
for obj in bpy.data.objects:
    if obj.type == 'LIGHT' and obj.data.type == 'SUN':
        sun = obj
        break

if not sun:
    light_data = bpy.data.lights.new(name="Sun", type='SUN')
    sun = bpy.data.objects.new(name="Sun", object_data=light_data)
    bpy.context.collection.objects.link(sun)

# === Setze Position, Richtung, Intensität, Winkel ===
sun.location = (20, 0, 20)
sun.data.energy = 20
sun.data.angle = radians(55)

# === Setze Shadow-Parameter (sofern vorhanden) ===
sun.data.use_shadow = True

# Influence-Werte setzen (Achtung: custom Render-Engines ignorieren teils diese Werte)
sun.data.shadow_filter_radius = 20.0
#sun.data.use_shadow_jitter = True 
#sun.data.shadow_jitter_overblur = 10.0
sun.data.shadow_maximum_resolution = 10
sun.data.diffuse_factor = 2
sun.data.specular_factor = 1.5
sun.data.transmission_factor = 1.0
sun.data.volume_factor = 1.0



# === Schritt 5: Definiere Materialien ===

def update_existing_material(obj, color, metallic, roughness):
    if not obj.material_slots:
        return

    mat = obj.material_slots[0].material
    if not mat or not mat.use_nodes:
        return

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness

# === Cerium (hell, blattgelb) ===
for obj in bpy.data.objects:
    if obj.name.startswith("Cerium_ball"):
        update_existing_material(obj, (0.9, 0.7, 0.0, 1.0), 0.75, 0.75)

# === Oxygen === #FF0016FF
for obj in bpy.data.objects:
    if obj.name.startswith("Oxygen_ball"):
        update_existing_material(obj, (0.277, 0.0, 0.0, 1.0), 0.75, 0.5)

# === Palladium === #008498FF
for obj in bpy.data.objects:
    if obj.name.startswith("Palladium_ball"):
        update_existing_material(obj, (0.0, 0.518, 0.596, 1.0), 1.0, 0.5)

# === Platinum ===
for obj in bpy.data.objects:
    if obj.name.startswith("Platinum_ball"):
        update_existing_material(obj, (0.75, 0.75, 0.75, 1.0), 1.0, 0.5)

# === Carbon ===
for obj in bpy.data.objects:
    if obj.name.startswith("Carbon_ball"):
        update_existing_material(obj, (0.025, 0.025, 0.025, 1.0), 0.75, 0.5)