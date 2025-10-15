import bpy
from mathutils import Euler, Vector
from math import radians

# === Szene leeren (ohne bpy.ops) ===
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.images, bpy.data.cameras):
    for block in list(coll):
        if block.users == 0:
            coll.remove(block)

# === Schritt 1: Lade XYZ-Datei ===
xyz_path = "/Users/sarahbernart/calc/Kinetics/Cluster/Pd10_CeO2/Blender/scattered2.xyz"
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
    if obj.name.startswith(("Oxygen", "Palladium", "Platinum", "Cerium", "Carbon", "Nitrogen", "Hydrogen", "Lanthanum", "Boron", "Rhodium")):
        obj.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.duplicates_make_real()

# === Schritt 4: Stelle sicher, dass genau eine SUN vorhanden ist ===
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

# === Schatten/Einfluss (falls vorhanden) ===
sun.data.use_shadow = True
setattr(sun.data, "shadow_filter_radius", 20.0)
setattr(sun.data, "shadow_maximum_resolution", 10)
setattr(sun.data, "diffuse_factor", 2.0)
setattr(sun.data, "specular_factor", 1.5)
setattr(sun.data, "transmission_factor", 1.0)
setattr(sun.data, "volume_factor", 1.0)

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

# === Lanthanum/Ce3+ (hellblau-türkis) ===  # #00B9B0FF linear
for obj in bpy.data.objects:
    if obj.name.startswith("Lanthanum_ball"):
        update_existing_material(obj, (0.0, 0.48515, 0.43415, 1.0), 0.75, 0.75)

# === Oxygen === #FF0016FF (linear angenähert)
for obj in bpy.data.objects:
    if obj.name.startswith("Oxygen_ball"):
        update_existing_material(obj, (0.277, 0.0, 0.0, 1.0), 0.75, 0.5)

# === Nitrogen === #001199FF linear
for obj in bpy.data.objects:
    if obj.name.startswith("Nitrogen_ball"):
        update_existing_material(obj, (0.0, 0.005605, 0.318547, 1.0), 0.75, 0.75)
        
# === Rhodium === #001199FF linear
for obj in bpy.data.objects:
    if obj.name.startswith("Rhodium_ball"):
        update_existing_material(obj, (0.0, 0.318547, 0.030713, 1.0), 1.0, 0.5)

# === Palladium === #008498FF (linear angenähert)
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


# === Make a ball "diffuse like black scattering" (volumetric cloud) ===
def make_black_cloud_mat(name="BlackCloud", density=0.12, albedo=0.05, anisotropy=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()

    # Principled Volume for soft scattering + absorption
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value            = (albedo, albedo, albedo, 1.0)   # scattering color (near-black)
    pv.inputs["Density"].default_value          = density                          # overall "cloudiness"
    pv.inputs["Anisotropy"].default_value       = anisotropy                        # 0 = isotropic
    pv.inputs["Absorption Color"].default_value = (0.01, 0.01, 0.01, 1.0)          # makes it darker

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(pv.outputs["Volume"], out.inputs["Volume"])
    return m

# Apply to chosen balls (change prefixes as needed)
TARGET_PREFIXES = ("Boron_ball",)  # e.g. ("Nitrogen_ball", "Boron_ball") etc.
cloud_mat = make_black_cloud_mat(density=1, albedo=0.04, anisotropy=0.0)

for obj in bpy.data.objects:
    if any(obj.name.startswith(p) for p in TARGET_PREFIXES):
        obj.data.materials.clear()
        obj.data.materials.append(cloud_mat)

# Renderer setup for volumes
scene = bpy.context.scene
if scene.render.engine == 'BLENDER_EEVEE':
    scene.eevee.use_volumetric_lights = True
    scene.eevee.use_volumetric_shadows = True
    scene.eevee.volumetric_end = 100.0
    scene.eevee.volumetric_tile_size = '2'  # higher quality
# Cycles renders volumes naturally; no special switches required.




# === BACKDROP: weiße Plane (Y=25, RotX=45°, Scale=100) mit heller Emission ===
import bpy
from math import radians

# 1) Mesh für Plane anlegen
mesh = bpy.data.meshes.new("BackdropMesh")
verts = [(-1, -1, 0), (1, -1, 0), (1,  1, 0), (-1,  1, 0)]
faces = [(0, 1, 2, 3)]
mesh.from_pydata(verts, [], faces)
mesh.update()

# 2) Objekt holen oder neu erstellen und linken
bg = bpy.data.objects.get("Backdrop")
if bg is None:
    bg = bpy.data.objects.new("Backdrop", mesh)
    bpy.context.collection.objects.link(bg)
else:
    # vorhandenes Objekt weiterverwenden, neues Mesh zuweisen
    bg.data = mesh

# 3) Transform setzen
bg.location = (0.0, 25.0, 0.0)                 # oder (-20.0) falls gewünscht
bg.rotation_euler = (radians(45.0), 0.0, 0.0)  # 45° um X
bg.scale = (100.0, 100.0, 100.0)               # ggf. 10000.0 wenn nötig

# 4) Emissions-Material in reinem Weiß
mat = bpy.data.materials.get("Backdrop_White_Emit") or bpy.data.materials.new("Backdrop_White_Emit")
mat.use_nodes = True
nt = mat.node_tree
# Nodes neu aufsetzen
for n in list(nt.nodes):
    nt.nodes.remove(n)
emit = nt.nodes.new("ShaderNodeEmission")
emit.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
emit.inputs["Strength"].default_value = 12.0    # Helligkeit, gern höher stellen (z.B. 20)
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

bg.data.materials.clear()
bg.data.materials.append(mat)

# 5) Schatten aus (optional)
if hasattr(bg, "cycles_visibility"):
    bg.cycles_visibility.shadow = False
if hasattr(mat, "shadow_method"):
    mat.shadow_method = 'NONE'

