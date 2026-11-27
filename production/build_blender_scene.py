"""
MASTER 3D BLENDER 4.2 SCENE BUILDER — "3 Kota Paling Unik di Dunia"
Builds production/three_unique_cities.blend with:
  - 7 Distinct Real-World-Referenced Mid-Poly Cel-Shaded 3D Shoot Zones:
      1. Begich Towers Exterior Plaza, 14-Story 1957 Facade & Chugach Mountains (Whittier, AK)
      2. Begich Towers Ground-Floor Lobby, Post Office, PO Boxes, Elevator & Kozy Korner
      3. Whittier Underground Yellow-Blue Arched School Tunnel & Concrete Stairs
      4. Coober Pedy Scorching Red Outback Desert, Mullock Heaps, 24 White Vent Pipes & Danger Sign
      5. Coober Pedy Carved Sandstone Dugout Living Room, Leather Sofa, Recessed Bookshelf & Opal Vein
      6. Setenil de las Bodegas — Calle Cuevas del Sol, Colossal Overhanging Cliff & Bar La Roca Terrace
      7. Setenil 2nd-Floor Wrought-Iron Balconies, Blooming Geraniums, Laundry & Golden Hour God Rays
  - All 4 Selective Dynamic Reveal Animations (Architectural, Assembly, Procedural Wave, Pop-up)
    with non-linear ease-out overshoot curves & strict Hard Lock after completion!
  - Living Busy Set Dressing: Moving Vehicles (Whittier winter trucks + Coober Pedy Outback pickup),
    Isolated Exterior Snowstorm, Steam Puffs, Fluttering Laundry, Swaying Geraniums, Gliding Birds!
  - 30+ Continuous Wide-Angle Camera Movements + 11 Ground-Locked 2.5D Hybrid Character Cards!

Run:
  blender --background --python production/build_blender_scene.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from typing import List, Tuple

import bmesh
import bpy
from mathutils import Euler, Vector

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROD_DIR = PROJECT_ROOT / "production"
BLEND_OUT = PROD_DIR / "three_unique_cities.blend"
SPRITES_ROOT = PROD_DIR / "char_sprites"

sys.path.insert(0, str(PROD_DIR))

from blender_materials import (
    get_sign_texture_paths,
    make_cel_material,
    make_character_card_material,
    make_glass_material,
    make_opal_iridescent_material,
    make_sign_material,
    make_volumetric_beam_material,
)
from timeline_data import (
    DYNAMIC_REVEALS,
    FPS,
    TOTAL_FRAMES,
    ease_out_back,
    ease_out_expo,
    get_camera_state,
)

# ============================================================================
# GEOMETRY & ANIMATION HELPERS (Beveled Mid-Poly, Never Raw Primitive Boxes!)
# ============================================================================
def clear_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def ensure_collection(name: str, parent=None) -> bpy.types.Collection:
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def link_obj(obj: bpy.types.Object, col: bpy.types.Collection) -> bpy.types.Object:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def make_bevel_box(
    name: str,
    size: Tuple[float, float, float],
    loc: Tuple[float, float, float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    rot: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.03,
    pivot_bottom: bool = True,
) -> bpy.types.Object:
    """Create a crisp beveled mid-poly box; when pivot_bottom=True, origin Z=0 sits strictly at base."""
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z = (v.co.z + 0.5) * sz if pivot_bottom else v.co.z * sz
    if bevel > 0.0 and min(sx, sy, sz) > bevel * 3.0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2, affect="EDGES", clamp_overlap=True)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = False
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return link_obj(obj, col)


def make_cylinder(
    name: str,
    radius: float,
    height: float,
    loc: Tuple[float, float, float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    segs: int = 16,
    rot: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    r_top: float | None = None,
    pivot_bottom: bool = True,
) -> bpy.types.Object:
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segs,
        radius1=radius,
        radius2=radius if r_top is None else r_top,
        depth=height,
    )
    if pivot_bottom:
        for v in bm.verts:
            v.co.z += height * 0.5
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return link_obj(obj, col)


def make_sculpted_rock(
    name: str,
    scale_xyz: Tuple[float, float, float],
    loc: Tuple[float, float, float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    seed: int = 1,
    subdiv: int = 3,
    rough: float = 0.22,
    stratify: float = 0.0,
    smooth: bool = False,
) -> bpy.types.Object:
    """Create mid-poly sculpted organic rock/mountain/cliff mass with sedimentary strata."""
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    px = rng.uniform(0, 10)
    py = rng.uniform(0, 10)
    pz = rng.uniform(0, 10)
    for v in bm.verts:
        nx, ny, nz = v.co.x, v.co.y, v.co.z
        n1 = math.sin(nx * 3.1 + px) * math.cos(ny * 2.7 + py) * math.sin(nz * 3.5 + pz)
        n2 = math.sin(nx * 6.4 - py) * math.sin(ny * 5.9 + pz) * 0.45
        strata = math.sin(nz * 14.0) * stratify
        disp = 1.0 + (n1 + n2) * rough + strata
        v.co.x = nx * scale_xyz[0] * disp
        v.co.y = ny * scale_xyz[1] * disp
        v.co.z = nz * scale_xyz[2] * disp
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = smooth
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.data.materials.append(mat)
    return link_obj(obj, col)


def make_sign_plane(
    name: str,
    width: float,
    height: float,
    loc: Tuple[float, float, float],
    yaw_deg: float,
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    frame_mat: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """Create a VERTICAL upright UV-mapped crisp sign board facing -Y (rotated cleanly by yaw_deg around Z!)."""
    bm = bmesh.new()
    v0 = bm.verts.new((-width * 0.5, 0.0, -height * 0.5))
    v1 = bm.verts.new((width * 0.5, 0.0, -height * 0.5))
    v2 = bm.verts.new((width * 0.5, 0.0, height * 0.5))
    v3 = bm.verts.new((-width * 0.5, 0.0, height * 0.5))
    f = bm.faces.new((v0, v1, v2, v3))
    uv_layer = bm.loops.layers.uv.new("UVMap")
    uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for loop, uv in zip(f.loops, uvs):
        loop[uv_layer].uv = uv
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = (0.0, 0.0, math.radians(yaw_deg))
    obj.data.materials.append(mat)
    link_obj(obj, col)

    if frame_mat:
        back = make_bevel_box(
            f"{name}_Frame",
            (width + 0.10, 0.06, height + 0.10),
            (0.0, 0.04, 0.0),
            col,
            frame_mat,
            bevel=0.015,
            pivot_bottom=False,
        )
        back.parent = obj
    return obj


# ============================================================================
# DYNAMIC REVEAL KEYFRAME HELPERS (Non-Linear Ease-Out Overshoot + Hard Lock!)
# ============================================================================
def _set_bezier_ease(obj: bpy.types.Object) -> None:
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"


def animate_popup_z(obj: bpy.types.Object, start_f: int, dur: int = 20, drop_z: float = 0.0) -> None:
    """1) 3D Diorama Pop-up: Scale Z 0 -> 1.08 overshoot -> 1.0 Hard Lock (pivot at ground!)."""
    orig_z = obj.location.z
    orig_sc = tuple(obj.scale)
    f_over = start_f + int(dur * 0.72)
    f_end = start_f + dur

    obj.scale = (orig_sc[0] * 0.01, orig_sc[1] * 0.01, 0.001)
    obj.location.z = orig_z - drop_z
    obj.keyframe_insert("scale", frame=max(0, start_f - 1))
    obj.keyframe_insert("location", frame=max(0, start_f - 1))

    obj.scale = (orig_sc[0] * 1.04, orig_sc[1] * 1.04, orig_sc[2] * 1.09)
    obj.location.z = orig_z + 0.04
    obj.keyframe_insert("scale", frame=f_over)
    obj.keyframe_insert("location", frame=f_over)

    # Hard Lock at exact final resting transform!
    obj.scale = orig_sc
    obj.location.z = orig_z
    obj.keyframe_insert("scale", frame=f_end)
    obj.keyframe_insert("location", frame=f_end)
    _set_bezier_ease(obj)


def animate_assembly_drop(obj: bpy.types.Object, start_f: int, dur: int = 22, offset_vec=(0.0, 0.0, 1.6)) -> None:
    """2) Build-up / Assembly: Component flies in smoothly and snappy-locks into place!"""
    orig_loc = Vector(obj.location)
    orig_sc = tuple(obj.scale)
    f_mid = start_f + int(dur * 0.78)
    f_end = start_f + dur

    obj.location = orig_loc + Vector(offset_vec)
    obj.scale = (0.01, 0.01, 0.01)
    obj.keyframe_insert("location", frame=max(0, start_f - 1))
    obj.keyframe_insert("scale", frame=max(0, start_f - 1))

    obj.location = orig_loc - Vector(offset_vec) * 0.04
    obj.scale = (orig_sc[0] * 1.05, orig_sc[1] * 1.05, orig_sc[2] * 1.05)
    obj.keyframe_insert("location", frame=f_mid)
    obj.keyframe_insert("scale", frame=f_mid)

    obj.location = orig_loc
    obj.scale = orig_sc
    obj.keyframe_insert("location", frame=f_end)
    obj.keyframe_insert("scale", frame=f_end)
    _set_bezier_ease(obj)


def build_vehicle(
    name: str,
    loc: Tuple[float, float, float],
    rot_z_deg: float,
    col: bpy.types.Collection,
    body_mat: bpy.types.Material,
    glass_mat: bpy.types.Material,
    dark_mat: bpy.types.Material,
    light_mat: bpy.types.Material,
    snow_cap_mat: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """Build a crisp mid-poly 4x4 SUV / Outback Pickup Truck with wheels, cab, bed & glowing headlights!"""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0.0, 0.0, math.radians(rot_z_deg))
    link_obj(root, col)

    # Lower chassis body
    chassis = make_bevel_box(f"{name}_Body", (4.4, 1.9, 0.85), (0.0, 0.0, 0.42), col, body_mat, bevel=0.08)
    chassis.parent = root
    # Cabin upper greenhouse
    cab = make_bevel_box(f"{name}_Cab", (2.1, 1.72, 0.78), (-0.35, 0.0, 1.22), col, body_mat, bevel=0.07)
    cab.parent = root
    wind = make_bevel_box(f"{name}_Glass", (2.16, 1.56, 0.52), (-0.35, 0.0, 1.32), col, glass_mat, bevel=0.03)
    wind.parent = root
    # 4 Wheels grounded strictly at Z=0!
    for wx in (-1.35, 1.35):
        for wy in (-0.92, 0.92):
            wh = make_cylinder(
                f"{name}_Wh_{wx:.1f}_{wy:.1f}", 0.42, 0.30, (wx, wy, 0.42), col, dark_mat,
                segs=14, rot=(math.pi * 0.5, 0.0, 0.0), pivot_bottom=False,
            )
            wh.parent = root
    # Headlights
    for hy in (-0.62, 0.62):
        hl = make_bevel_box(f"{name}_HL_{hy:.1f}", (0.12, 0.32, 0.20), (2.20, hy, 0.86), col, light_mat, bevel=0.02)
        hl.parent = root
    # Optional snow layer on roof/hood for Whittier Alaska!
    if snow_cap_mat:
        sn = make_bevel_box(f"{name}_SnowCap", (2.15, 1.75, 0.16), (-0.35, 0.0, 1.98), col, snow_cap_mat, bevel=0.05)
        sn.parent = root
        sn2 = make_bevel_box(f"{name}_SnowHood", (1.35, 1.85, 0.14), (1.35, 0.0, 1.24), col, snow_cap_mat, bevel=0.04)
        sn2.parent = root
    return root


# ============================================================================
# MATERIAL PALETTE BUILDER
# ============================================================================
def create_materials() -> dict[str, bpy.types.Material]:
    signs = get_sign_texture_paths()
    m: dict[str, bpy.types.Material] = {}

    # --- Zone 1 & 2 & 3: Whittier, Alaska ---
    m["snow"]           = make_cel_material("Mat_Snow", (0.93, 0.96, 1.0), (0.48, 0.62, 0.82), roughness=0.55, tex_scale=12.0, tex_contrast=0.08, bump_strength=0.12)
    m["ice_mountain"]   = make_cel_material("Mat_IceMtn", (0.34, 0.44, 0.58), (0.14, 0.22, 0.38), roughness=0.82, tex_scale=4.0, tex_contrast=0.22, bump_strength=0.25)
    m["begich_concrete"]= make_cel_material("Mat_BegichConcrete", (0.58, 0.66, 0.74), (0.24, 0.34, 0.48), roughness=0.84, tex_scale=9.0, tex_contrast=0.18, bump_strength=0.18)
    m["begich_trim"]    = make_cel_material("Mat_BegichTrim", (0.32, 0.42, 0.54), (0.14, 0.20, 0.32), roughness=0.72, tex_scale=6.0)
    m["apt_lit"]        = make_cel_material("Mat_AptWindowLit", (0.98, 0.86, 0.58), (0.85, 0.70, 0.42), emission_rgb=(1.0, 0.84, 0.48), emission_strength=0.85)
    m["apt_dark"]       = make_cel_material("Mat_AptWindowDark", (0.18, 0.26, 0.38), (0.08, 0.12, 0.22), roughness=0.18, metallic=0.25)
    m["linoleum"]       = make_cel_material("Mat_Linoleum", (0.84, 0.78, 0.66), (0.45, 0.40, 0.36), roughness=0.32, tex_type="speckle_linoleum", tex_scale=36.0, tex_contrast=0.12, bump_strength=0.04)
    m["lobby_wall"]     = make_cel_material("Mat_LobbyWall", (0.90, 0.85, 0.74), (0.52, 0.46, 0.42), roughness=0.75, tex_scale=10.0, tex_contrast=0.08)
    m["wood_warm"]      = make_cel_material("Mat_WoodWarm", (0.52, 0.32, 0.18), (0.22, 0.13, 0.09), roughness=0.58, tex_type="wave_sandstone", tex_scale=14.0, tex_contrast=0.18, bump_strength=0.14)
    m["steel_brushed"]  = make_cel_material("Mat_SteelBrushed", (0.64, 0.68, 0.74), (0.26, 0.32, 0.42), roughness=0.35, metallic=0.85, tex_scale=24.0, tex_contrast=0.10)
    m["brass"]          = make_cel_material("Mat_Brass", (0.82, 0.64, 0.26), (0.42, 0.30, 0.12), roughness=0.28, metallic=0.85, tex_scale=12.0)
    m["tunnel_yellow"]  = make_cel_material("Mat_TunnelYellow", (0.90, 0.74, 0.22), (0.48, 0.38, 0.14), roughness=0.72, tex_scale=10.0, tex_contrast=0.14, bump_strength=0.15)
    m["tunnel_blue"]    = make_cel_material("Mat_TunnelBlue", (0.22, 0.46, 0.78), (0.10, 0.22, 0.44), roughness=0.72, tex_scale=10.0, tex_contrast=0.14)
    m["tunnel_concrete"]= make_cel_material("Mat_TunnelConcrete", (0.64, 0.68, 0.72), (0.26, 0.32, 0.42), roughness=0.88, tex_scale=12.0, tex_contrast=0.18, bump_strength=0.22)
    m["pipe_red"]       = make_cel_material("Mat_PipeRed", (0.78, 0.22, 0.18), (0.38, 0.10, 0.12), roughness=0.45, metallic=0.35)
    m["neon_glow"]      = make_cel_material("Mat_NeonGlow", (0.98, 0.96, 0.88), (0.95, 0.92, 0.82), emission_rgb=(1.0, 0.95, 0.84), emission_strength=1.4)
    m["truck_red"]      = make_cel_material("Mat_TruckRed", (0.76, 0.22, 0.18), (0.34, 0.12, 0.16), roughness=0.35, metallic=0.35)
    m["truck_blue"]     = make_cel_material("Mat_TruckBlue", (0.20, 0.38, 0.62), (0.10, 0.18, 0.36), roughness=0.35, metallic=0.35)
    m["tire_dark"]      = make_cel_material("Mat_TireDark", (0.12, 0.12, 0.15), (0.06, 0.06, 0.10), roughness=0.88)

    # --- Zone 4 & 5: Coober Pedy, Australia ---
    m["red_desert"]     = make_cel_material("Mat_RedDesert", (0.78, 0.34, 0.16), (0.40, 0.16, 0.14), (0.98, 0.68, 0.44), roughness=0.92, tex_scale=6.0, tex_contrast=0.22, bump_strength=0.25)
    m["mullock_white"]  = make_cel_material("Mat_MullockWhite", (0.88, 0.80, 0.68), (0.52, 0.42, 0.38), roughness=0.90, tex_scale=14.0, tex_contrast=0.18, bump_strength=0.24)
    m["pvc_white"]      = make_cel_material("Mat_PVCWhite", (0.95, 0.94, 0.91), (0.56, 0.58, 0.66), roughness=0.42, tex_scale=10.0, tex_contrast=0.06)
    m["sandstone_carved"]= make_cel_material("Mat_SandstoneCarved", (0.84, 0.56, 0.36), (0.38, 0.22, 0.18), (0.98, 0.78, 0.58), roughness=0.90, tex_type="wave_sandstone", tex_scale=9.5, tex_contrast=0.22, bump_strength=0.38)
    m["terracotta"]     = make_cel_material("Mat_Terracotta", (0.72, 0.38, 0.24), (0.34, 0.18, 0.14), roughness=0.52, tex_type="voronoi_cobble", tex_scale=5.5, tex_contrast=0.14, bump_strength=0.10)
    m["leather_sofa"]   = make_cel_material("Mat_LeatherSofa", (0.42, 0.22, 0.12), (0.18, 0.09, 0.08), roughness=0.38, tex_scale=16.0, tex_contrast=0.12, bump_strength=0.08)
    m["copper_lamp"]    = make_cel_material("Mat_CopperLamp", (0.80, 0.44, 0.22), (0.36, 0.18, 0.12), roughness=0.26, metallic=0.88)
    m["rug_tribal"]     = make_cel_material("Mat_RugTribal", (0.74, 0.26, 0.18), (0.36, 0.14, 0.14), roughness=0.92, tex_type="brick", tex_scale=12.0, tex_contrast=0.24)
    m["opal_vein"]      = make_opal_iridescent_material("Mat_Opal_Vein")
    m["cactus_green"]   = make_cel_material("Mat_Succulent", (0.28, 0.56, 0.32), (0.12, 0.28, 0.20), roughness=0.72)

    # --- Zone 6 & 7: Setenil de las Bodegas, Spain ---
    m["cliff_rock"]     = make_cel_material("Mat_SetenilCliff", (0.46, 0.36, 0.27), (0.16, 0.16, 0.24), (0.78, 0.62, 0.44), roughness=0.92, tex_type="wave_sandstone", tex_scale=4.5, tex_contrast=0.28, bump_strength=0.48)
    m["white_stucco"]   = make_cel_material("Mat_WhiteStucco", (0.98, 0.96, 0.92), (0.50, 0.56, 0.72), (1.0, 0.96, 0.88), roughness=0.80, tex_scale=18.0, tex_contrast=0.07, bump_strength=0.14)
    m["cobblestone"]    = make_cel_material("Mat_Cobblestone", (0.56, 0.52, 0.48), (0.24, 0.26, 0.36), roughness=0.55, tex_type="voronoi_cobble", tex_scale=12.0, tex_contrast=0.22, bump_strength=0.28)
    m["shutter_green"]  = make_cel_material("Mat_ShutterGreen", (0.16, 0.36, 0.24), (0.08, 0.18, 0.16), roughness=0.65)
    m["wrought_iron"]   = make_cel_material("Mat_WroughtIron", (0.12, 0.13, 0.16), (0.06, 0.07, 0.12), roughness=0.48, metallic=0.80)
    m["geranium_red"]   = make_cel_material("Mat_GeraniumRed", (0.90, 0.16, 0.22), (0.48, 0.08, 0.16), roughness=0.62)
    m["geranium_pink"]  = make_cel_material("Mat_GeraniumPink", (0.92, 0.28, 0.52), (0.48, 0.12, 0.28), roughness=0.62)
    m["table_cloth"]    = make_cel_material("Mat_TableCloth", (0.86, 0.22, 0.20), (0.44, 0.12, 0.16), roughness=0.82, tex_type="brick", tex_scale=22.0, tex_contrast=0.35)
    m["spanish_plate"]  = make_cel_material("Mat_SpanishPlate", (0.20, 0.42, 0.82), (0.10, 0.22, 0.48), roughness=0.22)
    m["tapas_bread"]    = make_cel_material("Mat_TapasBread", (0.86, 0.62, 0.32), (0.46, 0.28, 0.16), roughness=0.78)
    m["laundry_cream"]  = make_cel_material("Mat_LaundryCream", (0.96, 0.90, 0.78), (0.58, 0.52, 0.50), roughness=0.88)
    m["laundry_coral"]  = make_cel_material("Mat_LaundryCoral", (0.88, 0.42, 0.32), (0.46, 0.20, 0.22), roughness=0.88)

    # --- Glass, Volumetric Beams & Real-World Signage ---
    m["glass_frosted"]  = make_glass_material("Mat_FrostedGlass", (0.78, 0.90, 0.98), alpha=0.34)
    m["god_ray_gold"]   = make_volumetric_beam_material("Mat_GodRayGold", (1.0, 0.86, 0.50), strength=0.09)
    m["flash_beam"]     = make_volumetric_beam_material("Mat_FlashBeam", (0.74, 0.94, 1.0), strength=0.15)
    m["iced_tea"]       = make_glass_material("Mat_IcedTea", (0.76, 0.42, 0.12), alpha=0.65)
    m["lemon_yellow"]   = make_cel_material("Mat_Lemon", (0.96, 0.86, 0.18), (0.56, 0.48, 0.12), roughness=0.45)

    for key, path in signs.items():
        if path.exists():
            m[key] = make_sign_material(f"Mat_{key}", path, emission_boost=0.22)
        else:
            m[key] = m["wood_warm"]

    # Colorful grocery/book accent materials
    m["box_cyan"]   = make_cel_material("Mat_BoxCyan",   (0.18, 0.72, 0.78), (0.08, 0.34, 0.44))
    m["box_yellow"] = make_cel_material("Mat_BoxYellow", (0.94, 0.76, 0.20), (0.52, 0.40, 0.12))
    m["box_coral"]  = make_cel_material("Mat_BoxCoral",  (0.88, 0.32, 0.26), (0.46, 0.14, 0.16))
    m["box_green"]  = make_cel_material("Mat_BoxGreen",  (0.24, 0.68, 0.38), (0.12, 0.34, 0.22))

    return m


# ============================================================================
# ZONE 1 & 2 & 3: WHITTIER, ALASKA (Begich Towers + Lobby + School Tunnel)
# ============================================================================
def build_whittier_zones(m: dict[str, bpy.types.Material]) -> None:
    col_ext = ensure_collection("Zone1_Whittier_Exterior")
    col_lob = ensure_collection("Zone2_Whittier_Lobby")
    col_tun = ensure_collection("Zone3_Whittier_Tunnel")

    # ---- ZONE 1: BEGICH TOWERS EXTERIOR & CHUGACH MOUNTAINS ----
    # Snow-covered plaza ground (strictly Z=0.0 top surface!)
    make_bevel_box("Whittier_SnowGround", (90.0, 42.0, 0.6), (0.0, -8.0, -0.6), col_ext, m["snow"], bevel=0.0)
    # Cleared walkway leading straight into lobby doors
    make_bevel_box("Whittier_Walkway", (4.2, 16.0, 0.04), (0.0, 2.0, -0.02), col_ext, m["begich_concrete"], bevel=0.01)

    # Waist-high smooth-sculpted snowdrifts flanking entrance (leaving clear 4.8m center path!)
    for side in (-1, 1):
        for idx, (dy, sx, sz) in enumerate([(1.2, 2.4, 0.85), (4.5, 2.8, 1.05), (7.6, 2.2, 0.95), (-3.0, 3.4, 1.1)]):
            make_sculpted_rock(
                f"SnowMound_{side}_{idx}", (sx, 2.2, sz), (side * (4.4 + idx * 0.4), dy, 0.05),
                col_ext, m["snow"], seed=100 + idx * 7 + (1 if side > 0 else 0), subdiv=3, rough=0.18, smooth=True,
            )
        # Metal stair handrails flanking doorway
        make_cylinder(f"RailPostA_{side}", 0.04, 1.0, (side * 1.9, 6.2, 0.0), col_ext, m["steel_brushed"], segs=8)
        make_cylinder(f"RailPostB_{side}", 0.04, 1.0, (side * 1.9, 9.0, 0.0), col_ext, m["steel_brushed"], segs=8)
        make_bevel_box(f"RailBar_{side}", (0.06, 2.9, 0.06), (side * 1.9, 7.6, 0.96), col_ext, m["steel_brushed"], bevel=0.01)

    # 14-Story Begich Towers (1957 Cold War Concrete Modular Facade!)
    rev_arch = DYNAMIC_REVEALS["begich_tower_arch"]
    make_bevel_box("Begich_Podium_L", (11.6, 1.0, 3.8), (-7.2, 9.8, 0.0), col_ext, m["begich_concrete"], bevel=0.04)
    make_bevel_box("Begich_Podium_R", (11.6, 1.0, 3.8), (7.2, 9.8, 0.0), col_ext, m["begich_concrete"], bevel=0.04)
    make_bevel_box("Begich_Canopy", (7.4, 2.8, 0.38), (0.0, 8.6, 3.35), col_ext, m["begich_trim"], bevel=0.04)
    make_bevel_box("Begich_CanopySnow", (7.2, 2.6, 0.18), (0.0, 8.6, 3.73), col_ext, m["snow"], bevel=0.05)
    for px in (-3.2, 3.2):
        make_cylinder(f"CanopyPillar_{px:.1f}", 0.14, 3.4, (px, 7.5, 0.0), col_ext, m["steel_brushed"], segs=12)
    # Upright crisp Begich Towers Plaque facing camera (-Y)!
    make_sign_plane("Sign_Begich_Ext", 4.4, 0.95, (0.0, 7.12, 3.65), 0.0, col_ext, m["sign_begich_ext"], m["begich_trim"])

    # Hinged Frosted Aluminum Glass Double Doors (Y=9.6) -> Swing OPEN smoothly at f=64..96!
    for side, s_name in [(-1, "L"), (1, "R")]:
        hinge = bpy.data.objects.new(f"LobbyDoorHinge_{s_name}", None)
        hinge.location = (side * 1.40, 9.6, 0.0)
        link_obj(hinge, col_ext)
        # Door aluminum frame + glass pane
        offset_x = -side * 0.68
        df = make_bevel_box(f"LobbyDoorFrame_{s_name}", (1.36, 0.09, 2.65), (offset_x, 0.0, 0.0), col_ext, m["steel_brushed"], bevel=0.015)
        df.parent = hinge
        dg = make_bevel_box(f"LobbyDoorGlass_{s_name}", (1.14, 0.11, 2.28), (offset_x, 0.0, 0.22), col_ext, m["glass_frosted"], bevel=0.01)
        dg.parent = hinge
        handle = make_bevel_box(f"LobbyDoorHandle_{s_name}", (0.06, 0.18, 0.55), (-side * 1.18, -0.06, 1.05), col_ext, m["brass"], bevel=0.01)
        handle.parent = hinge
        # Keyframe door closed -> pushed open inward as Fajar enters!
        hinge.rotation_euler = (0.0, 0.0, 0.0)
        hinge.keyframe_insert("rotation_euler", frame=62)
        hinge.rotation_euler = (0.0, 0.0, side * math.radians(-105.0))
        hinge.keyframe_insert("rotation_euler", frame=84)
        hinge.keyframe_insert("rotation_euler", frame=110)
        hinge.rotation_euler = (0.0, 0.0, 0.0)
        hinge.keyframe_insert("rotation_euler", frame=132)
        _set_bezier_ease(hinge)

    # 13 Upper Modular Stories (Floors 2..14, Z=3.8..41.5m) with Architectural Build-up!
    rng_w = random.Random(1957)
    for fl in range(13):
        zf = 3.8 + fl * 2.85
        fl_slab = make_bevel_box(f"Begich_Floor_{fl+2:02d}", (26.0, 14.0, 2.82), (0.0, 16.8, zf), col_ext, m["begich_concrete"], bevel=0.05)
        band = make_bevel_box(f"Begich_Band_{fl+2:02d}", (26.3, 14.3, 0.34), (0.0, 16.8, zf), col_ext, m["begich_trim"], bevel=0.03)
        band.parent = fl_slab
        # Uniform grid of 10 retro apartment windows with recessed dark aluminum frames & mullions!
        for wi in range(10):
            wx = -11.0 + wi * 2.45
            is_lit = rng_w.random() < 0.62
            wframe = make_bevel_box(f"Begich_WinF_{fl+2:02d}_{wi}", (1.72, 0.18, 1.62), (wx, -7.02, 0.78), col_ext, m["begich_trim"], bevel=0.02)
            wframe.parent = fl_slab
            win = make_bevel_box(
                f"Begich_Win_{fl+2:02d}_{wi}", (1.46, 0.22, 1.38), (wx, -7.05, 0.90),
                col_ext, m["apt_lit"] if is_lit else m["apt_dark"], bevel=0.01,
            )
            win.parent = fl_slab
            mull = make_bevel_box(f"Begich_Mul_{fl+2:02d}_{wi}", (0.08, 0.25, 1.42), (wx, -7.06, 0.88), col_ext, m["begich_trim"], bevel=0.005)
            mull.parent = fl_slab
        # Staggered Architectural Build-up from floor 2 -> floor 14 (f=4..50, then Hard Lock!)
        animate_popup_z(fl_slab, rev_arch["start"] + fl * 2, dur=18)

    # Rooftop Mechanical Penthouse & Radio Mast
    pent = make_bevel_box("Begich_Penthouse", (8.5, 6.5, 3.2), (0.0, 16.5, 40.9), col_ext, m["begich_trim"], bevel=0.06)
    mast = make_cylinder("Begich_RadioMast", 0.14, 7.5, (0.0, 0.0, 3.2), col_ext, m["steel_brushed"], segs=8, r_top=0.03)
    mast.parent = pent
    animate_popup_z(pent, rev_arch["start"] + 28, dur=18)

    # Chugach Glacier Mountains Encircling Far Background (Strictly clear of School Tunnel X=5..46, Y=21..27!)
    mtn_specs = [
        (-42.0, 58.0, 26.0, 20.0, 38.0, 11),
        (-12.0, 72.0, 32.0, 22.0, 48.0, 22),
        (22.0,  70.0, 30.0, 20.0, 44.0, 33),
        (68.0,  54.0, 22.0, 18.0, 36.0, 44),
        (-48.0, 18.0, 18.0, 16.0, 28.0, 55),
    ]
    for idx, (mx, my, sx, sy, sz, sd) in enumerate(mtn_specs):
        make_sculpted_rock(f"Chugach_Mtn_{idx}", (sx, sy, sz), (mx, my, -2.0), col_ext, m["ice_mountain"], seed=sd, subdiv=3, rough=0.28)
        make_sculpted_rock(f"Chugach_Cap_{idx}", (sx * 0.72, sy * 0.72, sz * 0.56), (mx, my - 1.0, sz * 0.45), col_ext, m["snow"], seed=sd + 100, subdiv=2, rough=0.22)

    # Parked Snow-Covered SUVs + 1 Animated Moving Winter Pickup Truck!
    build_vehicle("Whittier_ParkedSUV_L", (-7.6, 2.2, 0.0), 18.0, col_ext, m["truck_blue"], m["apt_dark"], m["tire_dark"], m["neon_glow"], m["snow"])
    build_vehicle("Whittier_ParkedSUV_R", (8.2, 3.8, 0.0), -162.0, col_ext, m["truck_red"], m["apt_dark"], m["tire_dark"], m["neon_glow"], m["snow"])
    # Moving snow-dusted pickup cruising across foreground snowy road (Y=-6.2, clean ahead of camera!)
    mov_truck = build_vehicle("Whittier_MovingTruck", (-16.0, -5.8, 0.0), 0.0, col_ext, m["truck_red"], m["apt_dark"], m["tire_dark"], m["neon_glow"], m["snow"])
    mov_truck.keyframe_insert("location", frame=0)
    mov_truck.location.x = 18.0
    mov_truck.keyframe_insert("location", frame=95)

    # Isolated Exterior Slanted Arctic Blizzard Snowflakes (Strictly Y < 8.4 — NEVER leaks into lobby!)
    rng_sn = random.Random(2026)
    for si in range(110):
        sx0 = rng_sn.uniform(-9.0, 9.0)
        sy0 = rng_sn.uniform(-10.0, 8.2)
        sz0 = rng_sn.uniform(0.3, 6.5)
        r_fl = rng_sn.uniform(0.025, 0.055)
        flk = make_cylinder(f"SnowFlake_{si:03d}", r_fl, 0.015, (sx0, sy0, sz0), col_ext, m["snow"], segs=6, pivot_bottom=False)
        flk.keyframe_insert("location", frame=0)
        flk.location = (sx0 + 5.5, sy0, sz0 - 4.2)
        flk.keyframe_insert("location", frame=105)

    # ---- ZONE 2: BEGICH TOWERS WARM GROUND-FLOOR LOBBY (X=-5..5, Y=10..30, Z=0..3.6) ----
    make_bevel_box("Lobby_Floor", (10.4, 21.0, 0.3), (0.0, 20.0, -0.3), col_lob, m["linoleum"], bevel=0.0)
    make_bevel_box("Lobby_Ceiling", (10.4, 21.0, 0.3), (0.0, 20.0, 3.6), col_lob, m["lobby_wall"], bevel=0.0)
    make_bevel_box("Lobby_Wall_L", (0.35, 20.6, 3.7), (-5.0, 20.0, 0.0), col_lob, m["lobby_wall"], bevel=0.02)
    # Right wall split cleanly around School Tunnel entrance (Y=22.2..25.8)
    make_bevel_box("Lobby_Wall_R1", (0.35, 12.6, 3.7), (5.0, 16.0, 0.0), col_lob, m["lobby_wall"], bevel=0.02)
    make_bevel_box("Lobby_Wall_R2", (0.35, 4.6, 3.7), (5.0, 28.0, 0.0), col_lob, m["lobby_wall"], bevel=0.02)
    make_bevel_box("Lobby_Wall_R_Top", (0.35, 3.8, 0.95), (5.0, 24.0, 2.75), col_lob, m["lobby_wall"], bevel=0.02)
    make_bevel_box("Lobby_Wall_Back", (10.4, 0.35, 3.7), (0.0, 30.2, 0.0), col_lob, m["lobby_wall"], bevel=0.02)
    # Wood wainscoting strips along lower lobby walls
    make_bevel_box("Lobby_Wainscot_L", (0.12, 20.2, 1.05), (-4.78, 20.0, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    make_bevel_box("Lobby_Wainscot_R1", (0.12, 12.2, 1.05), (4.78, 16.0, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    # Warm 3400K glowing ceiling light panels
    for ly in (12.5, 16.5, 20.5, 24.5, 28.0):
        make_bevel_box(f"Lobby_LightPanel_{ly:.1f}", (2.4, 0.65, 0.08), (0.0, ly, 3.52), col_lob, m["neon_glow"], bevel=0.01)

    # Welcome Wet Rubber Mat + Boot & Coat Rack near Entry
    make_bevel_box("Lobby_WetMat", (2.4, 1.3, 0.03), (0.0, 10.9, 0.0), col_lob, m["tire_dark"], bevel=0.01)
    make_bevel_box("Lobby_BootRack", (0.65, 1.8, 0.45), (4.25, 12.2, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    for bi in range(4):
        make_cylinder(f"Lobby_Boot_{bi}", 0.09, 0.28, (4.22, 11.6 + bi * 0.4, 0.45), col_lob, m["tire_dark"], segs=8)

    # 14-Floor Building Directory Board & Community Bulletin Board (Left wall, upright facing +X!)
    make_sign_plane("Sign_Directory", 1.55, 2.15, (-4.72, 16.8, 1.68), 90.0, col_lob, m["sign_directory"], m["wood_warm"])
    cork = make_bevel_box("Lobby_CorkBoard", (0.10, 1.8, 1.25), (-4.75, 14.0, 1.25), col_lob, m["wood_warm"], bevel=0.02)
    for fi, (fy, fz, fm) in enumerate([(-0.5, 0.7, m["box_yellow"]), (0.0, 0.8, m["box_cyan"]), (0.45, 0.6, m["box_coral"]), (-0.25, 0.3, m["box_green"]), (0.3, 0.35, m["snow"])]):
        fl_p = make_bevel_box(f"Flyer_{fi}", (0.03, 0.32, 0.38), (0.06, fy, fz), col_lob, fm, bevel=0.005)
        fl_p.parent = cork
    # Warm lobby back-wall rich set dressing (potted plant, parcels & framed Alaska poster)
    make_cylinder("Lobby_PlantPot", 0.28, 0.42, (-0.8, 29.3, 0.0), col_lob, m["terracotta"], segs=12, r_top=0.34)
    make_sculpted_rock("Lobby_PlantLeaf", (0.45, 0.45, 0.62), (-0.8, 29.3, 0.82), col_lob, m["cactus_green"], seed=18, subdiv=2, rough=0.35)
    make_bevel_box("Lobby_BackTrim", (10.0, 0.14, 1.05), (0.0, 29.95, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    make_bevel_box("Lobby_Parcel1", (0.42, 0.34, 0.28), (-3.55, 28.4, 1.18), col_lob, m["tapas_bread"], bevel=0.02)
    make_bevel_box("Lobby_Parcel2", (0.30, 0.28, 0.22), (-3.55, 28.4, 1.46), col_lob, m["box_cyan"], bevel=0.02)
    make_bevel_box("Lobby_LetterStack", (0.24, 0.18, 0.08), (-3.45, 26.8, 1.18), col_lob, m["snow"], bevel=0.01)

    # Dual Brushed-Steel Elevator Doors (X=-4.75, Y=25.0) -> Slide OPEN at f=362..386!
    make_bevel_box("Elevator_Frame", (0.28, 2.5, 2.75), (-4.78, 25.0, 0.0), col_lob, m["steel_brushed"], bevel=0.03)
    make_bevel_box("Elevator_Recess", (1.2, 2.1, 2.65), (-5.5, 25.0, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    make_bevel_box("Elevator_FloorDisplay", (0.12, 0.68, 0.26), (-4.68, 25.0, 2.86), col_lob, m["neon_glow"], bevel=0.02)
    ed_l = make_bevel_box("ElevDoor_L", (0.08, 1.04, 2.52), (-4.68, 24.48, 0.0), col_lob, m["steel_brushed"], bevel=0.015)
    ed_r = make_bevel_box("ElevDoor_R", (0.08, 1.04, 2.52), (-4.68, 25.52, 0.0), col_lob, m["steel_brushed"], bevel=0.015)
    for ed, dir_y in [(ed_l, -0.92), (ed_r, 0.92)]:
        oy = ed.location.y
        ed.keyframe_insert("location", frame=360)
        ed.location.y = oy + dir_y
        ed.keyframe_insert("location", frame=384)
        ed.keyframe_insert("location", frame=422)
        ed.location.y = oy
        ed.keyframe_insert("location", frame=445)
        _set_bezier_ease(ed)

    # U.S. Post Office Counter + Brass PO Boxes Wall (Assembly Build-up f=205..241!)
    rev_po = DYNAMIC_REVEALS["lobby_post_assembly"]
    po_counter = make_bevel_box("PO_Counter", (1.35, 3.2, 1.08), (-3.85, 27.6, 0.0), col_lob, m["wood_warm"], bevel=0.04)
    po_top = make_bevel_box("PO_CounterTop", (1.48, 3.32, 0.09), (0.0, 0.0, 1.08), col_lob, m["brass"], bevel=0.02)
    po_top.parent = po_counter
    animate_assembly_drop(po_counter, rev_po["start"], dur=26, offset_vec=(0.0, 0.0, 1.2))
    # Post Office Sign (Upright facing +X toward lobby!)
    po_sign = make_sign_plane("Sign_PostOffice", 2.8, 0.68, (-3.65, 27.6, 2.68), 90.0, col_lob, m["sign_post_office"], m["wood_warm"])
    animate_assembly_drop(po_sign, rev_po["start"] + 6, dur=24, offset_vec=(0.0, 0.0, 1.0))
    # 20 Numbered Brass PO Boxes Grid on Left Wall
    po_boxes = make_bevel_box("PO_BoxWall", (0.28, 2.4, 1.55), (-4.70, 27.6, 1.05), col_lob, m["brass"], bevel=0.02)
    for r in range(4):
        for c_i in range(5):
            bx = make_bevel_box(f"POBox_{r}_{c_i}", (0.05, 0.38, 0.28), (0.15, -0.92 + c_i * 0.46, 0.14 + r * 0.35), col_lob, m["steel_brushed"], bevel=0.01)
            bx.parent = po_boxes
    animate_assembly_drop(po_boxes, rev_po["start"] + 12, dur=24, offset_vec=(-0.8, 0.0, 0.0))

    # Hero 3D Prop: Pak Arthur's Steaming "WHITTIER" Ceramic Coffee Mug!
    mug = make_cylinder("Prop_Whittier_Mug", 0.052, 0.11, (-2.5, 26.0, 0.95), col_lob, m["snow"], segs=12)
    mug_h = make_bevel_box("Prop_MugHandle", (0.04, 0.02, 0.065), (0.055, 0.0, 0.022), col_lob, m["snow"], bevel=0.006)
    mug_h.parent = mug

    # "KOZY KORNER" Minimarket Storefront & Colorful Stocked Shelves (Assembly Build-up f=255..289!)
    rev_mart = DYNAMIC_REVEALS["lobby_mart_assembly"]
    mart_sign = make_sign_plane("Sign_KozyKorner", 3.4, 0.90, (4.70, 19.6, 2.88), -90.0, col_lob, m["sign_kozy_korner"], m["wood_warm"])
    animate_assembly_drop(mart_sign, rev_mart["start"], dur=22, offset_vec=(0.0, 0.0, 0.9))
    shelf = make_bevel_box("Kozy_Shelf", (0.78, 3.6, 2.15), (4.35, 19.6, 0.0), col_lob, m["wood_warm"], bevel=0.03)
    prod_mats = [m["box_coral"], m["box_cyan"], m["box_yellow"], m["box_green"], m["truck_blue"]]
    for row_z in (0.45, 0.95, 1.45, 1.90):
        for pi in range(9):
            pm = prod_mats[(pi + int(row_z * 10)) % len(prod_mats)]
            pr = make_bevel_box(f"MartProd_{row_z:.2f}_{pi}", (0.28, 0.28, 0.32), (-0.20, -1.55 + pi * 0.38, row_z), col_lob, pm, bevel=0.02)
            pr.parent = shelf
    animate_assembly_drop(shelf, rev_mart["start"] + 8, dur=26, offset_vec=(1.0, 0.0, 0.0))

    # Directional Sign above School Tunnel Opening (Upright facing -X into lobby!)
    tun_entry_sign = make_sign_plane("Sign_ToSchoolTunnel", 2.5, 0.65, (4.72, 24.0, 2.98), -90.0, col_lob, m["sign_school_tunnel"], m["tunnel_blue"])
    animate_popup_z(tun_entry_sign, DYNAMIC_REVEALS["tunnel_sign_popup"]["start"], dur=20)
    # Also inside the tunnel archway at X=27.5 so Maya's shot showcases "SCHOOL TUNNEL ->"!
    make_sign_plane("Sign_InsideTunnel", 2.2, 0.55, (31.5, 24.0, 0.45), -90.0, col_tun, m["sign_school_tunnel"], m["tunnel_blue"])

    # ---- ZONE 3: WHITTIER UNDERGROUND SCHOOL TUNNEL (X=5..45, Y=24, Z=0..-2.4) ----
    # 12 Descending Concrete Steps (X=5.0..11.6, Z=0.0 -> -2.4)
    for si in range(12):
        sx = 5.25 + si * 0.55
        sz = -0.20 * (si + 1)
        make_bevel_box(f"TunnelStep_{si:02d}", (0.60, 3.8, 0.24), (sx, 24.0, sz), col_tun, m["tunnel_concrete"], bevel=0.015)
    # Stairwell enclosing walls & slanted roof
    make_bevel_box("StairWall_N", (7.4, 0.35, 5.8), (8.4, 26.0, -2.6), col_tun, m["tunnel_blue"], bevel=0.02)
    make_bevel_box("StairWall_S", (7.4, 0.35, 5.8), (8.4, 22.0, -2.6), col_tun, m["tunnel_blue"], bevel=0.02)
    make_bevel_box("StairRoof", (7.8, 4.4, 0.35), (8.4, 24.0, 2.3), col_tun, m["tunnel_concrete"], rot=(0.0, math.radians(18.0), 0.0), bevel=0.02)

    # Main Underground Arched Concrete Tunnel (X=11.5..46.0, Floor Z=-2.4)
    make_bevel_box("Tunnel_Floor", (35.0, 4.6, 0.35), (29.0, 24.0, -2.75), col_tun, m["tunnel_concrete"], bevel=0.0)
    # Yellow Lower Dado + Blue Stripe + Concrete Upper Walls
    for side, wy in [("S", 21.85), ("N", 26.15)]:
        make_bevel_box(f"Tunnel_DadoY_{side}", (35.0, 0.35, 1.35), (29.0, wy, -2.4), col_tun, m["tunnel_yellow"], bevel=0.02)
        make_bevel_box(f"Tunnel_StripeB_{side}", (35.0, 0.38, 0.34), (29.0, wy, -1.05), col_tun, m["tunnel_blue"], bevel=0.01)
        make_bevel_box(f"Tunnel_Upper_{side}", (35.0, 0.35, 1.85), (29.0, wy, -0.71), col_tun, m["tunnel_concrete"], bevel=0.02)
    make_bevel_box("Tunnel_Ceiling", (35.0, 4.8, 0.35), (29.0, 24.0, 1.12), col_tun, m["tunnel_concrete"], bevel=0.0)
    # Concrete Arch Ribs + Overhead Red & Yellow Heating Pipes + Caged Fluorescent Lights
    make_cylinder("Tunnel_PipeRed", 0.11, 34.0, (29.0, 22.5, 0.72), col_tun, m["pipe_red"], segs=10, rot=(0.0, math.pi * 0.5, 0.0), pivot_bottom=False)
    make_cylinder("Tunnel_PipeYel", 0.09, 34.0, (29.0, 22.9, 0.78), col_tun, m["tunnel_yellow"], segs=10, rot=(0.0, math.pi * 0.5, 0.0), pivot_bottom=False)
    for rx in range(13, 44, 4):
        make_bevel_box(f"TunnelRib_S_{rx}", (0.36, 0.25, 3.5), (float(rx), 22.12, -2.4), col_tun, m["tunnel_blue"], bevel=0.02)
        make_bevel_box(f"TunnelRib_N_{rx}", (0.36, 0.25, 3.5), (float(rx), 25.88, -2.4), col_tun, m["tunnel_blue"], bevel=0.02)
        make_bevel_box(f"TunnelRib_T_{rx}", (0.36, 4.1, 0.26), (float(rx), 24.0, 0.88), col_tun, m["tunnel_blue"], bevel=0.02)
        make_bevel_box(f"TunnelLamp_{rx}", (1.35, 0.28, 0.10), (float(rx) + 2.0, 24.0, 0.96), col_tun, m["neon_glow"], bevel=0.01)
    # Heavy Steel Bulkhead Portal Frame near Tunnel Exit (X=38.0) + Dark Speed-Dive Portal (X=45.0)
    make_bevel_box("TunnelPortal_L", (0.55, 1.1, 3.4), (38.0, 22.4, -2.4), col_tun, m["steel_brushed"], bevel=0.03)
    make_bevel_box("TunnelPortal_R", (0.55, 1.1, 3.4), (38.0, 25.6, -2.4), col_tun, m["steel_brushed"], bevel=0.03)
    make_bevel_box("TunnelPortal_Top", (0.55, 4.2, 0.7), (38.0, 24.0, 0.35), col_tun, m["steel_brushed"], bevel=0.03)
    make_bevel_box("Tunnel_EndDark", (0.4, 4.8, 4.2), (45.5, 24.0, -2.4), col_tun, m["tire_dark"], bevel=0.0)


# ============================================================================
# ZONE 4 & 5: COOBER PEDY, AUSTRALIA (Red Outback Desert + Sandstone Dugout)
# ============================================================================
def build_coober_pedy_zones(m: dict[str, bpy.types.Material]) -> None:
    col_des = ensure_collection("Zone4_CooberPedy_Desert")
    col_dug = ensure_collection("Zone5_CooberPedy_Dugout")

    # ---- ZONE 4: SCORCHING RED OUTBACK DESERT (X=100, Y=-18..17.2, Z=0 — stops cleanly at dugout wall!) ----
    make_bevel_box("Desert_Floor", (96.0, 36.0, 0.6), (100.0, -0.8, -0.6), col_des, m["red_desert"], bevel=0.0)

    # Red Ochre Outback Hillside Cliff strictly OUTSIDE the hollow Dugout interior (X=94.5..105.5, Y=18..34, Z=0..3.4)!
    make_sculpted_rock("DugoutHill_L", (8.2, 8.5, 5.2), (85.2, 24.5, 1.5), col_des, m["red_desert"], seed=301, subdiv=3, rough=0.18, stratify=0.08, smooth=True)
    make_sculpted_rock("DugoutHill_R", (8.2, 8.5, 5.4), (114.8, 24.5, 1.6), col_des, m["red_desert"], seed=302, subdiv=3, rough=0.18, stratify=0.08, smooth=True)
    make_sculpted_rock("DugoutHill_Top", (11.5, 9.5, 2.6), (100.0, 25.5, 6.4), col_des, m["red_desert"], seed=303, subdiv=3, rough=0.16, stratify=0.06, smooth=True)
    # Organic red sandstone boulders blending the hillside organically around the timber doorway!
    make_sculpted_rock("CaveRock_L1", (3.6, 2.2, 2.8), (94.8, 16.0, 1.8), col_des, m["red_desert"], seed=311, subdiv=3, rough=0.22, stratify=0.08, smooth=True)
    make_sculpted_rock("CaveRock_R1", (3.6, 2.2, 2.9), (105.2, 16.0, 1.9), col_des, m["red_desert"], seed=312, subdiv=3, rough=0.22, stratify=0.08, smooth=True)
    make_sculpted_rock("CaveRock_Top1", (5.8, 2.0, 1.4), (100.0, 16.2, 4.1), col_des, m["red_desert"], seed=313, subdiv=3, rough=0.20, stratify=0.07, smooth=True)
    # Clean facade rock wall around timber doorway (Y=16.8) leaving exact 2.4m doorway clear!
    make_bevel_box("CaveFacade_L", (6.4, 2.0, 4.4), (95.4, 16.8, 0.0), col_des, m["red_desert"], bevel=0.22)
    make_bevel_box("CaveFacade_R", (6.4, 2.0, 4.4), (104.6, 16.8, 0.0), col_des, m["red_desert"], bevel=0.22)
    make_bevel_box("CaveFacade_Top", (15.6, 2.2, 1.9), (100.0, 16.8, 2.85), col_des, m["red_desert"], bevel=0.22)

    # Heavy Timber Door Frame + Hinged Thick Wooden Cave Door (Swings OPEN at f=1048..1085!)
    make_bevel_box("CaveTimber_L", (0.28, 0.45, 2.9), (98.8, 15.7, 0.0), col_des, m["wood_warm"], bevel=0.03)
    make_bevel_box("CaveTimber_R", (0.28, 0.45, 2.9), (101.2, 15.7, 0.0), col_des, m["wood_warm"], bevel=0.03)
    make_bevel_box("CaveTimber_Top", (2.8, 0.48, 0.30), (100.0, 15.7, 2.78), col_des, m["wood_warm"], bevel=0.03)
    door_hinge = bpy.data.objects.new("CaveDoorHinge", None)
    door_hinge.location = (98.95, 15.75, 0.0)
    link_obj(door_hinge, col_des)
    door_leaf = make_bevel_box("CaveWoodDoor", (2.10, 0.16, 2.74), (1.05, 0.0, 0.0), col_des, m["wood_warm"], bevel=0.025)
    door_leaf.parent = door_hinge
    door_ring = make_cylinder("CaveDoorHandle", 0.08, 0.10, (1.82, -0.10, 1.25), col_des, m["brass"], segs=10, rot=(math.pi * 0.5, 0.0, 0.0), pivot_bottom=False)
    door_ring.parent = door_hinge
    door_hinge.rotation_euler = (0.0, 0.0, 0.0)
    door_hinge.keyframe_insert("rotation_euler", frame=1046)
    door_hinge.rotation_euler = (0.0, 0.0, math.radians(108.0))
    door_hinge.keyframe_insert("rotation_euler", frame=1078)
    door_hinge.keyframe_insert("rotation_euler", frame=1115)
    _set_bezier_ease(door_hinge)

    # Clay Potted Succulents flanking Cave Door!
    for sx in (98.1, 101.9):
        make_cylinder(f"SucPot_{sx:.1f}", 0.24, 0.36, (sx, 15.0, 0.0), col_des, m["terracotta"], segs=10, r_top=0.30)
        make_sculpted_rock(f"SucPlant_{sx:.1f}", (0.25, 0.25, 0.30), (sx, 15.0, 0.48), col_des, m["cactus_green"], seed=int(sx), subdiv=2, rough=0.30)

    # Pale-White Conical Mullock Heaps (Excavated Mine Spoil Mounds!)
    mullocks = [
        (92.0, 3.5, 3.4, 2.2), (109.5, 4.8, 4.0, 2.6), (86.0, 9.5, 4.6, 3.1),
        (114.0, 11.0, 4.8, 3.2), (94.0, -4.5, 3.0, 1.8), (108.0, -3.0, 3.5, 2.1),
        (81.0, -6.0, 5.2, 3.5), (120.0, 2.0, 5.4, 3.6),
    ]
    for idx, (mx, my, mr, mh) in enumerate(mullocks):
        make_cylinder(f"MullockHeap_{idx}", mr, mh, (mx, my, 0.0), col_des, m["mullock_white"], segs=12, r_top=mr * 0.24)

    # Hero Vent Pipe at (100, 2.0) — Match-Cut Portal where Camera Erupts!
    make_cylinder("HeroVentPipe_Rim", 0.36, 1.15, (100.0, 2.0, 0.0), col_des, m["pvc_white"], segs=16)

    # 22 White PVC Ventilation Pipes across Desert Hills -> Staggered Procedural Reveal Wave!
    rev_pipes = DYNAMIC_REVEALS["desert_pipes_wave"]
    pipe_coords = [
        (96.5, 4.2, 1.4), (103.5, 4.5, 1.6), (94.2, 7.8, 1.5), (105.8, 8.2, 1.8),
        (97.8, 9.6, 1.3), (102.8, 10.4, 1.5), (91.5, 6.0, 1.7), (108.5, 6.4, 1.6),
        (90.0, 11.5, 1.9), (110.2, 12.2, 1.7), (95.5, 1.2, 1.3), (104.5, 1.5, 1.5),
        (93.0, 13.8, 1.6), (107.0, 14.0, 1.5), (88.0, 4.0, 1.8), (112.0, 3.8, 1.7),
        (98.5, 17.5, 1.8), (101.8, 18.2, 1.6), (95.0, 19.0, 1.7), (105.0, 19.2, 1.8),
        (89.5, 0.5, 1.5), (111.5, 0.2, 1.6),
    ]
    for idx, (px, py, ph) in enumerate(pipe_coords):
        pz = 3.6 if py > 16.5 else 0.0
        pipe = make_cylinder(f"VentPipe_{idx:02d}", 0.16, ph, (px, py, pz), col_des, m["pvc_white"], segs=12)
        cap = make_cylinder(f"VentCap_{idx:02d}", 0.28, 0.16, (0.0, 0.0, ph + 0.02), col_des, m["steel_brushed"], segs=12, r_top=0.03)
        cap.parent = pipe
        animate_popup_z(pipe, rev_pipes["start"] + idx * rev_pipes["stagger"], dur=rev_pipes["dur"])

    # Rusted Yellow Triangle "DANGER: OPEN SHAFTS" Sign (Framed clearly beside Fajar, 3D Pop-up f=948..970!)
    make_cylinder("OpenShaft_Rim", 0.85, 0.18, (103.4, 8.6, 0.0), col_des, m["red_desert"], segs=14)
    make_cylinder("OpenShaft_Hole", 0.65, 0.22, (103.4, 8.6, 0.02), col_des, m["tire_dark"], segs=14)
    danger_root = make_cylinder("DangerSign_Post", 0.07, 1.55, (101.6, 8.2, 0.0), col_des, m["wood_warm"], segs=8)
    d_board = make_sign_plane("Sign_DangerShafts", 0.96, 0.96, (0.0, -0.09, 1.48), -22.0, col_des, m["sign_danger_shafts"], m["tire_dark"])
    d_board.parent = danger_root
    animate_popup_z(danger_root, DYNAMIC_REVEALS["danger_sign_popup"]["start"], dur=DYNAMIC_REVEALS["danger_sign_popup"]["dur"])

    # Distant Old Opal Mining Rig + Animated Cruising Outback Pickup Truck!
    make_bevel_box("MiningRig_Base", (3.6, 2.2, 1.2), (85.0, 12.0, 0.0), col_des, m["copper_lamp"], bevel=0.05)
    make_cylinder("MiningRig_Derrick", 0.22, 6.8, (85.0, 12.0, 1.1), col_des, m["steel_brushed"], segs=6, r_top=0.08)
    outback_ute = build_vehicle("Coober_OutbackPickup", (76.0, 26.5, 4.2), 0.0, col_des, m["mullock_white"], m["apt_dark"], m["tire_dark"], m["neon_glow"])
    outback_ute.keyframe_insert("location", frame=836)
    outback_ute.location.x = 124.0
    outback_ute.keyframe_insert("location", frame=1080)

    # ---- ZONE 5: COOBER PEDY CARVED SANDSTONE DUGOUT (X=94.5..105.5, Y=18..34, Z=0..3.4) ----
    make_bevel_box("Dugout_Floor", (11.5, 19.0, 0.35), (100.0, 25.5, -0.35), col_dug, m["terracotta"], bevel=0.0)
    # Sculpted curved tunnelling-machine sandstone walls & arched cavern ceiling!
    make_bevel_box("Dugout_Wall_L", (0.7, 17.5, 3.6), (94.6, 26.2, 0.0), col_dug, m["sandstone_carved"], bevel=0.18)
    make_bevel_box("Dugout_Wall_R", (0.7, 17.5, 3.6), (105.4, 26.2, 0.0), col_dug, m["sandstone_carved"], bevel=0.18)
    make_bevel_box("Dugout_Wall_Back", (11.4, 0.7, 3.6), (100.0, 34.4, 0.0), col_dug, m["sandstone_carved"], bevel=0.18)
    make_bevel_box("Dugout_Ceiling", (11.6, 19.0, 0.6), (100.0, 25.5, 3.35), col_dug, m["sandstone_carved"], bevel=0.18)
    # Curved sandstone ceiling ribs mimicking tunnelling machine arches!
    for dy in (20.5, 24.5, 28.5, 32.5):
        make_sculpted_rock(f"DugoutArchL_{dy:.0f}", (0.75, 1.4, 1.9), (95.1, dy, 2.7), col_dug, m["sandstone_carved"], seed=int(dy) + 10, subdiv=2, rough=0.14)
        make_sculpted_rock(f"DugoutArchR_{dy:.0f}", (0.75, 1.4, 1.9), (104.9, dy, 2.7), col_dug, m["sandstone_carved"], seed=int(dy) + 30, subdiv=2, rough=0.14)

    # Woven Tribal Rug + Timber Coffee Table + Frosted Iced Tea Glass with Lemon!
    rev_dug = DYNAMIC_REVEALS["dugout_furniture_asm"]
    make_bevel_box("Dugout_Rug", (3.6, 2.4, 0.03), (99.4, 26.6, 0.0), col_dug, m["rug_tribal"], bevel=0.01)
    ctbl = make_bevel_box("Dugout_CoffeeTable", (1.65, 0.92, 0.44), (99.4, 26.6, 0.0), col_dug, m["wood_warm"], bevel=0.03)
    tea_gl = make_cylinder("Prop_IcedTea", 0.06, 0.16, (-0.32, 0.12, 0.44), col_dug, m["iced_tea"], segs=12, r_top=0.072)
    tea_gl.parent = ctbl
    lem = make_cylinder("Prop_LemonSlice", 0.045, 0.015, (-0.27, 0.12, 0.59), col_dug, m["lemon_yellow"], segs=10, rot=(0.0, 0.7, 0.0))
    lem.parent = ctbl
    animate_assembly_drop(ctbl, rev_dug["start"], dur=22, offset_vec=(0.0, 0.0, 1.1))

    # Plush Brown Leather Sofa (Jack sits cleanly at X=98.4, Y=28.4!)
    sofa = make_bevel_box("Dugout_LeatherSofa", (2.65, 1.05, 0.46), (98.4, 28.8, 0.0), col_dug, m["leather_sofa"], bevel=0.08)
    s_back = make_bevel_box("Sofa_Backrest", (2.65, 0.28, 0.62), (0.0, 0.38, 0.44), col_dug, m["leather_sofa"], bevel=0.07)
    s_back.parent = sofa
    for ax in (-1.22, 1.22):
        arm = make_bevel_box(f"Sofa_Arm_{ax:.1f}", (0.28, 1.02, 0.34), (ax, 0.0, 0.42), col_dug, m["leather_sofa"], bevel=0.06)
        arm.parent = sofa
    animate_assembly_drop(sofa, rev_dug["start"] + 6, dur=24, offset_vec=(0.0, 1.2, 0.6))

    # Recessed Bookshelf Carved into Sandstone Wall + Books + Crate of Rough Opal Samples!
    shelf_d = make_bevel_box("Dugout_RecessedShelf", (0.52, 2.2, 2.1), (104.8, 28.0, 0.25), col_dug, m["wood_warm"], bevel=0.03)
    for bi, bz in enumerate((0.45, 0.95, 1.45)):
        for k in range(5):
            bm_col = [m["box_coral"], m["box_cyan"], m["box_yellow"], m["box_green"], m["truck_blue"]][(bi + k) % 5]
            bk = make_bevel_box(f"DugBook_{bi}_{k}", (0.26, 0.14, 0.28), (-0.12, -0.78 + k * 0.36, bz), col_dug, bm_col, bevel=0.015)
            bk.parent = shelf_d
    animate_assembly_drop(shelf_d, rev_dug["start"] + 12, dur=24, offset_vec=(0.9, 0.0, 0.0))

    # Visual Gag: Standing Vintage Electric Fan (Completely Stationary/OFF — 24°C alami!)
    make_cylinder("Fan_Base", 0.22, 0.06, (96.2, 26.2, 0.0), col_dug, m["steel_brushed"], segs=12)
    make_cylinder("Fan_Pole", 0.035, 1.28, (96.2, 26.2, 0.05), col_dug, m["steel_brushed"], segs=10)
    make_cylinder("Fan_Cage", 0.28, 0.12, (96.2, 26.2, 1.38), col_dug, m["copper_lamp"], segs=16, rot=(math.pi * 0.5, 0.0, 0.35), pivot_bottom=False)

    # Framed Opal Mining Map (Upright facing +X into dugout!) + Hanging Industrial Copper Pendant Lamps
    make_sign_plane("Sign_OpalMap", 1.7, 1.15, (95.02, 25.0, 1.75), 90.0, col_dug, m["sign_opal_map"], m["wood_warm"])
    for lx, ly in [(98.6, 26.8), (102.6, 26.8), (100.2, 30.8)]:
        make_cylinder(f"LampCord_{lx:.0f}_{ly:.0f}", 0.018, 0.85, (lx, ly, 2.52), col_dug, m["wrought_iron"], segs=6)
        make_cylinder(f"CopperShade_{lx:.0f}_{ly:.0f}", 0.28, 0.22, (lx, ly, 2.34), col_dug, m["copper_lamp"], segs=14, r_top=0.08)
        make_cylinder(f"LampBulb_{lx:.0f}_{ly:.0f}", 0.08, 0.09, (lx, ly, 2.28), col_dug, m["neon_glow"], segs=10)

    # HERO PROP: Iridescent Blue-Green-Magenta Opal Crystal Vein + Elena's Volumetric Flashlight Cone!
    for oi, (oy, oz, sc) in enumerate([(30.5, 1.35, 0.24), (30.85, 1.48, 0.30), (31.15, 1.32, 0.22), (30.70, 1.18, 0.19), (31.0, 1.62, 0.20)]):
        make_sculpted_rock(f"Hero_OpalCrystal_{oi}", (0.14, sc, sc * 0.72), (104.92, oy, oz), col_dug, m["opal_vein"], seed=500 + oi, subdiv=2, rough=0.32)
    # Volumetric LED Flashlight Beam aimed softly from Elena onto Opal Vein!
    beam = make_cylinder(
        "Prop_Elena_FlashBeam", 0.34, 1.45, (104.22, 30.28, 1.40), col_dug, m["flash_beam"],
        segs=18, r_top=0.05, rot=(math.radians(90.0), 0.0, math.radians(130.0)), pivot_bottom=False,
    )
    beam.visible_shadow = False


# ============================================================================
# ZONE 6 & 7: SETENIL DE LAS BODEGAS — CALLE CUEVAS DEL SOL & UPPER BALCONIES
# ============================================================================
def build_setenil_zones(m: dict[str, bpy.types.Material]) -> None:
    col_st = ensure_collection("Zone6_Setenil_Street")
    col_bl = ensure_collection("Zone7_Setenil_Balcony")

    # Narrow Curving Cobblestone Street (X=194..206, Y=-10..46, Z=0.0)
    make_bevel_box("Setenil_CobbleStreet", (14.0, 62.0, 0.4), (200.0, 18.0, -0.4), col_st, m["cobblestone"], bevel=0.0)
    # Sidewalk terrace strip on cafe side (right, X=202.8..205.5)
    make_bevel_box("Setenil_TerraceCurb", (3.2, 42.0, 0.06), (204.0, 18.0, 0.0), col_st, m["cobblestone"], bevel=0.02)

    # COLOSSAL OVERHANGING SEDIMENTARY ROCK CLIFF (The Signature Setenil Hero Landmark!)
    # Looms from X=209 jutting all the way across to X=196.4 at Z=4.3..13.5m!
    cliff_blocks = [
        (203.2,  5.5, 9.0, 7.6, 5.5, 4.1, 601),
        (202.6, 12.5, 8.7, 7.8, 6.0, 4.0, 602),
        (202.2, 19.5, 8.4, 7.8, 6.2, 3.8, 603),  # Directly over Mateo's Bar La Roca terrace!
        (202.5, 26.8, 8.8, 7.6, 6.0, 4.0, 604),
        (203.4, 33.8, 9.2, 7.2, 5.5, 4.2, 605),
        (208.5, 18.0, 6.5, 5.5, 22.0, 7.5, 606), # Massive solid eastern cliff anchor backing!
    ]
    for idx, (cx, cy, cz, sx, sy, sz, sd) in enumerate(cliff_blocks):
        make_sculpted_rock(f"Setenil_OverhangCliff_{idx}", (sx, sy, sz), (cx, cy, cz), col_st, m["cliff_rock"], seed=sd, subdiv=3, rough=0.20, stratify=0.09)

    # Whitewashed Andalusian Houses Wedged Seamlessly Under the Overhanging Rock!
    # Right-side houses cleanly set back at X=205.4 (front wall at X=203.2) so Mateo at X=201.8 has 1.4m clear terrace!
    rev_houses = DYNAMIC_REVEALS["setenil_houses_arch"]
    house_specs = [
        # Right side tucked directly beneath giant rock roof (X=205.4)
        (205.4,  7.0, 4.2, 5.6, 4.8, 1),
        (205.4, 13.0, 4.2, 5.8, 4.7, 2),
        (205.4, 19.2, 4.4, 6.0, 4.6, 3),  # Bar La Roca building!
        (205.4, 25.6, 4.2, 6.2, 5.6, 4),  # 2nd-floor balcony house!
        (205.4, 32.0, 4.2, 5.8, 5.4, 5),
        # Opposite sunlit canyon cliffside white houses (X=193.8)
        (193.8,  8.5, 4.0, 6.2, 6.8, 6),
        (193.8, 15.5, 4.0, 6.6, 7.4, 7),
        (193.8, 23.0, 4.0, 6.8, 7.2, 8),
        (194.0, 30.5, 4.0, 6.2, 6.5, 9),
    ]
    for idx, (hx, hy, hw, hd, hh, tag) in enumerate(house_specs):
        hs = make_bevel_box(f"Setenil_WhiteHouse_{tag}", (hw, hd, hh), (hx, hy, 0.0), col_st, m["white_stucco"], bevel=0.08)
        face_x = -hw * 0.50 - 0.03 if hx > 200.0 else hw * 0.50 + 0.03
        # Dark green Andalusian wooden shuttered windows & timber doorways!
        for wy in (-1.3, 1.3):
            win = make_bevel_box(f"SetWin_{tag}_{wy:.1f}", (0.12, 0.95, 1.35), (face_x, wy, 1.55), col_st, m["shutter_green"], bevel=0.02)
            win.parent = hs
            glass = make_bevel_box(f"SetWinG_{tag}_{wy:.1f}", (0.14, 0.52, 1.08), (face_x, wy, 1.68), col_st, m["apt_lit"], bevel=0.01)
            glass.parent = hs
        door = make_bevel_box(f"SetDoor_{tag}", (0.14, 1.15, 2.25), (face_x, 0.0, 0.0), col_st, m["wood_warm"], bevel=0.02)
        door.parent = hs
        # Antique black wrought-iron wall lantern
        lant = make_bevel_box(f"SetLantern_{tag}", (0.28, 0.24, 0.38), (face_x + (-0.18 if hx > 200 else 0.18), 0.85, 2.55), col_st, m["wrought_iron"], bevel=0.02)
        lant.parent = hs
        bulb = make_cylinder(f"SetBulb_{tag}", 0.08, 0.18, (0.0, 0.0, 0.08), col_st, m["neon_glow"], segs=8)
        bulb.parent = lant
        # Terracotta roof tiles on exposed sunlit opposite side
        if hx < 200.0:
            roof = make_bevel_box(f"SetRoof_{tag}", (hw + 0.35, hd + 0.2, 0.36), (0.0, 0.0, hh), col_st, m["terracotta"], rot=(0.0, math.radians(-12.0), 0.0), bevel=0.03)
            roof.parent = hs
        animate_popup_z(hs, rev_houses["start"] + idx * 4, dur=22)

    # ZONE 7: 2nd-Floor Wrought-Iron Balconies, Cascading Geraniums & Animated Fluttering Laundry!
    for by in (19.5, 23.5, 26.8):
        # Wrought-iron Juliet balcony jutting from white facade
        bal = make_bevel_box(f"SetBalconyFloor_{by:.1f}", (0.95, 2.4, 0.14), (202.1, by, 3.85), col_bl, m["wrought_iron"], bevel=0.02)
        for rx in range(7):
            rail = make_cylinder(f"BalBar_{by:.1f}_{rx}", 0.02, 0.92, (-0.42, -1.05 + rx * 0.35, 0.14), col_bl, m["wrought_iron"], segs=6)
            rail.parent = bal
        top_r = make_bevel_box(f"BalTopRail_{by:.1f}", (0.06, 2.38, 0.05), (-0.42, 0.0, 1.05), col_bl, m["wrought_iron"], bevel=0.01)
        top_r.parent = bal
        # Blooming red & pink geranium flower pots lined on the balcony!
        for gi in range(4):
            gy = -0.82 + gi * 0.55
            pot = make_cylinder(f"BalPot_{by:.1f}_{gi}", 0.13, 0.22, (-0.36, gy, 0.14), col_bl, m["terracotta"], segs=8, r_top=0.17)
            pot.parent = bal
            fl_m = m["geranium_red"] if gi % 2 == 0 else m["geranium_pink"]
            fl = make_sculpted_rock(f"BalFlower_{by:.1f}_{gi}", (0.20, 0.22, 0.18), (-0.36, gy, 0.42), col_bl, fl_m, seed=700 + gi + int(by), subdiv=2, rough=0.35)
            fl.parent = bal

    # Animated Fluttering Laundry Clothesline stretched across Setenil alley (Z=4.95m)!
    make_cylinder("LaundryLine", 0.012, 7.6, (199.4, 24.8, 4.95), col_bl, m["wrought_iron"], segs=6, rot=(0.0, math.pi * 0.5, 0.0), pivot_bottom=False)
    for li, (lx, lmat) in enumerate([(197.8, m["laundry_cream"]), (199.1, m["laundry_coral"]), (200.4, m["laundry_cream"])]):
        sh = make_bevel_box(f"LaundrySheet_{li}", (0.88, 0.04, 1.05), (lx, 24.8, 4.92), col_bl, lmat, bevel=0.01, pivot_bottom=False)
        # Gentle animated Mediterranean breeze flutter!
        for kf in range(1520, 2283, 28):
            ang = math.radians(10.0 + math.sin((kf + li * 17) * 0.11) * 14.0)
            sh.rotation_euler = (ang, 0.0, 0.0)
            sh.keyframe_insert("rotation_euler", frame=kf)
        _set_bezier_ease(sh)

    # Bar La Roca Tapas Terrace: Upright Wooden Menu Board (Pop-up) + Bistro Tables & Wine Barrels!
    bar_sign = make_sign_plane("Sign_BarLaRoca", 1.05, 1.38, (202.8, 17.5, 1.15), -32.0, col_st, m["sign_bar_laroca"], m["wood_warm"])
    animate_popup_z(bar_sign, DYNAMIC_REVEALS["bar_sign_popup"]["start"], dur=DYNAMIC_REVEALS["bar_sign_popup"]["dur"])

    rev_cafe = DYNAMIC_REVEALS["setenil_cafe_wave"]
    table_ys = [11.5, 14.0, 16.5, 19.8, 22.8]
    for ti, ty in enumerate(table_ys):
        tx = 202.0 if ti != 3 else 201.6
        tbl = make_cylinder(f"BistroTable_{ti}", 0.05, 0.78, (tx, ty, 0.0), col_st, m["wrought_iron"], segs=10)
        base = make_cylinder(f"BistroBase_{ti}", 0.28, 0.05, (0.0, 0.0, 0.0), col_st, m["wrought_iron"], segs=10)
        base.parent = tbl
        top = make_cylinder(f"BistroTop_{ti}", 0.56, 0.06, (0.0, 0.0, 0.76), col_st, m["table_cloth"], segs=16)
        top.parent = tbl
        # Spanish Blue Ceramic Plate + Warm Tapas Bread + Green Olives!
        plate = make_cylinder(f"TapasPlate_{ti}", 0.19, 0.025, (0.08, -0.05, 0.82), col_st, m["spanish_plate"], segs=12)
        plate.parent = tbl
        bread = make_bevel_box(f"TapasBread_{ti}", (0.16, 0.09, 0.05), (0.08, -0.05, 0.845), col_st, m["tapas_bread"], bevel=0.015)
        bread.parent = tbl
        oj = make_cylinder(f"OrangeJuice_{ti}", 0.042, 0.13, (-0.18, 0.12, 0.82), col_st, m["box_yellow"], segs=10)
        oj.parent = tbl
        # Wicker bistro chair beside table
        chair = make_bevel_box(f"BistroChair_{ti}", (0.44, 0.44, 0.46), (0.0, 0.78, 0.0), col_st, m["wood_warm"], bevel=0.03)
        chair.parent = tbl
        animate_popup_z(tbl, rev_cafe["start"] + ti * rev_cafe["stagger"], dur=rev_cafe["dur"])

    # Oak Wine Barrels + Wall-Hung Geranium Pots along Street!
    for bi, by in enumerate([10.0, 18.2, 24.4]):
        bar = make_cylinder(f"WineBarrel_{bi}", 0.34, 0.92, (202.7, by, 0.0), col_st, m["wood_warm"], segs=14)
        animate_popup_z(bar, rev_cafe["start"] + (bi + 5) * rev_cafe["stagger"], dur=rev_cafe["dur"])
    for gi, gy in enumerate([9.0, 12.2, 15.4, 18.6, 21.8, 25.0]):
        gp = make_cylinder(f"StreetPot_{gi}", 0.18, 0.26, (202.85, gy, 1.85), col_st, m["terracotta"], segs=8, r_top=0.22)
        gf = make_sculpted_rock(f"StreetGeranium_{gi}", (0.26, 0.26, 0.22), (0.0, 0.0, 0.32), col_st, m["geranium_red"] if gi % 2 == 0 else m["geranium_pink"], seed=810 + gi, subdiv=2, rough=0.35)
        gf.parent = gp
        animate_popup_z(gp, rev_cafe["start"] + (gi + 2) * rev_cafe["stagger"], dur=16)

    # Background: Arched Andalusian Stone Bridge & Distant Sunlit Cliff Houses (Y=40..54)
    make_bevel_box("Setenil_StoneBridge", (12.0, 3.2, 2.2), (200.0, 42.0, 0.0), col_st, m["cliff_rock"], bevel=0.12)
    for dh in range(4):
        make_bevel_box(f"DistantWhiteHouse_{dh}", (4.2, 4.2, 4.5 + dh * 1.2), (195.5 + dh * 3.5, 49.0, 2.5 + dh * 1.4), col_st, m["white_stucco"], bevel=0.06)

    # Volumetric Golden Hour God Rays Slicing Diagonally High Above Alley (Clear of camera line-of-sight!)
    for ri, ry in enumerate([10.5, 22.5, 31.5]):
        ray = make_cylinder(
            f"GoldenGodRay_{ri}", 0.85, 11.0, (196.6, ry, 5.8), col_bl, m["god_ray_gold"],
            segs=18, r_top=0.35, rot=(0.0, math.radians(-38.0), math.radians(10.0)), pivot_bottom=False,
        )
        ray.visible_shadow = False

    # 3 Animated Gliding Birds Soaring Across Sunlit Setenil Canyon Sky!
    for bi in range(3):
        bird = make_bevel_box(f"SetenilBird_{bi}", (0.55, 0.14, 0.06), (192.0 + bi * 2.2, 36.0 + bi * 3.0, 9.2 + bi * 0.9), col_bl, m["wrought_iron"], bevel=0.01)
        bird.keyframe_insert("location", frame=1520)
        bird.location = (208.0 + bi * 1.5, 42.0 + bi * 2.0, 10.6 + bi * 0.7)
        bird.keyframe_insert("location", frame=2282)


# ============================================================================
# LIGHTING RIG (Low Sun + Long Shadows + Blue Shade + Dynamic Story Moods!)
# ============================================================================
def build_lighting() -> None:
    col_l = ensure_collection("Lighting_And_Atmosphere")

    # Dynamic World Sky Gradient (Updated per scene by render_blender_chunk.py!)
    world = bpy.data.worlds.new("StoryWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    n, l = nt.nodes, nt.links
    n.clear()
    out = n.new("ShaderNodeOutputWorld")
    bg = n.new("ShaderNodeBackground")
    bg.name = "WorldBG"
    bg.inputs["Strength"].default_value = 0.85
    ramp = n.new("ShaderNodeValToRGB")
    ramp.name = "SkyRamp"
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.46, 0.58, 0.72, 1.0)
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = (0.72, 0.80, 0.88, 1.0)
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs["Vector"])
    l.new(sep.outputs["Z"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bg.inputs["Color"])
    l.new(bg.outputs["Background"], out.inputs["Surface"])

    def add_light(name, ltype, loc, rot_deg, energy, color, size=1.0, spot_deg=45.0):
        ld = bpy.data.lights.new(name=name, type=ltype)
        ld.energy = energy
        ld.color = color
        if ltype == "AREA":
            ld.size = size
        elif ltype == "POINT":
            ld.shadow_soft_size = size
        elif ltype == "SPOT":
            ld.spot_size = math.radians(spot_deg)
            ld.spot_blend = 0.45
            ld.shadow_soft_size = size
        elif ltype == "SUN":
            ld.angle = math.radians(2.2)
        obj = bpy.data.objects.new(name, ld)
        obj.location = loc
        obj.rotation_euler = tuple(math.radians(a) for a in rot_deg)
        link_obj(obj, col_l)
        return obj

    # Low Cinematic Directional Sun (Long Shadows + Blue Shade!)
    # Rotated & tinted per zone via localized Area/Sun lighting!
    add_light("Sun_LowGolden", "SUN", (100.0, -20.0, 25.0), (68.0, 0.0, -34.0), 3.6, (1.0, 0.86, 0.66))

    # Zone 1: Cold Arctic Overcast Key + Cool Rim
    add_light("Light_WhittierExt_Key", "AREA", (-6.0, -6.0, 9.0), (52.0, 0.0, -28.0), 420.0, (0.76, 0.88, 1.0), size=8.0)

    # Zone 2: Warm 3400K Tungsten Lobby Ceiling Lamps (Stark warm contrast vs outside snow!)
    for ly in (13.0, 19.0, 25.0, 28.0):
        add_light(f"Light_Lobby_{ly:.0f}", "POINT", (0.0, ly, 3.15), (0.0, 0.0, 0.0), 175.0, (1.0, 0.86, 0.64), size=0.6)

    # Zone 3: School Tunnel Caged Fluorescent Vault Lamps (Bright & crisp!)
    for lx in (10.0, 16.0, 22.0, 28.0, 34.0, 40.0):
        add_light(f"Light_Tunnel_{lx:.0f}", "POINT", (lx, 24.0, 0.45), (0.0, 0.0, 0.0), 160.0, (0.94, 0.97, 1.0), size=0.5)

    # Zone 4: Scorching Coober Pedy Desert Blazing Overhead Sun
    add_light("Light_Desert_Sun", "AREA", (106.0, -4.0, 14.0), (35.0, 0.0, 25.0), 1600.0, (1.0, 0.86, 0.60), size=10.0)

    # Zone 5: Coober Pedy Dugout Warm Copper Indirect Lamps + Elena's Focused LED Flashlight!
    for lx, ly in [(98.6, 26.8), (102.4, 26.8), (100.2, 30.6)]:
        add_light(f"Light_Dugout_{lx:.0f}_{ly:.0f}", "POINT", (lx, ly, 2.25), (0.0, 0.0, 0.0), 220.0, (1.0, 0.78, 0.52), size=0.5)
    add_light("Light_Elena_Flashlight", "SPOT", (103.3, 29.5, 1.38), (88.0, 0.0, -52.0), 340.0, (0.72, 0.95, 1.0), size=0.14, spot_deg=38.0)

    # Zone 6 & 7: Setenil Mediterranean Golden Hour Bounce Light + Warm Cafe Lantern Glow!
    add_light("Light_Setenil_Bounce1", "AREA", (197.5, 12.0, 3.2), (65.0, 0.0, -72.0), 520.0, (1.0, 0.80, 0.52), size=6.0)
    add_light("Light_Setenil_Bounce2", "AREA", (197.5, 22.0, 3.4), (65.0, 0.0, -72.0), 560.0, (1.0, 0.78, 0.48), size=6.5)
    add_light("Light_Setenil_CafeWarm", "POINT", (201.8, 19.2, 2.7), (0.0, 0.0, 0.0), 110.0, (1.0, 0.82, 0.54), size=0.5)


# ============================================================================
# GROUND-LOCKED 2.5D CHARACTER CARDS (Zero Floating! Exact Foot Alignment!)
# ============================================================================
def build_character_cards() -> None:
    col_c = ensure_collection("Characters_25D_Hybrid")
    # Exact pixel calibration measured from render_characters_seq.py (ground_shadow=False):
    # y_top=0.0856, y_bot=0.9221 -> visible frac=0.8365, bottom margin=0.0779!
    vis_frac = 0.8365
    bot_margin = 0.0779
    aspect = 480.0 / 1040.0

    actor_heights = {
        "fajar": 1.72,
        "pak_arthur": 1.68,
        "maya": 1.56,
        "jack": 1.72,
        "elena": 1.66,
        "mateo": 1.74,
        "npc_whittier_1": 1.66,
        "npc_whittier_2": 1.70,
        "npc_setenil_1": 1.64,
        "npc_setenil_2": 1.68,
        "npc_setenil_3": 1.66,
    }

    for slug, h_m in actor_heights.items():
        plane_h = h_m / vis_frac
        plane_w = plane_h * aspect
        z_bot = -bot_margin * plane_h
        z_top = z_bot + plane_h

        bm = bmesh.new()
        v0 = bm.verts.new((-plane_w * 0.5, 0.0, z_bot))
        v1 = bm.verts.new((plane_w * 0.5, 0.0, z_bot))
        v2 = bm.verts.new((plane_w * 0.5, 0.0, z_top))
        v3 = bm.verts.new((-plane_w * 0.5, 0.0, z_top))
        face = bm.faces.new((v0, v1, v2, v3))
        uv_layer = bm.loops.layers.uv.new("UVMap")
        for loop, uv in zip(face.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
            loop[uv_layer].uv = uv
        mesh = bpy.data.meshes.new(f"Mesh_Actor_{slug}")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(f"Actor_{slug}", mesh)
        # Find any existing sprite for initial viewport preview
        default_img = SPRITES_ROOT / slug / "frame_0025.png"
        if not default_img.exists():
            cands = sorted((SPRITES_ROOT / slug).glob("*.png")) if (SPRITES_ROOT / slug).exists() else []
            if cands:
                default_img = cands[0]
        mat = make_character_card_material(f"Mat_Actor_{slug}", default_img)
        obj.data.materials.append(mat)
        link_obj(obj, col_c)


# ============================================================================
# CONTINUOUS 30-MOVE WIDE-ANGLE CAMERA & SCENE SETTINGS
# ============================================================================
def build_camera_and_render_settings() -> None:
    col_cam = ensure_collection("Camera_Rig")
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 0
    scene.frame_end = TOTAL_FRAMES - 1

    # Cycles CPU + OpenImageDenoise (100% reliable headless on Windows & GitHub Actions Linux!)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 20
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.04
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 2
    scene.cycles.transparent_max_bounces = 16
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.28

    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Punchy"
    except Exception:
        scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.15

    tgt = bpy.data.objects.new("CameraTarget", None)
    tgt.empty_display_type = "SPHERE"
    tgt.empty_display_size = 0.35
    link_obj(tgt, col_cam)

    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 20.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 350.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    link_obj(cam_obj, col_cam)
    scene.camera = cam_obj

    trk = cam_obj.constraints.new(type="TRACK_TO")
    trk.target = tgt
    trk.track_axis = "TRACK_NEGATIVE_Z"
    trk.up_axis = "UP_Y"

    # Bake exact camera path keyframes every 4 frames (render_blender_chunk.py sets exact per-frame too!)
    for f in range(0, TOTAL_FRAMES, 4):
        pos, look, lens = get_camera_state(f)
        cam_obj.location = pos
        tgt.location = look
        cam_data.lens = lens
        cam_obj.keyframe_insert("location", frame=f)
        tgt.keyframe_insert("location", frame=f)
        cam_data.keyframe_insert("lens", frame=f)


def main() -> None:
    print("Building 3D Master Scene: 3 Kota Paling Unik di Dunia...")
    clear_scene()
    mats = create_materials()
    build_whittier_zones(mats)
    build_coober_pedy_zones(mats)
    build_setenil_zones(mats)
    build_lighting()
    build_character_cards()
    build_camera_and_render_settings()

    PROD_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    print(f"SUCCESS! Saved Blender 4.2 Master Scene: {BLEND_OUT}")


if __name__ == "__main__":
    main()
