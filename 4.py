import bpy
from mathutils import Euler, Vector
from math import radians
import os, math, time

# ========================
# Konfiguration (2-Struktur-Test)
# ========================
TEST_NAMES   = ["M1"#]
,"1Vo","2O","2Vo","CO_1Vo","CO_O","CO_2O","CO","CO2_1Vo",
"CO2_2Vo","CO2_O","CO2","1Vo_sub","O","O2_1Vo","O2_2Vo","O2","OCOO_1Vo","OCOO",
"TS_CO_1Vo","TS_CO_O","TS_CO_2O","TS_CO","TS_O2_1Vo","TS_O2_2Vo","TS_O2",
"TS_OCOO_1Vo","TS_OCOO","1Vo_sub_nn","CO_1Vo_nn","CO2_2Vo_nn","2Vo_nn","O2_2Vo_nn",
"TS_CO_1Vo_nn","TS_O2_2Vo_nn"]
BASE_XYZ_DIR = "/Users/sarahbernart/calc/Kinetics/Cluster/Pd4_CeO2/Blender"
OUT_DIR      = os.path.expanduser('~/calc/Kinetics/Cluster/Pd4_CeO2/Blender/pics')
TARGET_SIZE  = 1500     # quadratisch (px)
AUTO_FIT     = False    # True -> passt ORTHO-Breite (ortho_scale) automatisch an

# ========================
# Szene leeren (ohne bpy.ops)
# ========================
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.images, bpy.data.cameras):
    for block in list(coll):
        if block.users == 0:
            coll.remove(block)

# ========================
# Viewport auf RENDERED & ORTHO (falls GUI)
# ========================
if bpy.context.screen:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'RENDERED'
                    space.region_3d.view_perspective = 'ORTHO'
                    space.region_3d.view_rotation = Euler((radians(40), 0.0, radians(40)), 'XYZ').to_quaternion()

# ========================
# Licht (Sun) – wie in deinem Script
# ========================
light_data = bpy.data.lights.new(name="Sun", type='SUN')
sun = bpy.data.objects.new(name="Sun", object_data=light_data)
bpy.context.collection.objects.link(sun)

sun.location = (9, -9, 10)
sun.data.energy = 10
sun.data.angle = radians(55)
sun.data.use_shadow = True
setattr(sun.data, "shadow_filter_radius", 20.0)
setattr(sun.data, "shadow_maximum_resolution", 10)
setattr(sun.data, "diffuse_factor", 5.0)
setattr(sun.data, "specular_factor", 1.5)
setattr(sun.data, "transmission_factor", 1.0)
setattr(sun.data, "volume_factor", 1.0)

# ========================
# Materialien (deine Zuweisungen)
# ========================
def update_existing_material(obj, color, metallic, roughness):
    if not obj.material_slots: return
    mat = obj.material_slots[0].material
    if not mat or not mat.use_nodes: return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value   = metallic
        bsdf.inputs["Roughness"].default_value  = roughness

def apply_element_materials():
    for obj in bpy.data.objects:
        n = obj.name
        if   n.startswith("Cerium_ball"):    update_existing_material(obj, (0.9, 0.7, 0.0, 1.0), 0.75, 0.75)
        elif n.startswith("Lanthanum_ball"): update_existing_material(obj, (0.0, 0.48515, 0.43415, 1.0), 0.75, 0.75)
        elif n.startswith("Oxygen_ball"):    update_existing_material(obj, (0.277, 0.0, 0.0, 1.0), 0.75, 0.5)
        elif n.startswith("Nitrogen_ball"):  update_existing_material(obj, (0.0, 0.005605, 0.318547, 1.0), 0.75, 0.75)
        elif n.startswith("Rhodium_ball"):   update_existing_material(obj, (0.0, 0.318547, 0.030713, 1.0), 1.0, 0.5)
        elif n.startswith("Palladium_ball"): update_existing_material(obj, (0.0, 0.518, 0.596, 1.0), 1.0, 0.5)
        elif n.startswith("Platinum_ball"):  update_existing_material(obj, (0.75, 0.75, 0.75, 1.0), 1.0, 0.5)
        elif n.startswith("Carbon_ball"):    update_existing_material(obj, (0.025, 0.025, 0.025, 1.0), 0.75, 0.5)

def make_black_cloud_mat(name="BlackCloud", density=1, albedo=0.04, anisotropy=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value            = (albedo, albedo, albedo, 1.0)
    pv.inputs["Density"].default_value          = density
    pv.inputs["Anisotropy"].default_value       = anisotropy
    pv.inputs["Absorption Color"].default_value = (0.01, 0.01, 0.01, 1.0)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(pv.outputs["Volume"], out.inputs["Volume"])
    return m

TARGET_PREFIXES = ("Boron_ball",)  # ggf. erweitern
cloud_mat = make_black_cloud_mat()

def apply_cloud_to_targets():
    for obj in bpy.data.objects:
        if any(obj.name.startswith(p) for p in TARGET_PREFIXES):
            obj.data.materials.clear()
            obj.data.materials.append(cloud_mat)

# ========================
# Backdrop (weiß, Emission)
# ========================
mesh = bpy.data.meshes.new("BackdropMesh")
mesh.from_pydata([(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)], [], [(0,1,2,3)])
mesh.update()
bg = bpy.data.objects.new("Backdrop", mesh)
bpy.context.collection.objects.link(bg)
bg.location = (0.0, 25.0, 0.0)
bg.rotation_euler = (radians(45.0), 0.0, 0.0)
bg.scale = (100.0, 100.0, 100.0)

mat = bpy.data.materials.new("Backdrop_White_Emit")
mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
emit = nt.nodes.new("ShaderNodeEmission")
emit.inputs["Color"].default_value    = (1.0, 1.0, 1.0, 1.0)
emit.inputs["Strength"].default_value = 12.0
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
bg.data.materials.clear()
bg.data.materials.append(mat)
if hasattr(bg, "cycles_visibility"): bg.cycles_visibility.shadow = False
if hasattr(mat, "shadow_method"):   mat.shadow_method = 'NONE'

# ========================
# Kamera (fix, ORTHO)
# ========================
CAMERA_Z      = 25.0    # Höhe über dem Slab
CAMERA_NAME   = "Camera"

cam_data = bpy.data.cameras.get(CAMERA_NAME) or bpy.data.cameras.new(CAMERA_NAME)
cam_obj  = bpy.data.objects.get(CAMERA_NAME)
if cam_obj is None:
    cam_obj = bpy.data.objects.new(CAMERA_NAME, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
else:
    cam_obj.data = cam_data

# Top-down: Kamera schaut entlang -Z (Blender-Kamera schaut lokal entlang -Z)
cam_obj.location       = Vector((-2.0, 1.0, CAMERA_Z))
cam_obj.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')

cam_data.type        = 'ORTHO'
cam_data.ortho_scale = 10     # nur Bildbreite; bei Bedarf NUR diesen Wert feinjustieren
cam_data.clip_start  = 1e-4
cam_data.clip_end    = 100000.0

bpy.context.scene.camera = cam_obj

def orthographic_autofit(cam, padding=1.12):
    from mathutils import Vector
    cam_inv = cam.matrix_world.inverted()
    xs, ys = [], []
    for obj in bpy.context.visible_objects:
        if obj.type in {'MESH','CURVE','SURFACE','META','FONT'} and obj.name != "Backdrop":
            for bb in obj.bound_box:
                w = obj.matrix_world @ Vector(bb)
                c = cam_inv @ w
                xs.append(c.x); ys.append(c.y)
    if xs and ys:
        width  = (max(xs) - min(xs)) * padding
        height = (max(ys) - min(ys)) * padding
        cam.data.ortho_scale = max(width, height)

# ========================
# Render-Setup (quadratisch + Qualität)
# ========================
os.makedirs(OUT_DIR, exist_ok=True)
r = bpy.context.scene.render
r.image_settings.file_format   = 'PNG'
r.image_settings.color_mode    = 'RGB'
r.use_file_extension           = True
r.resolution_x = TARGET_SIZE
r.resolution_y = TARGET_SIZE
r.resolution_percentage = 100
r.pixel_aspect_x = r.pixel_aspect_y = 1

if r.engine == 'CYCLES':
    c = bpy.context.scene.cycles
    c.use_adaptive_sampling = True
    c.adaptive_threshold    = 0.02
    c.samples               = max(getattr(c, "samples", 128), 512)
    if hasattr(c, "sampling_pattern"):   c.sampling_pattern = 'PROGRESSIVE_MULTI_JITTER'
    if hasattr(c, "pixel_filter_type"):
        c.pixel_filter_type = 'BLACKMAN_HARRIS'
        c.filter_width      = 1.5
    if bpy.context.scene.view_layers:
        bpy.context.scene.view_layers[0].cycles.use_denoising = True
elif r.engine == 'BLENDER_EEVEE':
    e = bpy.context.scene.eevee
    if hasattr(e, "taa_render_samples"): e.taa_render_samples = max(getattr(e, "taa_render_samples", 16), 128)
    if hasattr(e, "render_samples"):     e.render_samples     = max(getattr(e, "render_samples", 16), 128)
    e.use_volumetric_lights  = True
    e.use_volumetric_shadows = True
    e.volumetric_end = 100.0
    e.volumetric_tile_size = '2'

# ========================
# Helpers
# ========================
ELEMENT_PREFIXES = (
    "Oxygen_ball","Palladium_ball","Platinum_ball","Cerium_ball",
    "Carbon_ball","Nitrogen_ball","Hydrogen_ball","Lanthanum_ball",
    "Boron_ball","Rhodium_ball"
)

def imported_atom_objects():
    return [o for o in bpy.data.objects if any(o.name.startswith(p) for p in ELEMENT_PREFIXES)]

def clear_imported():
    for o in list(bpy.data.objects):
        if any(o.name.startswith(p) for p in ELEMENT_PREFIXES):
            bpy.data.objects.remove(o, do_unlink=True)

def make_instances_real_if_any():
    bpy.ops.object.select_all(action='DESELECT')
    objs = imported_atom_objects()
    for o in objs: o.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.duplicates_make_real()

# ========================
# Loop über zwei Strukturen
# ========================
for NAME in TEST_NAMES:
    xyz_path   = os.path.join(BASE_XYZ_DIR, f"{NAME}.xyz")
    out_no_ext = os.path.join(OUT_DIR, NAME)
    png_path   = out_no_ext + ".png"

    if not os.path.exists(xyz_path):
        print(f"[WARN] Übersprungen (XYZ fehlt): {xyz_path}")
        continue

    clear_imported()

    t0 = time.perf_counter()
    # Import (ohne Zentrierung!)
    try:
        bpy.ops.import_mesh.xyz(filepath=xyz_path, use_center=True, use_center_all=True)
    except Exception as e:
        print(f"[ERROR] Import fehlgeschlagen: {xyz_path} -> {e}")
        continue
    bpy.context.view_layer.update()
    t1 = time.perf_counter()
    print(f"[TIMING][{NAME}] Import: {t1 - t0:.2f} s")

    # Instanzen real
    make_instances_real_if_any()
    bpy.context.view_layer.update()
    t2 = time.perf_counter()
    print(f"[TIMING][{NAME}] Instanzen real: {t2 - t1:.2f} s")

    # Materialien
    apply_element_materials()
    apply_cloud_to_targets()
    bpy.context.view_layer.update()
    t3 = time.perf_counter()
    print(f"[TIMING][{NAME}] Materialien: {t3 - t2:.2f} s")

    # Optionaler ORTHO-Autofit
    if AUTO_FIT:
        orthographic_autofit(cam_obj, padding=1.12)
        print(f"[INFO][{NAME}] ORTHO auto-fit scale -> {cam_obj.data.ortho_scale:.3f}")

    # Render
    bpy.context.scene.render.filepath = out_no_ext
    if os.path.exists(png_path):
        try: os.remove(png_path)
        except Exception as e: print(f"[WARN] Konnte bestehende Datei nicht löschen: {e}")

    bpy.ops.render.render(write_still=True)
    t4 = time.perf_counter()
    print(f"[TIMING][{NAME}] Render: {t4 - t3:.2f} s")
    print(f"[OK] {png_path}")

print("[DONE] 2-Struktur-Test abgeschlossen.")

