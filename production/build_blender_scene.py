"""
V2 MASTER 3D BLENDER 4.2 SCENE BUILDER — "3 Kota Paling Unik di Dunia" (VERTICAL 9:16)

Fixes ALL 7 Director Review Revisions:
  1. Vertical 9:16 (1080x1920 / 720x1280, camera.data.sensor_fit='VERTICAL', 24-28mm wide-angle)
  2. Strict 3-Collection Isolation: LOC_01_Whittier, LOC_02_CooberPedy, LOC_03_Setenil (ZERO bleed!)
  3. High-Detail Real-World Assets (ZERO primitive boxes!):
       - Whittier: Sleek vertical 14-story Begich Towers, wheeled 4x4 trucks with glass & snow,
         snow-laden Alaskan pines, streetlamps, numbered doors, Kozy Korner, USPS scale & mail,
         truly curved concrete arched School Tunnel with handrails, caged neons & steel fire-door!
       - Coober Pedy: 320m endless red desert + mesas, asymmetric displaced gravel mullock heaps,
         weathered vent pipes with base dirt collars & struts, lattice drilling rig, barbed-wire
         shaft fence, radial desert agave plants, recessed sandstone bookshelf, bladed vintage fan,
         throw-pillowed leather sofa, sharp multi-faceted rainbow Opal crystal cluster!
       - Setenil: High-subdiv smooth natural limestone overhanging cliff (ZERO cardboard stripes!),
         Pueblos Blancos with louvered dark-green shutters, brass handles, ceramic house numbers,
         wrought-iron lanterns & scrolled balconies, leafy multi-bloom geranium pots (ZERO cupcakes!),
         real sagging catenary clothesline, 4-legged wicker chairs, wine barrels & arched stone bridge!
  4. Natural Physical Skies (Arctic Clouds, Outback Nishita High-Dust Sun, Spanish Golden Hour 12° Sun)
  5. Reusable `animate_buildup()` (Exponential Ease-Out overshoot 0 -> 1.06 -> 1.0 + Hard Lock)
     at EVERY new location entry + Heavy Cliff Drop Lock triggering 4-frame micro camera shake!

Run:
  blender --background --python production/build_blender_scene.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from typing import Tuple

import bmesh
import bpy
from mathutils import Vector

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROD_DIR = PROJECT_ROOT / "production"
BLEND_OUT = PROD_DIR / "three_unique_cities.blend"
SPRITES_ROOT = PROD_DIR / "char_sprites"

sys.path.insert(0, str(PROD_DIR))

from blender_materials import (
    create_natural_worlds,
    get_sign_texture_paths,
    make_cel_material,
    make_character_card_material,
    make_cobblestone_material,
    make_desert_sand_material,
    make_glass_material,
    make_natural_rock_material,
    make_opal_iridescent_material,
    make_sign_material,
    make_snow_mountain_material,
    make_volumetric_beam_material,
)
from timeline_data import (
    DYNAMIC_REVEALS,
    FPS,
    LOCATION_RANGES,
    TOTAL_FRAMES,
    get_camera_state,
)


# ============================================================================
# CORE GEOMETRY & REUSABLE BUILD-UP ANIMATION HELPERS
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


def _set_bezier_ease(obj: bpy.types.Object) -> None:
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"


def animate_buildup(
    obj: bpy.types.Object,
    start_frame: int,
    duration: int = 10,
    mode: str = "POP_UP",
    offset: Tuple[float, float, float] | None = None,
) -> None:
    """
    Reusable Exponential Ease-Out Build-Up / Assembly Animator with subtle overshoot (0 -> 1.06 -> 1.0)
    followed by PERMANENT HARD LOCK at exact floor/world transform!
    Modes:
      - POP_UP    : Rises smoothly from beneath ground with scale 0 -> 1.06 -> 1.0 overshoot!
      - DROP_LOCK : Heavy object drops from overhead (+Z) and snaps firmly down onto roof/floor!
      - SLIDE_IN  : Flies/slides in cleanly from custom 3D offset vector and snaps into lock!
    """
    orig_loc = Vector(obj.location)
    orig_sc = tuple(obj.scale)
    f0 = max(0, int(start_frame) - 1)
    f_over = int(start_frame) + max(2, int(round(duration * 0.72)))
    f_end = int(start_frame) + max(4, int(duration))

    if mode == "DROP_LOCK":
        off = Vector(offset if offset else (0.0, 0.0, 9.5))
        obj.location = orig_loc + off
        obj.scale = (orig_sc[0] * 0.85, orig_sc[1] * 0.85, orig_sc[2] * 0.85)
        obj.keyframe_insert("location", frame=f0)
        obj.keyframe_insert("scale", frame=f0)

        # Heavy impact squash on landing!
        obj.location = orig_loc - Vector((0.0, 0.0, 0.12))
        obj.scale = (orig_sc[0] * 1.03, orig_sc[1] * 1.03, orig_sc[2] * 0.96)
        obj.keyframe_insert("location", frame=f_over)
        obj.keyframe_insert("scale", frame=f_over)
    elif mode == "SLIDE_IN":
        off = Vector(offset if offset else (0.0, 0.0, 1.4))
        obj.location = orig_loc + off
        obj.scale = (0.001, 0.001, 0.001)
        obj.keyframe_insert("location", frame=f0)
        obj.keyframe_insert("scale", frame=f0)

        obj.location = orig_loc - off * 0.04
        obj.scale = (orig_sc[0] * 1.06, orig_sc[1] * 1.06, orig_sc[2] * 1.06)
        obj.keyframe_insert("location", frame=f_over)
        obj.keyframe_insert("scale", frame=f_over)
    else:  # POP_UP
        drop_z = offset[2] if offset else 0.45
        obj.location = Vector((orig_loc.x, orig_loc.y, orig_loc.z - drop_z))
        obj.scale = (orig_sc[0] * 0.001, orig_sc[1] * 0.001, 0.001)
        obj.keyframe_insert("location", frame=f0)
        obj.keyframe_insert("scale", frame=f0)

        obj.location = Vector((orig_loc.x, orig_loc.y, orig_loc.z + 0.05))
        obj.scale = (orig_sc[0] * 1.04, orig_sc[1] * 1.04, orig_sc[2] * 1.07)
        obj.keyframe_insert("location", frame=f_over)
        obj.keyframe_insert("scale", frame=f_over)

    # Permanent HARD LOCK at exact resting surface coordinate!
    obj.location = orig_loc
    obj.scale = orig_sc
    obj.keyframe_insert("location", frame=f_end)
    obj.keyframe_insert("scale", frame=f_end)
    _set_bezier_ease(obj)


def make_bevel_box(
    name: str,
    size: Tuple[float, float, float],
    loc: Tuple[float, float, float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    rot: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.025,
    pivot_bottom: bool = True,
) -> bpy.types.Object:
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
        bm, cap_ends=True, cap_tris=False, segments=segs,
        radius1=radius, radius2=radius if r_top is None else r_top, depth=height,
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
    subdiv: int = 4,
    rough: float = 0.22,
    stratify: float = 0.05,
    smooth: bool = True,
    flatten_bottom: bool = False,
) -> bpy.types.Object:
    """High-subdiv organically displaced smooth rock / cliff / mullock heap (ZERO flat-box look!)."""
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    px, py, pz = rng.uniform(0, 10), rng.uniform(0, 10), rng.uniform(0, 10)
    for v in bm.verts:
        nx, ny, nz = v.co.x, v.co.y, v.co.z
        n1 = math.sin(nx * 2.9 + px) * math.cos(ny * 2.6 + py) * math.sin(nz * 3.1 + pz)
        n2 = math.sin(nx * 6.3 - py) * math.cos(ny * 5.7 + pz) * 0.42
        n3 = math.cos(nx * 12.1 + pz) * math.sin(ny * 11.4 - px) * 0.16
        strata = math.sin(nz * 9.5 + n1 * 1.4) * stratify
        disp = 1.0 + (n1 + n2 + n3) * rough + strata
        v.co.x = nx * scale_xyz[0] * disp
        v.co.y = ny * scale_xyz[1] * disp
        z_val = nz * scale_xyz[2] * disp
        if flatten_bottom:
            z_val = max(0.0, z_val + scale_xyz[2] * 0.55)
        v.co.z = z_val
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = smooth
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.data.materials.append(mat)
    return link_obj(obj, col)


def make_craggy_mountain(
    name: str,
    scale_xyz: Tuple[float, float, float],
    loc: Tuple[float, float, float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    seed: int = 1,
) -> bpy.types.Object:
    """Broad rugged Alaskan Chugach alpine peak mesh with natural glacier shoulders & craggy ridges."""
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=32, radius1=1.0, radius2=0.14, depth=1.0)
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=4, use_grid_fill=True)
    px, py, pz = rng.uniform(0, 10), rng.uniform(0, 10), rng.uniform(0, 10)
    for v in bm.verts:
        nx, ny, nz = v.co.x, v.co.y, v.co.z + 0.5  # nz in 0..1
        ang = math.atan2(ny, nx)
        ridge1 = 1.0 - abs(math.sin(ang * 3.0 + px + nz * 1.1))
        ridge2 = (1.0 - abs(math.sin(ang * 6.0 - py - nz * 2.0))) * 0.42
        crag = math.sin(nx * 7.5 + pz) * math.cos(ny * 7.0 - px) * 0.14
        radial = 0.78 + (ridge1 * 0.28 + ridge2 * 0.18 + crag) * (1.0 - nz * 0.35)
        # Broad natural alpine mountain profile (NOT sharp needle cones!)
        shoulder = 1.0 - (nz ** 1.35) * 0.62
        v.co.x = nx * scale_xyz[0] * radial * shoulder
        v.co.y = ny * scale_xyz[1] * radial * shoulder
        peak_jit = (ridge1 * 0.16 + crag * 0.32) * math.sin(nz * math.pi * 0.85)
        v.co.z = max(0.0, (nz * 0.78 + peak_jit) * scale_xyz[2])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = True  # Natural weathered glacier slopes with crisp bump!
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.data.materials.append(mat)
    return link_obj(obj, col)


def make_curved_tunnel_arch(
    name: str,
    length_x: float,
    width_y: float,
    wall_h: float,
    arch_r: float,
    loc: Tuple[float, float, float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    segs: int = 16,
) -> bpy.types.Object:
    """True curved semi-cylindrical vaulted concrete tunnel roof mesh (NOT a flat box!)."""
    bm = bmesh.new()
    half_x = length_x * 0.5
    thick = 0.28
    ring_inner = []
    ring_outer = []
    for i in range(segs + 1):
        ang = math.pi * (i / float(segs))
        cy = math.cos(ang) * (width_y * 0.5)
        cz = wall_h + math.sin(ang) * arch_r
        oy = math.cos(ang) * (width_y * 0.5 + thick)
        oz = wall_h + math.sin(ang) * (arch_r + thick)
        ring_inner.append((cy, cz))
        ring_outer.append((oy, oz))

    for i in range(segs):
        y0, z0 = ring_inner[i]
        y1, z1 = ring_inner[i + 1]
        oy0, oz0 = ring_outer[i]
        oy1, oz1 = ring_outer[i + 1]
        # Inner vaulted face
        v0 = bm.verts.new((-half_x, y0, z0))
        v1 = bm.verts.new((half_x, y0, z0))
        v2 = bm.verts.new((half_x, y1, z1))
        v3 = bm.verts.new((-half_x, y1, z1))
        bm.faces.new((v0, v1, v2, v3))
        # Outer backing shell (blocks stray light)
        o0 = bm.verts.new((-half_x, oy0, oz0))
        o1 = bm.verts.new((-half_x, oy1, oz1))
        o2 = bm.verts.new((half_x, oy1, oz1))
        o3 = bm.verts.new((half_x, oy0, oz0))
        bm.faces.new((o0, o1, o2, o3))

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = True
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
    bm = bmesh.new()
    v0 = bm.verts.new((-width * 0.5, 0.0, -height * 0.5))
    v1 = bm.verts.new((width * 0.5, 0.0, -height * 0.5))
    v2 = bm.verts.new((width * 0.5, 0.0, height * 0.5))
    v3 = bm.verts.new((-width * 0.5, 0.0, height * 0.5))
    f = bm.faces.new((v0, v1, v2, v3))
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for loop, uv in zip(f.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
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
            f"{name}_Frame", (width + 0.10, 0.06, height + 0.10), (0.0, 0.04, 0.0),
            col, frame_mat, bevel=0.015, pivot_bottom=False,
        )
        back.parent = obj
    return obj


# ============================================================================
# DETAILED REAL-WORLD HERO PROP BUILDERS
# ============================================================================
def build_detailed_vehicle(
    name: str,
    loc: Tuple[float, float, float],
    rot_z_deg: float,
    col: bpy.types.Collection,
    body_mat: bpy.types.Material,
    glass_mat: bpy.types.Material,
    tire_mat: bpy.types.Material,
    rim_mat: bpy.types.Material,
    headlight_mat: bpy.types.Material,
    taillight_mat: bpy.types.Material,
    snow_mat: bpy.types.Material | None = None,
) -> bpy.types.Object:
    """Detailed 3D 4x4 SUV / Pickup Truck with wheel rims, bumpers, cabin glass, headlights & roof rack!"""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0.0, 0.0, math.radians(rot_z_deg))
    link_obj(root, col)

    # Lower body + hood + rear bed + bumpers
    parts = [
        make_bevel_box(f"{name}_Chassis", (4.5, 1.88, 0.72), (0.0, 0.0, 0.44), col, body_mat, bevel=0.09),
        make_bevel_box(f"{name}_FrontBumper", (0.28, 1.96, 0.24), (2.28, 0.0, 0.36), col, tire_mat, bevel=0.04),
        make_bevel_box(f"{name}_RearBumper", (0.26, 1.96, 0.24), (-2.26, 0.0, 0.36), col, tire_mat, bevel=0.04),
        make_bevel_box(f"{name}_Grille", (0.08, 1.08, 0.34), (2.25, 0.0, 0.72), col, tire_mat, bevel=0.02),
        # Upper Cabin + Windshield + Side Windows + Roof Rack
        make_bevel_box(f"{name}_Cabin", (2.15, 1.72, 0.74), (-0.30, 0.0, 1.14), col, body_mat, bevel=0.08),
        make_bevel_box(f"{name}_Windshield", (2.20, 1.56, 0.48), (-0.30, 0.0, 1.24), col, glass_mat, bevel=0.03),
        make_bevel_box(f"{name}_SideGlass", (1.88, 1.76, 0.46), (-0.30, 0.0, 1.25), col, glass_mat, bevel=0.03),
        make_bevel_box(f"{name}_RoofRackL", (1.75, 0.06, 0.06), (-0.32, -0.68, 1.90), col, tire_mat, bevel=0.01),
        make_bevel_box(f"{name}_RoofRackR", (1.75, 0.06, 0.06), (-0.32, 0.68, 1.90), col, tire_mat, bevel=0.01),
    ]
    # 4 Wheels with dark rubber tire + metallic hubcap rims touching Z=0 strictly!
    for wx in (-1.38, 1.38):
        for wy in (-0.94, 0.94):
            wh = make_cylinder(f"{name}_Tire_{wx:.1f}_{wy:.1f}", 0.42, 0.30, (wx, wy, 0.42), col, tire_mat, segs=16, rot=(math.pi * 0.5, 0.0, 0.0), pivot_bottom=False)
            rim = make_cylinder(f"{name}_Rim_{wx:.1f}_{wy:.1f}", 0.23, 0.32, (wx, wy, 0.42), col, rim_mat, segs=12, rot=(math.pi * 0.5, 0.0, 0.0), pivot_bottom=False)
            parts.extend([wh, rim])
    # Headlights & Red Taillights
    for hy in (-0.68, 0.68):
        parts.append(make_bevel_box(f"{name}_HL_{hy:.1f}", (0.10, 0.30, 0.18), (2.26, hy, 0.86), col, headlight_mat, bevel=0.02))
        parts.append(make_bevel_box(f"{name}_TL_{hy:.1f}", (0.10, 0.28, 0.22), (-2.26, hy, 0.84), col, taillight_mat, bevel=0.02))
    # Optional thick snow accumulation on roof & hood (Whittier Alaska!)
    if snow_mat:
        parts.append(make_sculpted_rock(f"{name}_SnowRoof", (1.12, 0.88, 0.16), (-0.30, 0.0, 1.90), col, snow_mat, seed=91, subdiv=2, rough=0.14, smooth=True))
        parts.append(make_sculpted_rock(f"{name}_SnowHood", (0.72, 0.90, 0.12), (1.42, 0.0, 1.18), col, snow_mat, seed=92, subdiv=2, rough=0.14, smooth=True))

    for p in parts:
        p.parent = root
    return root


def build_snowy_pine_tree(
    name: str,
    loc: Tuple[float, float, float],
    scale: float,
    col: bpy.types.Collection,
    trunk_mat: bpy.types.Material,
    foliage_mat: bpy.types.Material,
    snow_mat: bpy.types.Material,
) -> bpy.types.Object:
    """Multi-tier Alaskan Spruce Pine Tree topped with fluffy white snow boughs!"""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.scale = (scale, scale, scale)
    link_obj(root, col)
    tr = make_cylinder(f"{name}_Trunk", 0.22, 1.8, (0.0, 0.0, 0.0), col, trunk_mat, segs=10, r_top=0.14)
    tr.parent = root
    for i, (r, h, z) in enumerate([(1.45, 1.75, 1.25), (1.18, 1.65, 2.35), (0.88, 1.45, 3.35), (0.54, 1.20, 4.25)]):
        cone = make_cylinder(f"{name}_Bough_{i}", r, h, (0.0, 0.0, z), col, foliage_mat, segs=10, r_top=0.05)
        cone.parent = root
        sn = make_cylinder(f"{name}_Snow_{i}", r * 0.88, h * 0.52, (0.0, 0.0, z + h * 0.48), col, snow_mat, segs=10, r_top=0.04)
        sn.parent = root
    return root


def build_desert_agave(
    name: str,
    loc: Tuple[float, float, float],
    col: bpy.types.Collection,
    pot_mat: bpy.types.Material,
    plant_mat: bpy.types.Material,
) -> bpy.types.Object:
    """Authentic multi-blade Agave / Prickly-Pear desert succulent in terracotta pot (NO polygon ball!)."""
    root = make_cylinder(name, 0.22, 0.34, loc, col, pot_mat, segs=12, r_top=0.28)
    for i in range(9):
        ang = (i / 9.0) * math.pi * 2.0
        tilt = math.radians(32.0 if i % 2 == 0 else 56.0)
        blade = make_bevel_box(
            f"{name}_Leaf_{i}", (0.08, 0.025, 0.36 if i % 2 == 0 else 0.28),
            (math.cos(ang) * 0.08, math.sin(ang) * 0.08, 0.32),
            col, plant_mat, rot=(math.sin(ang) * tilt, -math.cos(ang) * tilt, ang), bevel=0.008,
        )
        blade.parent = root
    return root


def build_leafy_geranium_pot(
    name: str,
    loc: Tuple[float, float, float],
    col: bpy.types.Collection,
    pot_mat: bpy.types.Material,
    leaf_mat: bpy.types.Material,
    bloom_mat: bpy.types.Material,
    seed: int = 1,
) -> bpy.types.Object:
    """Authentic Andalusian terracotta pot overflowing with dark-green foliage & tiny geranium flower clusters!"""
    rng = random.Random(seed)
    root = make_cylinder(name, 0.14, 0.22, loc, col, pot_mat, segs=10, r_top=0.19)
    rim = make_cylinder(f"{name}_Rim", 0.20, 0.04, (0.0, 0.0, 0.19), col, pot_mat, segs=10)
    rim.parent = root
    # Dense leafy green foliage base (8 overlapping angled green leaves)
    for i in range(8):
        ang = (i / 8.0) * math.pi * 2.0 + rng.uniform(-0.2, 0.2)
        lf = make_bevel_box(
            f"{name}_Leaf_{i}", (0.14, 0.09, 0.03),
            (math.cos(ang) * 0.12, math.sin(ang) * 0.12, 0.24 + rng.uniform(0.0, 0.06)),
            col, leaf_mat, rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), ang), bevel=0.01,
        )
        lf.parent = root
    # 7 distinct small blooming geranium flower clusters rising organically on stems!
    for j in range(7):
        ang = (j / 7.0) * math.pi * 2.0 + 0.3
        rad = rng.uniform(0.04, 0.15)
        hz = rng.uniform(0.28, 0.40)
        fl = make_sculpted_rock(
            f"{name}_Bloom_{j}", (0.055, 0.055, 0.05),
            (math.cos(ang) * rad, math.sin(ang) * rad, hz),
            col, bloom_mat, seed=seed * 20 + j, subdiv=1, rough=0.25, smooth=True,
        )
        fl.parent = root
    return root


def build_wicker_cafe_chair(
    name: str,
    loc: Tuple[float, float, float],
    yaw_deg: float,
    col: bpy.types.Collection,
    frame_mat: bpy.types.Material,
    wicker_mat: bpy.types.Material,
) -> bpy.types.Object:
    """Authentic 4-legged Andalusian bistro chair with woven wicker seat & curved wooden backrest!"""
    root = bpy.data.objects.new(name, None)
    root.location = loc
    root.rotation_euler = (0.0, 0.0, math.radians(yaw_deg))
    link_obj(root, col)
    seat = make_bevel_box(f"{name}_Seat", (0.44, 0.44, 0.05), (0.0, 0.0, 0.44), col, wicker_mat, bevel=0.015)
    seat.parent = root
    for lx in (-0.18, 0.18):
        for ly in (-0.18, 0.18):
            leg = make_cylinder(f"{name}_Leg_{lx:.2f}_{ly:.2f}", 0.02, 0.45, (lx, ly, 0.0), col, frame_mat, segs=8)
            leg.parent = root
    for bx in (-0.18, 0.18):
        post = make_cylinder(f"{name}_Post_{bx:.2f}", 0.02, 0.46, (bx, 0.19, 0.45), col, frame_mat, segs=8)
        post.parent = root
    back_slat1 = make_bevel_box(f"{name}_Back1", (0.40, 0.04, 0.12), (0.0, 0.19, 0.78), col, wicker_mat, bevel=0.01)
    back_slat2 = make_bevel_box(f"{name}_Back2", (0.40, 0.04, 0.09), (0.0, 0.19, 0.62), col, wicker_mat, bevel=0.01)
    back_slat1.parent = root
    back_slat2.parent = root
    return root


# ============================================================================
# MATERIAL PALETTE (V2 NATURAL GEOLOGY + CEL-SHADED SEMI-REALISTIC!)
# ============================================================================
def create_materials() -> dict[str, bpy.types.Material]:
    signs = get_sign_texture_paths()
    m: dict[str, bpy.types.Material] = {}

    # --- LOC 01: Whittier, Alaska ---
    m["snow"]            = make_cel_material("Mat_Snow", (0.93, 0.96, 1.00), (0.44, 0.60, 0.82), roughness=0.58, tex_scale=12.0, tex_contrast=0.08, bump_strength=0.14)
    m["ice_mountain"]    = make_snow_mountain_material("Mat_ChugachMountain")
    m["begich_concrete"] = make_cel_material("Mat_BegichConcrete", (0.58, 0.66, 0.74), (0.22, 0.34, 0.48), roughness=0.84, tex_scale=9.0, tex_contrast=0.18, bump_strength=0.22)
    m["begich_trim"]     = make_cel_material("Mat_BegichTrim", (0.30, 0.40, 0.52), (0.14, 0.20, 0.32), roughness=0.72, tex_scale=6.0)
    m["apt_lit"]         = make_cel_material("Mat_AptWindowLit", (0.98, 0.86, 0.56), (0.85, 0.70, 0.42), emission_rgb=(1.0, 0.84, 0.48), emission_strength=0.85)
    m["apt_dark"]        = make_cel_material("Mat_AptWindowDark", (0.16, 0.24, 0.36), (0.08, 0.12, 0.22), roughness=0.16, metallic=0.25)
    m["pine_green"]      = make_cel_material("Mat_AlaskanPine", (0.12, 0.28, 0.18), (0.06, 0.14, 0.16), roughness=0.82, tex_scale=14.0, tex_contrast=0.20, bump_strength=0.22)
    m["linoleum"]        = make_cel_material("Mat_Linoleum", (0.84, 0.78, 0.66), (0.45, 0.40, 0.36), roughness=0.30, tex_type="speckle_linoleum", tex_scale=36.0, tex_contrast=0.14, bump_strength=0.04)
    m["lobby_wall"]      = make_cel_material("Mat_LobbyWall", (0.90, 0.85, 0.75), (0.50, 0.46, 0.44), roughness=0.76, tex_scale=10.0, tex_contrast=0.08)
    m["wood_warm"]       = make_cel_material("Mat_WoodWarm", (0.50, 0.30, 0.17), (0.22, 0.13, 0.09), roughness=0.58, tex_type="wood", tex_scale=10.0, tex_contrast=0.20, bump_strength=0.16)
    m["steel_brushed"]   = make_cel_material("Mat_SteelBrushed", (0.64, 0.68, 0.74), (0.26, 0.32, 0.42), roughness=0.32, metallic=0.85, tex_scale=24.0)
    m["brass"]           = make_cel_material("Mat_Brass", (0.84, 0.66, 0.26), (0.42, 0.30, 0.12), roughness=0.26, metallic=0.88, tex_scale=12.0)
    m["tunnel_yellow"]   = make_cel_material("Mat_TunnelYellow", (0.90, 0.74, 0.20), (0.48, 0.38, 0.14), roughness=0.72, tex_scale=10.0, tex_contrast=0.14, bump_strength=0.16)
    m["tunnel_blue"]     = make_cel_material("Mat_TunnelBlue", (0.20, 0.44, 0.78), (0.10, 0.22, 0.44), roughness=0.72, tex_scale=10.0, tex_contrast=0.14)
    m["tunnel_concrete"] = make_natural_rock_material("Mat_TunnelConcrete", (0.36, 0.40, 0.46), (0.58, 0.62, 0.66), (0.72, 0.74, 0.76), (0.24, 0.28, 0.34), macro_scale=0.8, crack_scale=2.2, grain_scale=22.0, z_strata_stretch=1.2, bump_strength=0.28)
    m["pipe_red"]        = make_cel_material("Mat_PipeRed", (0.78, 0.20, 0.16), (0.38, 0.10, 0.12), roughness=0.42, metallic=0.35)
    m["neon_glow"]       = make_cel_material("Mat_NeonGlow", (0.98, 0.96, 0.88), (0.95, 0.92, 0.82), emission_rgb=(1.0, 0.95, 0.84), emission_strength=1.5)
    m["amber_glow"]      = make_cel_material("Mat_AmberGlow", (1.0, 0.76, 0.34), (0.90, 0.64, 0.24), emission_rgb=(1.0, 0.76, 0.32), emission_strength=1.4)
    m["taillight_red"]   = make_cel_material("Mat_TailRed", (0.94, 0.14, 0.12), (0.60, 0.08, 0.08), emission_rgb=(0.98, 0.14, 0.10), emission_strength=1.2)
    m["truck_red"]       = make_cel_material("Mat_TruckRed", (0.76, 0.20, 0.16), (0.34, 0.10, 0.14), roughness=0.32, metallic=0.38)
    m["truck_blue"]      = make_cel_material("Mat_TruckBlue", (0.18, 0.38, 0.64), (0.09, 0.18, 0.36), roughness=0.32, metallic=0.38)
    m["tire_dark"]       = make_cel_material("Mat_TireDark", (0.12, 0.12, 0.15), (0.06, 0.06, 0.10), roughness=0.88)

    # --- LOC 02: Coober Pedy, Australia (Natural Stratified Outback Earth, Wind-Rippled Sand & Sandstone!) ---
    m["desert_sand"]     = make_desert_sand_material("Mat_RedDesertSand")
    m["red_desert"]      = make_natural_rock_material("Mat_RedDesert", (0.50, 0.20, 0.11), (0.76, 0.33, 0.16), (0.88, 0.48, 0.24), (0.46, 0.20, 0.12), shadow_rgb=(0.34, 0.15, 0.14), macro_scale=0.35, crack_scale=1.2, grain_scale=20.0, z_strata_stretch=2.6, bump_strength=0.40)
    m["mullock_white"]   = make_natural_rock_material("Mat_MullockGravel", (0.70, 0.60, 0.48), (0.85, 0.78, 0.66), (0.94, 0.89, 0.80), (0.74, 0.54, 0.38), shadow_rgb=(0.44, 0.36, 0.32), macro_scale=1.2, crack_scale=3.8, grain_scale=28.0, z_strata_stretch=1.3, bump_strength=0.48)
    m["pvc_white"]       = make_cel_material("Mat_PVCWeathered", (0.90, 0.88, 0.83), (0.52, 0.48, 0.48), roughness=0.52, tex_scale=10.0, tex_contrast=0.16, bump_strength=0.12)
    m["rust_metal"]      = make_cel_material("Mat_RustMetal", (0.54, 0.26, 0.14), (0.24, 0.12, 0.10), roughness=0.82, metallic=0.45, tex_scale=14.0, tex_contrast=0.28, bump_strength=0.26)
    m["sandstone_carved"]= make_natural_rock_material("Mat_DugoutSandstone", (0.52, 0.29, 0.16), (0.78, 0.50, 0.30), (0.90, 0.68, 0.44), (0.42, 0.22, 0.14), shadow_rgb=(0.28, 0.16, 0.14), macro_scale=0.65, crack_scale=1.8, grain_scale=24.0, z_strata_stretch=2.1, bump_strength=0.44)
    m["terracotta"]      = make_cel_material("Mat_Terracotta", (0.72, 0.38, 0.24), (0.34, 0.18, 0.14), roughness=0.48, tex_type="brick", tex_scale=5.0, tex_contrast=0.16, bump_strength=0.12)
    m["leather_sofa"]    = make_cel_material("Mat_LeatherSofa", (0.40, 0.21, 0.11), (0.18, 0.09, 0.08), roughness=0.36, tex_scale=16.0, tex_contrast=0.12, bump_strength=0.08)
    m["pillow_teal"]     = make_cel_material("Mat_PillowTeal", (0.20, 0.56, 0.54), (0.09, 0.26, 0.28), roughness=0.86)
    m["pillow_ochre"]    = make_cel_material("Mat_PillowOchre", (0.86, 0.62, 0.22), (0.44, 0.30, 0.12), roughness=0.86)
    m["copper_lamp"]     = make_cel_material("Mat_CopperLamp", (0.82, 0.44, 0.22), (0.36, 0.18, 0.12), roughness=0.24, metallic=0.88)
    m["rug_tribal"]      = make_cel_material("Mat_RugTribal", (0.74, 0.26, 0.18), (0.36, 0.14, 0.14), roughness=0.92, tex_type="brick", tex_scale=14.0, tex_contrast=0.28)
    m["opal_vein"]       = make_opal_iridescent_material("Mat_Opal_Vein")
    m["cactus_green"]    = make_cel_material("Mat_DesertAgave", (0.26, 0.52, 0.30), (0.12, 0.24, 0.18), roughness=0.74)

    # --- LOC 03: Setenil de las Bodegas, Spain (TRUE Natural Limestone Cliff & Stucco!) ---
    m["cliff_rock"]      = make_natural_rock_material("Mat_SetenilCliff", (0.28, 0.22, 0.18), (0.50, 0.42, 0.33), (0.68, 0.56, 0.42), (0.24, 0.28, 0.18), shadow_rgb=(0.16, 0.18, 0.28), macro_scale=0.38, crack_scale=1.35, grain_scale=18.0, z_strata_stretch=2.2, bump_strength=0.58)
    m["white_stucco"]    = make_cel_material("Mat_WhiteStucco", (0.96, 0.94, 0.89), (0.48, 0.54, 0.70), (1.0, 0.96, 0.88), roughness=0.84, tex_scale=20.0, tex_contrast=0.08, bump_strength=0.22)
    m["cobblestone"]     = make_cobblestone_material("Mat_SetenilCobble")
    m["shutter_green"]   = make_cel_material("Mat_ShutterGreen", (0.14, 0.36, 0.22), (0.06, 0.18, 0.15), roughness=0.66, tex_type="wood", tex_scale=16.0)
    m["wrought_iron"]    = make_cel_material("Mat_WroughtIron", (0.11, 0.12, 0.15), (0.05, 0.06, 0.10), roughness=0.44, metallic=0.82)
    m["wicker_tan"]      = make_cel_material("Mat_WickerTan", (0.76, 0.58, 0.34), (0.38, 0.28, 0.18), roughness=0.84, tex_type="brick", tex_scale=28.0, tex_contrast=0.20, bump_strength=0.18)
    m["marble_top"]      = make_cel_material("Mat_MarbleTop", (0.94, 0.92, 0.88), (0.56, 0.58, 0.66), roughness=0.22, tex_scale=8.0, tex_contrast=0.10)
    m["geranium_leaf"]   = make_cel_material("Mat_GeraniumLeaf", (0.16, 0.42, 0.18), (0.08, 0.22, 0.14), roughness=0.70)
    m["geranium_red"]    = make_cel_material("Mat_GeraniumRed", (0.92, 0.14, 0.20), (0.48, 0.08, 0.14), roughness=0.60)
    m["geranium_pink"]   = make_cel_material("Mat_GeraniumPink", (0.94, 0.24, 0.50), (0.48, 0.10, 0.26), roughness=0.60)
    m["table_cloth"]     = make_cel_material("Mat_TableCloth", (0.86, 0.20, 0.18), (0.44, 0.12, 0.16), roughness=0.82, tex_type="brick", tex_scale=22.0, tex_contrast=0.35)
    m["spanish_plate"]   = make_cel_material("Mat_SpanishPlate", (0.18, 0.42, 0.84), (0.09, 0.22, 0.48), roughness=0.20)
    m["tapas_bread"]     = make_cel_material("Mat_TapasBread", (0.86, 0.62, 0.30), (0.46, 0.28, 0.16), roughness=0.78)
    m["laundry_cream"]   = make_cel_material("Mat_LaundryCream", (0.96, 0.91, 0.80), (0.58, 0.52, 0.50), roughness=0.88)
    m["laundry_coral"]   = make_cel_material("Mat_LaundryCoral", (0.88, 0.40, 0.30), (0.46, 0.18, 0.20), roughness=0.88)

    # --- Glass, Volumetric Beams & Signage ---
    m["glass_frosted"]   = make_glass_material("Mat_FrostedGlass", (0.78, 0.90, 0.98), alpha=0.34)
    m["god_ray_gold"]    = make_volumetric_beam_material("Mat_GodRayGold", (1.0, 0.86, 0.52), strength=0.09)
    m["flash_beam"]      = make_volumetric_beam_material("Mat_FlashBeam", (0.76, 0.96, 1.0), strength=0.065)
    m["iced_tea"]        = make_glass_material("Mat_IcedTea", (0.76, 0.40, 0.10), alpha=0.68)
    m["lemon_yellow"]    = make_cel_material("Mat_Lemon", (0.96, 0.86, 0.16), (0.56, 0.48, 0.12), roughness=0.42)

    for key, path in signs.items():
        m[key] = make_sign_material(f"Mat_{key}", path, emission_boost=0.20) if path.exists() else m["wood_warm"]

    m["box_cyan"]   = make_cel_material("Mat_BoxCyan",   (0.18, 0.72, 0.78), (0.08, 0.34, 0.44))
    m["box_yellow"] = make_cel_material("Mat_BoxYellow", (0.94, 0.76, 0.20), (0.52, 0.40, 0.12))
    m["box_coral"]  = make_cel_material("Mat_BoxCoral",  (0.88, 0.32, 0.26), (0.46, 0.14, 0.16))
    m["box_green"]  = make_cel_material("Mat_BoxGreen",  (0.24, 0.68, 0.38), (0.12, 0.34, 0.22))
    return m


# ============================================================================
# LOC_01_Whittier — SLEEK 14-STORY BEGICH TOWERS, PACKED LOBBY & ARCHED TUNNEL
# ============================================================================
def build_loc01_whittier(m: dict[str, bpy.types.Material], root_col: bpy.types.Collection) -> None:
    col_ext = ensure_collection("Whittier_Exterior", root_col)
    col_lob = ensure_collection("Whittier_Lobby", root_col)
    col_tun = ensure_collection("Whittier_Tunnel", root_col)
    col_lgt = ensure_collection("Whittier_Lights", root_col)

    # Expansive Snowy Plaza Ground — STOPS STRICTLY AT Y=9.8 (Begich front facade) so it NEVER Z-fights Lobby_Floor OR slices through the underground School Tunnel!
    make_bevel_box("Whittier_SnowGround", (160.0, 62.0, 0.6), (0.0, -21.2, -0.6), col_ext, m["snow"], bevel=0.0)
    make_bevel_box("Whittier_SnowFlankL", (70.0, 60.0, 0.6), (-43.0, 39.8, -0.6), col_ext, m["snow"], bevel=0.0)
    make_bevel_box("Whittier_SnowFlankR", (70.0, 12.0, 0.6), (43.0, 15.8, -0.6), col_ext, m["snow"], bevel=0.0)
    make_bevel_box("Whittier_Walkway", (4.0, 18.0, 0.04), (0.0, 0.8, -0.02), col_ext, m["begich_concrete"], bevel=0.01)

    # Smooth sculpted snowdrifts flanking walkway
    for side in (-1, 1):
        for idx, (dy, sx, sz) in enumerate([(0.8, 2.3, 0.85), (4.6, 2.6, 1.0), (7.8, 2.0, 0.90), (-3.5, 3.2, 1.05)]):
            make_sculpted_rock(
                f"SnowMound_{side}_{idx}", (sx, 2.1, sz), (side * (4.2 + idx * 0.35), dy, 0.02),
                col_ext, m["snow"], seed=100 + idx * 7 + (1 if side > 0 else 0), subdiv=3, rough=0.16, smooth=True, flatten_bottom=True,
            )
        make_cylinder(f"RailPostA_{side}", 0.04, 1.0, (side * 1.85, 6.2, 0.0), col_ext, m["steel_brushed"], segs=8)
        make_cylinder(f"RailPostB_{side}", 0.04, 1.0, (side * 1.85, 9.0, 0.0), col_ext, m["steel_brushed"], segs=8)
        make_bevel_box(f"RailBar_{side}", (0.06, 2.9, 0.06), (side * 1.85, 7.6, 0.96), col_ext, m["steel_brushed"], bevel=0.01)

    # 1. Craggy Jagged Chugach Glacier Mountain Peaks (Pop-up f=0..18 — authentic sharp alpine ridges!)
    rev_mtn = DYNAMIC_REVEALS["whittier_mtns_popup"]
    mtn_specs = [
        (-36.0, 62.0, 28.0, 22.0, 44.0, 11),
        (-10.0, 74.0, 34.0, 24.0, 56.0, 22),
        (20.0,  72.0, 30.0, 22.0, 50.0, 33),
        (54.0,  58.0, 26.0, 20.0, 40.0, 44),
        (-46.0, 28.0, 20.0, 18.0, 34.0, 55),
    ]
    for idx, (mx, my, sx, sy, sz, sd) in enumerate(mtn_specs):
        mtn = make_craggy_mountain(
            f"Chugach_Peak_{idx}", (sx, sy, sz), (mx, my, -1.5),
            col_ext, m["ice_mountain"], seed=sd,
        )
        animate_buildup(mtn, rev_mtn["start"] + idx * rev_mtn["stagger"], duration=rev_mtn["dur"], mode="POP_UP", offset=(0, 0, 4.0))

    # 2. SLEEK VERTICAL 14-STORY BEGICH TOWERS (W=15.6m x D=10.8m x H=43m — True Vertical Slab Tower!)
    rev_arch = DYNAMIC_REVEALS["begich_tower_arch"]
    make_bevel_box("Begich_Podium_L", (6.4, 1.0, 3.8), (-4.6, 9.8, 0.0), col_ext, m["begich_concrete"], bevel=0.04)
    make_bevel_box("Begich_Podium_R", (6.4, 1.0, 3.8), (4.6, 9.8, 0.0), col_ext, m["begich_concrete"], bevel=0.04)

    # Entrance Canopy, Snow Layer, Pillars & Upright Sign (Staggered snap-in!)
    rev_pr = DYNAMIC_REVEALS["whittier_props_snap"]
    canopy = make_bevel_box("Begich_Canopy", (6.8, 2.7, 0.38), (0.0, 8.6, 3.35), col_ext, m["begich_trim"], bevel=0.04)
    c_snow = make_sculpted_rock("Begich_CanopySnow", (3.3, 1.3, 0.22), (0.0, 0.0, 0.34), col_ext, m["snow"], seed=88, subdiv=3, rough=0.14, smooth=True)
    c_snow.parent = canopy
    for px in (-2.9, 2.9):
        pil = make_cylinder(f"CanopyPillar_{px:.1f}", 0.13, 3.4, (px, -1.1, -3.35), col_ext, m["steel_brushed"], segs=12)
        pil.parent = canopy
    ext_sign = make_sign_plane("Sign_Begich_Ext", 4.3, 0.92, (0.0, -1.42, 0.28), 0.0, col_ext, m["sign_begich_ext"], m["begich_trim"])
    ext_sign.parent = canopy
    animate_buildup(canopy, rev_pr["start"], duration=rev_pr["dur"], mode="POP_UP")

    # Hinged Frosted Glass Double Doors (Swing wide OPEN at f=64..86 as Fajar pushes!)
    for side, s_name in [(-1, "L"), (1, "R")]:
        hinge = bpy.data.objects.new(f"LobbyDoorHinge_{s_name}", None)
        hinge.location = (side * 1.40, 9.6, 0.0)
        link_obj(hinge, col_ext)
        ox = -side * 0.68
        df = make_bevel_box(f"LobbyDoorFrame_{s_name}", (1.36, 0.09, 2.65), (ox, 0.0, 0.0), col_ext, m["steel_brushed"], bevel=0.015)
        dg = make_bevel_box(f"LobbyDoorGlass_{s_name}", (1.14, 0.11, 2.28), (ox, 0.0, 0.22), col_ext, m["glass_frosted"], bevel=0.01)
        dh = make_bevel_box(f"LobbyDoorHandle_{s_name}", (0.06, 0.18, 0.55), (-side * 1.18, -0.06, 1.05), col_ext, m["brass"], bevel=0.01)
        for p in (df, dg, dh):
            p.parent = hinge
        hinge.rotation_euler = (0.0, 0.0, 0.0)
        hinge.keyframe_insert("rotation_euler", frame=64)
        hinge.rotation_euler = (0.0, 0.0, side * math.radians(-105.0))
        hinge.keyframe_insert("rotation_euler", frame=84)
        hinge.keyframe_insert("rotation_euler", frame=110)
        hinge.rotation_euler = (0.0, 0.0, 0.0)
        hinge.keyframe_insert("rotation_euler", frame=132)
        _set_bezier_ease(hinge)

    # Floors 2..14 Vertical Concrete Tower Stack (Tight vertical grid, side fire-escapes, central shaft!)
    rng_w = random.Random(1957)
    for fl in range(13):
        zf = 3.8 + fl * 2.85
        fl_slab = make_bevel_box(f"Begich_Floor_{fl+2:02d}", (15.6, 10.8, 2.82), (0.0, 15.2, zf), col_ext, m["begich_concrete"], bevel=0.04)
        band = make_bevel_box(f"Begich_Band_{fl+2:02d}", (15.9, 11.1, 0.30), (0.0, 0.0, 0.0), col_ext, m["begich_trim"], bevel=0.02)
        band.parent = fl_slab
        # Tight 7-column recessed framed apartment windows across vertical slab!
        for wi in range(7):
            wx = -6.0 + wi * 2.0
            is_lit = rng_w.random() < 0.64
            wf = make_bevel_box(f"BWinF_{fl+2:02d}_{wi}", (1.42, 0.18, 1.56), (wx, -5.42, 0.78), col_ext, m["begich_trim"], bevel=0.02)
            wg = make_bevel_box(f"BWinG_{fl+2:02d}_{wi}", (1.20, 0.22, 1.32), (wx, -5.45, 0.90), col_ext, m["apt_lit"] if is_lit else m["apt_dark"], bevel=0.01)
            wm = make_bevel_box(f"BWinM_{fl+2:02d}_{wi}", (0.07, 0.25, 1.36), (wx, -5.46, 0.88), col_ext, m["begich_trim"], bevel=0.005)
            for p in (wf, wg, wm):
                p.parent = fl_slab
        # Side fire-escape metal balcony platform every 2nd floor!
        if fl % 2 == 0:
            fe = make_bevel_box(f"FireEsc_{fl+2:02d}", (0.95, 2.2, 0.12), (8.25, -1.8, 0.12), col_ext, m["wrought_iron"], bevel=0.01)
            fe.parent = fl_slab
        animate_buildup(fl_slab, rev_arch["start"] + fl * rev_arch["stagger"], duration=rev_arch["dur"], mode="POP_UP", offset=(0, 0, 1.2))

    # Rooftop Penthouse, Snow Parapet & Radio Antenna Array
    pent = make_bevel_box("Begich_Penthouse", (6.2, 5.2, 3.0), (0.0, 15.2, 40.9), col_ext, m["begich_trim"], bevel=0.05)
    mast1 = make_cylinder("Begich_Antenna1", 0.11, 7.2, (-1.2, 0.0, 3.0), col_ext, m["steel_brushed"], segs=8, r_top=0.02)
    mast2 = make_cylinder("Begich_Antenna2", 0.08, 5.0, (1.6, 0.0, 3.0), col_ext, m["steel_brushed"], segs=8, r_top=0.02)
    mast1.parent = pent
    mast2.parent = pent
    animate_buildup(pent, rev_arch["start"] + 28, duration=12, mode="POP_UP")

    # Exterior Rich Set Dressing: Detailed 3D 4x4 Trucks, Snow-Laden Alaskan Pines, Streetlamps, Trash Bins!
    suv_l = build_detailed_vehicle("Whittier_SUV_Blue", (-6.2, 2.4, 0.0), 16.0, col_ext, m["truck_blue"], m["apt_dark"], m["tire_dark"], m["steel_brushed"], m["neon_glow"], m["taillight_red"], m["snow"])
    suv_r = build_detailed_vehicle("Whittier_SUV_Red", (6.4, 3.2, 0.0), -162.0, col_ext, m["truck_red"], m["apt_dark"], m["tire_dark"], m["steel_brushed"], m["neon_glow"], m["taillight_red"], m["snow"])
    animate_buildup(suv_l, rev_pr["start"] + 6, duration=10, mode="POP_UP")
    animate_buildup(suv_r, rev_pr["start"] + 9, duration=10, mode="POP_UP")

    # Moving Snow-Dusted 4x4 Pickup Cruising Snowy Street!
    mov_tr = build_detailed_vehicle("Whittier_MovingTruck", (-14.0, -5.8, 0.0), 0.0, col_ext, m["truck_red"], m["apt_dark"], m["tire_dark"], m["steel_brushed"], m["neon_glow"], m["taillight_red"], m["snow"])
    mov_tr.keyframe_insert("location", frame=0)
    mov_tr.location.x = 16.0
    mov_tr.keyframe_insert("location", frame=95)

    # Snow-Laden Alaskan Spruce Pine Trees & Glowing Streetlamps + Trash Bins!
    for ti, (tx, ty, tsc) in enumerate([(-9.5, 8.0, 1.35), (-11.0, 1.5, 1.15), (9.6, 7.6, 1.40), (11.2, 0.8, 1.10)]):
        tr = build_snowy_pine_tree(f"AlaskanPine_{ti}", (tx, ty, 0.0), tsc, col_ext, m["wood_warm"], m["pine_green"], m["snow"])
        animate_buildup(tr, rev_pr["start"] + 12 + ti * 2, duration=10, mode="POP_UP")
    for li, (lx, ly) in enumerate([(-3.6, 0.2), (3.6, 0.2), (-3.8, -6.5), (3.8, -6.5)]):
        lp = make_cylinder(f"StreetLamp_{li}", 0.09, 4.4, (lx, ly, 0.0), col_ext, m["wrought_iron"], segs=10)
        arm = make_bevel_box(f"LampArm_{li}", (0.85, 0.08, 0.08), (-0.4 * (1 if lx > 0 else -1), 0.0, 4.32), col_ext, m["wrought_iron"], bevel=0.01)
        bulb = make_bevel_box(f"LampHead_{li}", (0.36, 0.24, 0.14), (-0.75 * (1 if lx > 0 else -1), 0.0, 4.22), col_ext, m["amber_glow"], bevel=0.02)
        arm.parent = lp
        bulb.parent = lp
        animate_buildup(lp, rev_pr["start"] + 15 + li * 2, duration=10, mode="POP_UP")
    make_cylinder("Whittier_TrashBin", 0.26, 0.78, (2.7, 6.8, 0.0), col_ext, m["begich_trim"], segs=12)

    # Foreground + Background Slanted Arctic Blizzard Snowflakes (Strictly Y < 8.4 — NEVER leaks into lobby!)
    rng_sn = random.Random(2026)
    for si in range(130):
        sx0 = rng_sn.uniform(-8.5, 8.5)
        sy0 = rng_sn.uniform(-12.0, 8.2)
        sz0 = rng_sn.uniform(0.3, 6.8)
        flk = make_cylinder(f"SnowFlake_{si:03d}", rng_sn.uniform(0.024, 0.052), 0.014, (sx0, sy0, sz0), col_ext, m["snow"], segs=6, pivot_bottom=False)
        flk.keyframe_insert("location", frame=0)
        flk.location = (sx0 + 5.8, sy0, sz0 - 4.4)
        flk.keyframe_insert("location", frame=105)

    # ---- BEGICH TOWERS PACKED WARM GROUND-FLOOR LOBBY (X=-5..5, Y=10..30, Z=0..3.6) ----
    make_bevel_box("Lobby_Floor", (10.4, 21.0, 0.3), (0.0, 20.0, -0.3), col_lob, m["linoleum"], bevel=0.0)
    make_bevel_box("Lobby_Ceiling", (10.4, 21.0, 0.3), (0.0, 20.0, 3.6), col_lob, m["lobby_wall"], bevel=0.0)
    make_bevel_box("Lobby_Wall_L", (0.35, 20.6, 3.7), (-5.0, 20.0, 0.0), col_lob, m["lobby_wall"], bevel=0.02)
    make_bevel_box("Lobby_Wall_R1", (0.35, 12.6, 3.7), (5.0, 16.0, 0.0), col_lob, m["lobby_wall"], bevel=0.02)
    make_bevel_box("Lobby_Wall_R2", (0.35, 4.6, 3.7), (5.0, 28.0, 0.0), col_lob, m["lobby_wall"], bevel=0.02)
    make_bevel_box("Lobby_Wall_R_Top", (0.35, 3.8, 0.95), (5.0, 24.0, 2.75), col_lob, m["lobby_wall"], bevel=0.02)
    make_bevel_box("Lobby_Wall_Back", (10.4, 0.35, 3.7), (0.0, 30.2, 0.0), col_lob, m["lobby_wall"], bevel=0.02)
    # Wood wainscoting + back wall municipal office doors (Police, Mayor, Clinic!)
    make_bevel_box("Lobby_Wainscot_L", (0.12, 20.2, 1.05), (-4.78, 20.0, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    make_bevel_box("Lobby_Wainscot_R1", (0.12, 12.2, 1.05), (4.78, 16.0, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    make_bevel_box("Lobby_Wainscot_Back", (10.0, 0.14, 1.05), (0.0, 29.95, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    for di, dx in enumerate((-1.4, 1.4)):
        d_u = make_bevel_box(f"Lobby_UnitDoor_{di}", (1.18, 0.12, 2.35), (dx, 29.96, 0.0), col_lob, m["wood_warm"], bevel=0.02)
        d_f = make_bevel_box(f"Lobby_UnitFrame_{di}", (1.32, 0.10, 2.45), (dx, 29.98, 0.0), col_lob, m["begich_trim"], bevel=0.02)
        d_pl = make_bevel_box(f"Lobby_UnitPlaque_{di}", (0.45, 0.04, 0.18), (dx, 29.88, 1.72), col_lob, m["brass"], bevel=0.01)
        d_kn = make_cylinder(f"Lobby_UnitKnob_{di}", 0.04, 0.08, (dx + 0.42, 29.85, 1.05), col_lob, m["brass"], segs=8, rot=(math.pi * 0.5, 0, 0), pivot_bottom=False)
    for ly in (12.5, 16.5, 20.5, 24.5, 28.0):
        make_bevel_box(f"Lobby_LightPanel_{ly:.1f}", (2.4, 0.65, 0.08), (0.0, ly, 3.52), col_lob, m["neon_glow"], bevel=0.01)

    # Wet Rubber Mat + Boot Rack + Potted Indoor Plant + Directory Board + Bulletin Board!
    make_bevel_box("Lobby_WetMat", (2.4, 1.3, 0.03), (0.0, 10.9, 0.0), col_lob, m["tire_dark"], bevel=0.01)
    make_bevel_box("Lobby_BootRack", (0.65, 1.8, 0.45), (4.25, 12.2, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    for bi in range(4):
        make_cylinder(f"Lobby_Boot_{bi}", 0.09, 0.28, (4.22, 11.6 + bi * 0.4, 0.45), col_lob, m["tire_dark"], segs=8)
    build_desert_agave("Lobby_Plant_L", (3.6, 29.2, 0.0), col_lob, m["terracotta"], m["pine_green"])
    make_sign_plane("Sign_Directory", 1.55, 2.15, (-4.72, 16.8, 1.68), 90.0, col_lob, m["sign_directory"], m["wood_warm"])
    cork = make_bevel_box("Lobby_CorkBoard", (0.10, 1.8, 1.25), (-4.75, 14.0, 1.25), col_lob, m["wood_warm"], bevel=0.02)
    for fi, (fy, fz, fm) in enumerate([(-0.5, 0.7, m["box_yellow"]), (0.0, 0.8, m["box_cyan"]), (0.45, 0.6, m["box_coral"]), (-0.25, 0.3, m["box_green"]), (0.3, 0.35, m["snow"])]):
        fl_p = make_bevel_box(f"Flyer_{fi}", (0.03, 0.32, 0.38), (0.06, fy, fz), col_lob, fm, bevel=0.005)
        fl_p.parent = cork

    # Brushed-Steel Dual Elevator Bay with Glowing Call Buttons & Floor Indicator!
    make_bevel_box("Elevator_Frame", (0.30, 2.55, 2.78), (-4.78, 25.0, 0.0), col_lob, m["steel_brushed"], bevel=0.03)
    make_bevel_box("Elevator_Recess", (1.2, 2.1, 2.65), (-5.5, 25.0, 0.0), col_lob, m["wood_warm"], bevel=0.02)
    make_bevel_box("Elevator_FloorDisplay", (0.14, 0.72, 0.28), (-4.66, 25.0, 2.88), col_lob, m["amber_glow"], bevel=0.02)
    make_bevel_box("Elevator_CallPanel", (0.08, 0.18, 0.32), (-4.68, 23.45, 1.18), col_lob, m["steel_brushed"], bevel=0.01)
    make_cylinder("Elevator_CallBtn", 0.03, 0.04, (-4.63, 23.45, 1.32), col_lob, m["amber_glow"], segs=8, rot=(0, math.pi * 0.5, 0), pivot_bottom=False)
    ed_l = make_bevel_box("ElevDoor_L", (0.08, 1.04, 2.52), (-4.68, 24.48, 0.0), col_lob, m["steel_brushed"], bevel=0.015)
    ed_r = make_bevel_box("ElevDoor_R", (0.08, 1.04, 2.52), (-4.68, 25.52, 0.0), col_lob, m["steel_brushed"], bevel=0.015)
    for ed, dir_y in [(ed_l, -0.92), (ed_r, 0.92)]:
        oy = ed.location.y
        ed.keyframe_insert("location", frame=360)
        ed.location.y = oy + dir_y
        ed.keyframe_insert("location", frame=382)
        ed.keyframe_insert("location", frame=422)
        ed.location.y = oy
        ed.keyframe_insert("location", frame=444)
        _set_bezier_ease(ed)

    # Post Office Counter + Brass Parcel Scale + Letter Stacks + Parcels + 20 Brass PO Boxes!
    rev_po = DYNAMIC_REVEALS["lobby_post_assembly"]
    po_counter = make_bevel_box("PO_Counter", (1.35, 3.2, 1.08), (-3.85, 27.6, 0.0), col_lob, m["wood_warm"], bevel=0.04)
    po_top = make_bevel_box("PO_CounterTop", (1.48, 3.32, 0.09), (0.0, 0.0, 1.08), col_lob, m["brass"], bevel=0.02)
    po_top.parent = po_counter
    # Postal scale + letter trays + stacked parcels right on counter!
    scale_base = make_bevel_box("PO_ScaleBase", (0.28, 0.28, 0.14), (0.22, -0.85, 1.17), col_lob, m["steel_brushed"], bevel=0.02)
    scale_pan = make_bevel_box("PO_ScalePan", (0.34, 0.34, 0.04), (0.22, -0.85, 1.32), col_lob, m["brass"], bevel=0.01)
    ltr1 = make_bevel_box("PO_Letters1", (0.26, 0.20, 0.12), (0.20, -0.35, 1.17), col_lob, m["snow"], bevel=0.01)
    parc1 = make_bevel_box("PO_Parcel1", (0.42, 0.34, 0.28), (0.15, 0.72, 1.17), col_lob, m["tapas_bread"], bevel=0.02)
    parc2 = make_bevel_box("PO_Parcel2", (0.30, 0.28, 0.22), (0.15, 0.72, 1.45), col_lob, m["box_cyan"], bevel=0.02)
    for pr in (scale_base, scale_pan, ltr1, parc1, parc2):
        pr.parent = po_counter
    animate_buildup(po_counter, rev_po["start"], duration=rev_po["dur"], mode="POP_UP")

    po_sign = make_sign_plane("Sign_PostOffice", 2.8, 0.68, (-3.65, 27.6, 2.68), 90.0, col_lob, m["sign_post_office"], m["wood_warm"])
    animate_buildup(po_sign, rev_po["start"] + 4, duration=10, mode="SLIDE_IN", offset=(0, 0, 0.8))

    po_boxes = make_bevel_box("PO_BoxWall", (0.28, 2.4, 1.55), (-4.70, 27.6, 1.05), col_lob, m["brass"], bevel=0.02)
    for r in range(4):
        for c_i in range(5):
            bx = make_bevel_box(f"POBox_{r}_{c_i}", (0.05, 0.38, 0.28), (0.15, -0.92 + c_i * 0.46, 0.14 + r * 0.35), col_lob, m["steel_brushed"], bevel=0.01)
            bx.parent = po_boxes
    animate_buildup(po_boxes, rev_po["start"] + 8, duration=10, mode="SLIDE_IN", offset=(-0.6, 0, 0))

    # Hero 3D Prop: Pak Arthur's "WHITTIER" Ceramic Coffee Mug!
    mug = make_cylinder("Prop_Whittier_Mug", 0.052, 0.11, (-2.5, 26.0, 0.95), col_lob, m["snow"], segs=12)
    mug_h = make_bevel_box("Prop_MugHandle", (0.04, 0.02, 0.065), (0.055, 0.0, 0.022), col_lob, m["snow"], bevel=0.006)
    mug_h.parent = mug

    # "KOZY KORNER" Minimarket Storefront & Colorful Shelves (Staggered Assembly!)
    rev_mart = DYNAMIC_REVEALS["lobby_mart_assembly"]
    mart_sign = make_sign_plane("Sign_KozyKorner", 3.4, 0.90, (4.70, 19.6, 2.88), -90.0, col_lob, m["sign_kozy_korner"], m["wood_warm"])
    animate_buildup(mart_sign, rev_mart["start"], duration=10, mode="SLIDE_IN", offset=(0, 0, 0.8))
    shelf = make_bevel_box("Kozy_Shelf", (0.78, 3.6, 2.15), (4.35, 19.6, 0.0), col_lob, m["wood_warm"], bevel=0.03)
    prod_mats = [m["box_coral"], m["box_cyan"], m["box_yellow"], m["box_green"], m["truck_blue"]]
    for row_z in (0.45, 0.95, 1.45, 1.90):
        for pi in range(9):
            pr = make_bevel_box(f"MartProd_{row_z:.2f}_{pi}", (0.28, 0.28, 0.32), (-0.20, -1.55 + pi * 0.38, row_z), col_lob, prod_mats[(pi + int(row_z * 10)) % len(prod_mats)], bevel=0.02)
            pr.parent = shelf
    animate_buildup(shelf, rev_mart["start"] + 5, duration=12, mode="POP_UP")

    tun_entry_sign = make_sign_plane("Sign_ToSchoolTunnel", 2.5, 0.65, (4.72, 24.0, 2.98), -90.0, col_lob, m["sign_school_tunnel"], m["tunnel_blue"])
    animate_buildup(tun_entry_sign, DYNAMIC_REVEALS["tunnel_sign_popup"]["start"], duration=12, mode="POP_UP")

    # ---- WHITTIER UNDERGROUND CURVED ARCHED SCHOOL TUNNEL (X=5..45, Y=24, Z=0..-2.4) ----
    for si in range(12):
        make_bevel_box(f"TunnelStep_{si:02d}", (0.60, 3.8, 0.24), (5.25 + si * 0.55, 24.0, -0.20 * (si + 1)), col_tun, m["tunnel_concrete"], bevel=0.015)
    make_bevel_box("StairWall_N", (7.4, 0.35, 5.8), (8.4, 26.0, -2.6), col_tun, m["tunnel_blue"], bevel=0.02)
    make_bevel_box("StairWall_S", (7.4, 0.35, 5.8), (8.4, 22.0, -2.6), col_tun, m["tunnel_blue"], bevel=0.02)
    make_bevel_box("StairRoof", (7.8, 4.4, 0.35), (8.4, 24.0, 2.3), col_tun, m["tunnel_concrete"], rot=(0.0, math.radians(18.0), 0.0), bevel=0.02)

    make_bevel_box("Tunnel_Floor", (35.0, 4.6, 0.35), (29.0, 24.0, -2.75), col_tun, m["tunnel_concrete"], bevel=0.0)
    for side, wy in [("S", 21.85), ("N", 26.15)]:
        make_bevel_box(f"Tunnel_DadoY_{side}", (35.0, 0.35, 1.30), (29.0, wy, -2.4), col_tun, m["tunnel_yellow"], bevel=0.02)
        make_bevel_box(f"Tunnel_StripeB_{side}", (35.0, 0.38, 0.30), (29.0, wy, -1.10), col_tun, m["tunnel_blue"], bevel=0.01)
        # Side Steel Handrail running the full length of the School Tunnel!
        ry = 22.12 if side == "S" else 25.88
        make_cylinder(f"Tunnel_Handrail_{side}", 0.035, 32.0, (28.0, ry, -1.42), col_tun, m["steel_brushed"], segs=8, rot=(0.0, math.pi * 0.5, 0.0), pivot_bottom=False)
    # TRUE CURVED SEMI-CYLINDRICAL VAULTED CONCRETE ROOF!
    make_curved_tunnel_arch("Tunnel_VaultArch", 35.0, 4.3, -0.82, 2.05, (29.0, 24.0, 0.0), col_tun, m["tunnel_concrete"], segs=18)

    # Overhead Red & Yellow Heating Pipes + Caged Industrial Neon Ceiling Lamps + Overhead Sign!
    make_cylinder("Tunnel_PipeRed", 0.10, 34.0, (29.0, 22.7, 0.72), col_tun, m["pipe_red"], segs=10, rot=(0.0, math.pi * 0.5, 0.0), pivot_bottom=False)
    make_cylinder("Tunnel_PipeYel", 0.08, 34.0, (29.0, 23.0, 0.80), col_tun, m["tunnel_yellow"], segs=10, rot=(0.0, math.pi * 0.5, 0.0), pivot_bottom=False)
    make_sign_plane("Sign_InsideTunnel", 2.2, 0.55, (31.5, 24.0, 0.38), -90.0, col_tun, m["sign_school_tunnel"], m["tunnel_blue"])
    for rx in range(13, 42, 4):
        make_bevel_box(f"TunnelRib_S_{rx}", (0.34, 0.22, 1.75), (float(rx), 22.10, -2.4), col_tun, m["tunnel_blue"], bevel=0.02)
        make_bevel_box(f"TunnelRib_N_{rx}", (0.34, 0.22, 1.75), (float(rx), 25.90, -2.4), col_tun, m["tunnel_blue"], bevel=0.02)
        # Caged Neon Tube Fixture!
        lamp = make_bevel_box(f"TunnelLamp_{rx}", (1.35, 0.26, 0.09), (float(rx) + 2.0, 24.0, 1.04), col_tun, m["neon_glow"], bevel=0.01)
        for cx in (-0.55, 0.0, 0.55):
            cage = make_bevel_box(f"TunnelCage_{rx}_{cx:.1f}", (0.04, 0.32, 0.15), (cx, 0.0, -0.02), col_tun, m["wrought_iron"], bevel=0.005)
            cage.parent = lamp

    # Heavy Industrial Steel Emergency Bulkhead Door at Tunnel Far End (with push-bar & porthole — NO black hole!)
    make_bevel_box("TunnelBulkhead_L", (0.55, 1.15, 3.6), (38.2, 22.42, -2.4), col_tun, m["steel_brushed"], bevel=0.03)
    make_bevel_box("TunnelBulkhead_R", (0.55, 1.15, 3.6), (38.2, 25.58, -2.4), col_tun, m["steel_brushed"], bevel=0.03)
    make_bevel_box("TunnelBulkhead_Top", (0.55, 4.3, 0.9), (38.2, 24.0, 0.25), col_tun, m["steel_brushed"], bevel=0.03)
    # Swinging steel emergency door opened partway toward school side so camera dives cleanly past it!
    st_door = make_bevel_box("TunnelSteelDoor", (0.14, 1.85, 2.55), (39.1, 25.1, -2.4), col_tun, m["begich_trim"], rot=(0.0, 0.0, math.radians(62.0)), bevel=0.02)
    pushbar = make_bevel_box("SteelDoor_PushBar", (0.08, 1.35, 0.12), (-0.10, 0.0, 1.05), col_tun, m["brass"], bevel=0.01)
    porthole = make_cylinder("SteelDoor_Porthole", 0.22, 0.18, (0.0, 0.0, 1.78), col_tun, m["glass_frosted"], segs=12, rot=(0.0, math.pi * 0.5, 0.0), pivot_bottom=False)
    pushbar.parent = st_door
    porthole.parent = st_door
    make_bevel_box("Tunnel_ExitGlowBack", (0.3, 4.6, 4.0), (45.2, 24.0, -2.4), col_tun, m["neon_glow"], bevel=0.0)

    # ---- WHITTIER LOCALIZED LIGHTS (Strictly inside LOC_01_Whittier!) ----
    def _lgt(name, ltype, loc, rot_deg, energy, color, size=1.0):
        ld = bpy.data.lights.new(name=name, type=ltype)
        ld.energy = energy
        ld.color = color
        if ltype == "AREA": ld.size = size
        elif ltype == "POINT": ld.shadow_soft_size = size
        elif ltype == "SUN": ld.angle = math.radians(4.5)
        o = bpy.data.objects.new(name, ld)
        o.location = loc
        o.rotation_euler = tuple(math.radians(a) for a in rot_deg)
        return link_obj(o, col_lgt)

    _lgt("Whittier_ArcticSun", "SUN", (-15.0, -25.0, 28.0), (58.0, 0.0, -26.0), 2.8, (0.82, 0.90, 1.0))
    _lgt("Whittier_ExtKey", "AREA", (-6.0, -7.0, 9.0), (50.0, 0.0, -26.0), 420.0, (0.78, 0.89, 1.0), size=9.0)
    for ly in (13.0, 19.0, 25.0, 28.0):
        _lgt(f"Whittier_LobbyLamp_{ly:.0f}", "POINT", (0.0, ly, 3.15), (0, 0, 0), 220.0, (1.0, 0.86, 0.65), size=0.6)
    for lx in (10.0, 16.0, 22.0, 28.0, 34.0, 40.0):
        _lgt(f"Whittier_TunnelLamp_{lx:.0f}", "POINT", (lx, 24.0, 0.35), (0, 0, 0), 260.0, (0.95, 0.98, 1.0), size=0.55)


# ============================================================================
# LOC_02_CooberPedy — ENDLESS OUTBACK DESERT, MULLOCK HEAPS, RIG & SANDSTONE DUGOUT
# ============================================================================
def build_loc02_coober_pedy(m: dict[str, bpy.types.Material], root_col: bpy.types.Collection) -> None:
    col_des = ensure_collection("CooberPedy_Desert", root_col)
    col_dug = ensure_collection("CooberPedy_Dugout", root_col)
    col_lgt = ensure_collection("CooberPedy_Lights", root_col)

    # Endless 320m Red Ochre Desert Horizon (wind-rippled smooth Outback sand, stops cleanly at dugout wall Y=17.2!)
    make_bevel_box("Desert_Floor_Main", (320.0, 160.0, 0.6), (100.0, -62.8, -0.6), col_des, m["desert_sand"], bevel=0.0)
    make_bevel_box("Desert_Floor_FarBack", (320.0, 140.0, 0.6), (100.0, 108.0, -0.6), col_des, m["desert_sand"], bevel=0.0)
    make_bevel_box("Desert_Floor_FarL", (140.0, 40.0, 0.6), (22.0, 28.0, -0.6), col_des, m["desert_sand"], bevel=0.0)
    make_bevel_box("Desert_Floor_FarR", (140.0, 40.0, 0.6), (178.0, 28.0, -0.6), col_des, m["desert_sand"], bevel=0.0)

    # Distant Stratified Australian Outback Mesas on Far Horizon (framed cleanly under Nishita Outback sky!)
    for mi, (mx, my, sx, sy, sz) in enumerate([(42.0, 68.0, 28, 16, 10), (105.0, 88.0, 36, 18, 11), (168.0, 62.0, 30, 16, 10), (146.0, 28.0, 20, 14, 7)]):
        make_sculpted_rock(f"OutbackMesa_{mi}", (sx, sy, sz), (mx, my, -0.5), col_des, m["red_desert"], seed=410 + mi, subdiv=3, rough=0.18, stratify=0.12, smooth=True, flatten_bottom=True)

    # 1. Compact Low Stratified Red Sandstone Cave Hill (leaves vast Outback sky & horizon open above!)
    rev_hill = DYNAMIC_REVEALS["coober_hill_popup"]
    hill_objs = [
        make_sculpted_rock("DugoutHill_L", (6.5, 8.2, 3.3), (87.8, 24.5, 0.0), col_des, m["red_desert"], seed=301, subdiv=4, rough=0.22, stratify=0.10, smooth=True, flatten_bottom=True),
        make_sculpted_rock("DugoutHill_R", (6.5, 8.2, 3.4), (112.2, 24.5, 0.0), col_des, m["red_desert"], seed=302, subdiv=4, rough=0.22, stratify=0.10, smooth=True, flatten_bottom=True),
        make_sculpted_rock("DugoutHill_Top", (9.8, 9.2, 1.8), (100.0, 25.5, 4.4), col_des, m["red_desert"], seed=303, subdiv=4, rough=0.18, stratify=0.08, smooth=True),
        make_sculpted_rock("CaveRock_L1", (3.2, 2.2, 2.4), (95.0, 16.0, 0.0), col_des, m["red_desert"], seed=311, subdiv=4, rough=0.24, stratify=0.10, smooth=True, flatten_bottom=True),
        make_sculpted_rock("CaveRock_R1", (3.2, 2.2, 2.5), (105.0, 16.0, 0.0), col_des, m["red_desert"], seed=312, subdiv=4, rough=0.24, stratify=0.10, smooth=True, flatten_bottom=True),
        make_sculpted_rock("CaveRock_Top1", (5.2, 2.2, 1.15), (100.0, 16.2, 3.5), col_des, m["red_desert"], seed=313, subdiv=4, rough=0.20, stratify=0.09, smooth=True),
    ]
    for hi, ho in enumerate(hill_objs):
        animate_buildup(ho, rev_hill["start"] + hi * 2, duration=rev_hill["dur"], mode="POP_UP", offset=(0, 0, 2.5))

    make_bevel_box("CaveFacade_L", (6.4, 2.0, 4.4), (95.4, 16.8, 0.0), col_des, m["red_desert"], bevel=0.22)
    make_bevel_box("CaveFacade_R", (6.4, 2.0, 4.4), (104.6, 16.8, 0.0), col_des, m["red_desert"], bevel=0.22)
    make_bevel_box("CaveFacade_Top", (15.6, 2.2, 1.9), (100.0, 16.8, 2.85), col_des, m["red_desert"], bevel=0.22)

    # Heavy Timber Door Frame + Studded Hinged Wooden Cave Door (Swings OPEN at f=1046..1078!)
    make_bevel_box("CaveTimber_L", (0.28, 0.45, 2.9), (98.8, 15.7, 0.0), col_des, m["wood_warm"], bevel=0.03)
    make_bevel_box("CaveTimber_R", (0.28, 0.45, 2.9), (101.2, 15.7, 0.0), col_des, m["wood_warm"], bevel=0.03)
    make_bevel_box("CaveTimber_Top", (2.8, 0.48, 0.30), (100.0, 15.7, 2.78), col_des, m["wood_warm"], bevel=0.03)
    door_hinge = bpy.data.objects.new("CaveDoorHinge", None)
    door_hinge.location = (98.95, 15.75, 0.0)
    link_obj(door_hinge, col_des)
    door_leaf = make_bevel_box("CaveWoodDoor", (2.10, 0.16, 2.74), (1.05, 0.0, 0.0), col_des, m["wood_warm"], bevel=0.025)
    door_strap1 = make_bevel_box("CaveDoorStrap1", (1.92, 0.19, 0.12), (1.05, 0.0, 2.18), col_des, m["wrought_iron"], bevel=0.01)
    door_strap2 = make_bevel_box("CaveDoorStrap2", (1.92, 0.19, 0.12), (1.05, 0.0, 0.52), col_des, m["wrought_iron"], bevel=0.01)
    door_ring = make_cylinder("CaveDoorHandle", 0.08, 0.10, (1.82, -0.10, 1.25), col_des, m["brass"], segs=10, rot=(math.pi * 0.5, 0, 0), pivot_bottom=False)
    for p in (door_leaf, door_strap1, door_strap2, door_ring):
        p.parent = door_hinge
    door_hinge.rotation_euler = (0.0, 0.0, 0.0)
    door_hinge.keyframe_insert("rotation_euler", frame=1046)
    door_hinge.rotation_euler = (0.0, 0.0, math.radians(108.0))
    door_hinge.keyframe_insert("rotation_euler", frame=1078)
    door_hinge.keyframe_insert("rotation_euler", frame=1115)
    _set_bezier_ease(door_hinge)

    # Authentic Multi-Blade Desert Agave Pots flanking Cave Door!
    build_desert_agave("DesertAgave_L", (98.0, 14.9, 0.0), col_des, m["terracotta"], m["cactus_green"])
    build_desert_agave("DesertAgave_R", (102.0, 14.9, 0.0), col_des, m["terracotta"], m["cactus_green"])

    # 2. Asymmetric Sculpted Rough Gravel Mullock Heaps + Loose Scatter Rocks (NO smooth pudding cones!)
    rev_pipes = DYNAMIC_REVEALS["desert_pipes_wave"]
    mullocks = [
        (91.5, 4.2, 3.8, 3.0, 2.3), (109.2, 5.2, 4.4, 3.4, 2.7), (85.5, 10.5, 5.0, 4.0, 3.2),
        (114.5, 11.5, 5.2, 4.2, 3.4), (93.5, -4.5, 3.4, 2.8, 1.9), (108.5, -3.2, 3.8, 3.2, 2.2),
        (80.5, -6.0, 5.6, 4.6, 3.6), (121.0, 2.5, 5.8, 4.8, 3.8),
    ]
    for idx, (mx, my, sx, sy, sz) in enumerate(mullocks):
        mh = make_sculpted_rock(
            f"MullockHeap_{idx}", (sx, sy, sz), (mx, my, 0.0),
            col_des, m["mullock_white"], seed=350 + idx, subdiv=4, rough=0.30, stratify=0.04, smooth=True, flatten_bottom=True,
        )
        animate_buildup(mh, rev_pipes["start"] + idx * 2, duration=12, mode="POP_UP", offset=(0, 0, 1.2))
    # Scattered Outback Desert Rocks blending hillside & mullocks naturally into red dirt!
    rng_rk = random.Random(404)
    for rki in range(28):
        rx = rng_rk.uniform(86.0, 114.0)
        ry = rng_rk.uniform(-6.0, 14.5)
        if abs(rx - 100.0) < 2.2 and ry > 9.0:
            continue
        make_sculpted_rock(
            f"DesertRock_{rki:02d}", (rng_rk.uniform(0.22, 0.65), rng_rk.uniform(0.20, 0.55), rng_rk.uniform(0.14, 0.38)),
            (rx, ry, 0.0), col_des, m["red_desert"] if rki % 3 else m["mullock_white"],
            seed=500 + rki, subdiv=2, rough=0.28, smooth=True, flatten_bottom=True,
        )

    # Hero Vent Pipe at (100, 2.0) — Match-Cut Portal with weathered dirt collar, rust rim & rain cap (cap hides only on f<=846)!
    hp_pipe = make_cylinder("HeroVentPipe_Rim", 0.28, 1.25, (100.0, 2.0, 0.0), col_des, m["pvc_white"], segs=16)
    hp_dirt = make_sculpted_rock("HeroVentPipe_Dirt", (0.50, 0.50, 0.22), (0.0, 0.0, 0.0), col_des, m["red_desert"], seed=609, subdiv=2, rough=0.25, smooth=True, flatten_bottom=True)
    hp_band = make_cylinder("HeroVentPipe_Band", 0.295, 0.16, (0.0, 0.0, 1.08), col_des, m["rust_metal"], segs=16)
    hp_dirt.parent = hp_pipe
    hp_band.parent = hp_pipe
    hp_cap = make_cylinder("HeroVentPipe_Cap", 0.42, 0.18, (100.0, 2.0, 1.32), col_des, m["rust_metal"], segs=16, r_top=0.04)
    for ang_d in (0, 120, 240):
        rad = math.radians(ang_d)
        st = make_cylinder(f"HeroVentStrut_{ang_d}", 0.018, 0.16, (math.cos(rad) * 0.22, math.sin(rad) * 0.22, -0.10), col_des, m["wrought_iron"], segs=6)
        st.parent = hp_cap

    # 20 Detailed Weathered White Vent Pipes (dirt collar, rust mesh ring, 3 struts, metal rain-cap!)
    pipe_coords = [
        (96.6, 4.6, 1.45), (103.4, 4.8, 1.65), (94.2, 8.0, 1.55), (105.8, 8.4, 1.75),
        (97.8, 9.8, 1.35), (102.8, 10.6, 1.55), (91.5, 6.2, 1.75), (108.5, 6.6, 1.60),
        (90.0, 11.8, 1.85), (110.2, 12.4, 1.70), (95.5, 1.4, 1.35), (104.5, 1.8, 1.50),
        (93.2, 13.8, 1.60), (107.0, 14.0, 1.50), (88.0, 4.2, 1.80), (112.0, 4.0, 1.70),
        (98.5, 17.5, 1.75), (101.8, 18.2, 1.60), (95.0, 19.0, 1.70), (105.0, 19.2, 1.80),
    ]
    for idx, (px, py, ph) in enumerate(pipe_coords):
        pz = 3.8 if py > 16.5 else 0.0
        pipe = make_cylinder(f"VentPipe_{idx:02d}", 0.16, ph, (px, py, pz), col_des, m["pvc_white"], segs=14)
        collar = make_sculpted_rock(f"VentDirt_{idx:02d}", (0.34, 0.34, 0.18), (0.0, 0.0, 0.0), col_des, m["red_desert"], seed=610 + idx, subdiv=2, rough=0.25, smooth=True, flatten_bottom=True)
        mesh_band = make_cylinder(f"VentMesh_{idx:02d}", 0.168, 0.18, (0.0, 0.0, ph - 0.18), col_des, m["rust_metal"], segs=12)
        cap = make_cylinder(f"VentCap_{idx:02d}", 0.28, 0.16, (0.0, 0.0, ph + 0.06), col_des, m["rust_metal"], segs=14, r_top=0.03)
        for ang_d in (0, 120, 240):
            rad = math.radians(ang_d)
            st = make_cylinder(f"VentStrut_{idx:02d}_{ang_d}", 0.014, 0.14, (math.cos(rad) * 0.13, math.sin(rad) * 0.13, ph - 0.04), col_des, m["wrought_iron"], segs=6)
            st.parent = pipe
        for p in (collar, mesh_band, cap):
            p.parent = pipe
        animate_buildup(pipe, rev_pipes["start"] + idx * rev_pipes["stagger"], duration=rev_pipes["dur"], mode="POP_UP")

    # Open Mine Shaft surrounded by Timber-Post Wire Warning Fence + Large Rusted "DANGER: OPEN SHAFTS" Sign!
    make_sculpted_rock("OpenShaft_Mound", (1.35, 1.25, 0.42), (103.0, 8.6, 0.0), col_des, m["mullock_white"], seed=388, subdiv=3, rough=0.25, smooth=True, flatten_bottom=True)
    make_cylinder("OpenShaft_Hole", 0.72, 0.45, (103.0, 8.6, 0.02), col_des, m["tire_dark"], segs=16)
    fence_pts = [(101.8, 7.6), (104.2, 7.6), (104.2, 9.6), (101.8, 9.6)]
    for fi, (fx, fy) in enumerate(fence_pts):
        fp = make_cylinder(f"ShaftFencePost_{fi}", 0.06, 1.05, (fx, fy, 0.0), col_des, m["wood_warm"], segs=8)
        animate_buildup(fp, DYNAMIC_REVEALS["danger_sign_popup"]["start"] - 4 + fi, duration=10, mode="POP_UP")
    for w_z in (0.45, 0.85):
        make_cylinder(f"FenceWireF_{w_z:.2f}", 0.015, 2.4, (103.0, 7.6, w_z), col_des, m["rust_metal"], segs=6, rot=(0, math.pi * 0.5, 0), pivot_bottom=False)
        make_cylinder(f"FenceWireL_{w_z:.2f}", 0.015, 2.0, (101.8, 8.6, w_z), col_des, m["rust_metal"], segs=6, rot=(math.pi * 0.5, 0, 0), pivot_bottom=False)
    danger_root = make_cylinder("DangerSign_Post", 0.08, 1.65, (101.4, 8.0, 0.0), col_des, m["wood_warm"], segs=8)
    d_board = make_sign_plane("Sign_DangerShafts", 1.15, 1.15, (0.0, -0.09, 1.56), -18.0, col_des, m["sign_danger_shafts"], m["rust_metal"])
    d_board.parent = danger_root
    animate_buildup(danger_root, DYNAMIC_REVEALS["danger_sign_popup"]["start"], duration=12, mode="POP_UP")

    # Authentic Weathered Opal Drilling Rig Derrick (clearly visible silhouette on left Outback horizon!) + Cruising 4x4 Ute!
    rig_root = bpy.data.objects.new("Outback_DrillRig", None)
    rig_root.location = (92.8, 17.8, 0.0)
    link_obj(rig_root, col_des)
    rb = make_bevel_box("Rig_TruckBed", (4.6, 2.1, 0.9), (0, 0, 0.5), col_des, m["rust_metal"], bevel=0.05)
    rb.parent = rig_root
    for leg_x in (-0.8, 0.8):
        for leg_y in (-0.6, 0.6):
            lg = make_cylinder(f"RigLeg_{leg_x:.1f}_{leg_y:.1f}", 0.08, 7.5, (leg_x, leg_y, 1.2), col_des, m["rust_metal"], segs=6, rot=(leg_y * 0.14, -leg_x * 0.14, 0))
            lg.parent = rig_root
    for wx in (-1.5, 1.5):
        for wy in (-1.05, 1.05):
            wh = make_cylinder(f"RigWh_{wx:.1f}_{wy:.1f}", 0.52, 0.34, (wx, wy, 0.52), col_des, m["tire_dark"], segs=12, rot=(math.pi * 0.5, 0, 0), pivot_bottom=False)
            wh.parent = rig_root
    animate_buildup(rig_root, DYNAMIC_REVEALS["danger_sign_popup"]["start"] - 6, duration=12, mode="POP_UP")

    outback_ute = build_detailed_vehicle("Coober_OutbackUte", (74.0, 26.5, 4.4), 0.0, col_des, m["mullock_white"], m["apt_dark"], m["tire_dark"], m["steel_brushed"], m["neon_glow"], m["taillight_red"])
    outback_ute.keyframe_insert("location", frame=836)
    outback_ute.location.x = 126.0
    outback_ute.keyframe_insert("location", frame=1080)

    # ---- COOBER PEDY CARVED SANDSTONE DUGOUT LIVING ROOM (X=94.5..105.5, Y=18..34, Z=0..3.4) ----
    make_bevel_box("Dugout_Floor", (11.5, 19.0, 0.35), (100.0, 25.5, -0.35), col_dug, m["terracotta"], bevel=0.0)
    make_bevel_box("Dugout_Wall_L", (0.7, 17.5, 3.6), (94.6, 26.2, 0.0), col_dug, m["sandstone_carved"], bevel=0.20)
    make_bevel_box("Dugout_Wall_R", (0.7, 17.5, 3.6), (105.4, 26.2, 0.0), col_dug, m["sandstone_carved"], bevel=0.20)
    make_bevel_box("Dugout_Wall_Back", (11.4, 0.7, 3.6), (100.0, 34.4, 0.0), col_dug, m["sandstone_carved"], bevel=0.20)
    make_bevel_box("Dugout_Ceiling", (11.6, 19.0, 0.6), (100.0, 25.5, 3.35), col_dug, m["sandstone_carved"], bevel=0.20)
    # Organic sculpted sandstone ceiling buttresses & carved recessed archway alcoves!
    for dy in (20.5, 24.5, 28.5, 32.5):
        make_sculpted_rock(f"DugoutRibL_{dy:.0f}", (0.75, 1.5, 1.7), (95.1, dy, 2.8), col_dug, m["sandstone_carved"], seed=int(dy) + 10, subdiv=3, rough=0.16, smooth=True)
        make_sculpted_rock(f"DugoutRibR_{dy:.0f}", (0.75, 1.5, 1.7), (104.9, dy, 2.8), col_dug, m["sandstone_carved"], seed=int(dy) + 30, subdiv=3, rough=0.16, smooth=True)
    # Glowing carved sandstone hallway arch on far back-left leading into deeper underground rooms!
    make_bevel_box("Dugout_InnerHallFrame", (2.2, 0.55, 2.65), (96.8, 33.9, 0.0), col_dug, m["sandstone_carved"], bevel=0.20)
    make_bevel_box("Dugout_InnerHallGlow", (1.45, 0.20, 2.18), (96.8, 34.05, 0.0), col_dug, m["amber_glow"], bevel=0.12)

    # Interior Pop-Up / Assembly as Camera Enters Dugout (f=1094..1144)!
    rev_dug = DYNAMIC_REVEALS["dugout_furniture_asm"]
    rug = make_bevel_box("Dugout_TribalRug", (4.2, 2.8, 0.03), (99.4, 26.8, 0.0), col_dug, m["rug_tribal"], bevel=0.01)
    animate_buildup(rug, rev_dug["start"], duration=10, mode="POP_UP")

    # Coffee Table + Sleek Frosted Iced Tea Glass, Lemon Wedge & Small Pitcher!
    ctbl = make_bevel_box("Dugout_CoffeeTable", (1.65, 0.92, 0.44), (99.2, 26.4, 0.0), col_dug, m["wood_warm"], bevel=0.03)
    tea_gl = make_cylinder("Prop_IcedTea", 0.048, 0.14, (-0.30, 0.08, 0.44), col_dug, m["iced_tea"], segs=12, r_top=0.058)
    lem = make_cylinder("Prop_LemonSlice", 0.036, 0.012, (-0.26, 0.08, 0.57), col_dug, m["lemon_yellow"], segs=10, rot=(0.0, 0.7, 0.0))
    pitcher = make_cylinder("Prop_TeaPitcher", 0.068, 0.17, (0.28, -0.04, 0.44), col_dug, m["iced_tea"], segs=14, r_top=0.056)
    p_lid = make_cylinder("Prop_PitcherLid", 0.058, 0.02, (0.28, -0.04, 0.61), col_dug, m["copper_lamp"], segs=14)
    for p in (tea_gl, lem, pitcher, p_lid):
        p.parent = ctbl
    animate_buildup(ctbl, rev_dug["start"] + 4, duration=12, mode="POP_UP")

    # Plush Leather Sofa with 3 Soft Rounded Throw Pillows (pushed back 0.25m so Jack's bent knees & boots sit cleanly IN FRONT!)
    sofa = make_bevel_box("Dugout_LeatherSofa", (2.75, 1.02, 0.44), (98.4, 29.05, 0.0), col_dug, m["leather_sofa"], bevel=0.08)
    s_back = make_bevel_box("Sofa_Backrest", (2.75, 0.30, 0.64), (0.0, 0.38, 0.42), col_dug, m["leather_sofa"], bevel=0.08)
    s_back.parent = sofa
    for ax in (-1.26, 1.26):
        arm = make_bevel_box(f"Sofa_Arm_{ax:.1f}", (0.30, 0.98, 0.36), (ax, 0.0, 0.40), col_dug, m["leather_sofa"], bevel=0.06)
        arm.parent = sofa
    for pi, (px, py_p, pmat, yaw_p) in enumerate([(-0.92, 0.14, m["pillow_teal"], 0.22), (0.88, 0.14, m["pillow_ochre"], -0.25), (0.50, 0.16, m["pillow_teal"], 0.12)]):
        pil = make_sculpted_rock(f"Sofa_Pillow_{pi}", (0.24, 0.11, 0.22), (px, py_p, 0.66), col_dug, pmat, seed=720 + pi, subdiv=3, rough=0.04, smooth=True)
        pil.rotation_euler = (-0.18, 0.08 * (pi - 1), yaw_p)
        pil.parent = sofa
    animate_buildup(sofa, rev_dug["start"] + 8, duration=12, mode="POP_UP")

    # Carved Recessed Wall Bookshelf filled with Books, Mineral Samples & Wooden Opal Crate!
    shelf_d = make_bevel_box("Dugout_CarvedAlcove", (0.58, 2.5, 2.25), (104.85, 27.6, 0.25), col_dug, m["wood_warm"], bevel=0.04)
    for bi, bz in enumerate((0.42, 0.94, 1.46, 1.92)):
        pl = make_bevel_box(f"AlcovePlank_{bi}", (0.48, 2.32, 0.06), (-0.08, 0.0, bz - 0.04), col_dug, m["wood_warm"], bevel=0.01)
        pl.parent = shelf_d
        for k in range(6):
            bm_col = [m["box_coral"], m["box_cyan"], m["box_yellow"], m["box_green"], m["truck_blue"], m["opal_vein"]][(bi + k) % 6]
            bk = make_bevel_box(f"DugBook_{bi}_{k}", (0.26, 0.14, 0.30), (-0.10, -0.92 + k * 0.36, bz), col_dug, bm_col, bevel=0.015)
            bk.parent = shelf_d
    crate = make_bevel_box("OpalSampleCrate", (0.65, 0.52, 0.38), (103.7, 27.6, 0.0), col_dug, m["wood_warm"], bevel=0.02)
    for ri in range(4):
        rk = make_sculpted_rock(f"CrateOpal_{ri}", (0.12, 0.10, 0.09), (-0.16 + ri * 0.11, 0.0, 0.42), col_dug, m["opal_vein"], seed=770 + ri, subdiv=1, rough=0.35, smooth=False)
        rk.parent = crate
    animate_buildup(shelf_d, rev_dug["start"] + 12, duration=12, mode="SLIDE_IN", offset=(0.7, 0, 0))
    animate_buildup(crate, rev_dug["start"] + 15, duration=10, mode="POP_UP")

    # Detailed Standing Vintage Electric Fan (Circular Wire Guard + 4 Distinct Stationary Metal Blades = 24°C Gag!)
    fan_root = make_cylinder("Fan_Base", 0.24, 0.06, (96.2, 26.4, 0.0), col_dug, m["steel_brushed"], segs=14)
    f_pole = make_cylinder("Fan_Pole", 0.032, 1.28, (0.0, 0.0, 0.05), col_dug, m["steel_brushed"], segs=10)
    f_hub = make_cylinder("Fan_MotorHub", 0.09, 0.16, (0.0, 0.0, 1.38), col_dug, m["copper_lamp"], segs=12, rot=(math.pi * 0.5, 0, -0.45), pivot_bottom=False)
    f_ring = make_cylinder("Fan_OuterRing", 0.30, 0.05, (0.0, -0.04, 1.38), col_dug, m["wrought_iron"], segs=20, rot=(math.pi * 0.5, 0, -0.45), pivot_bottom=False)
    for p in (f_pole, f_hub, f_ring):
        p.parent = fan_root
    # 4 Distinct Stationary Blades!
    for bi in range(4):
        ang = math.radians(bi * 90.0 + 20.0)
        bld = make_bevel_box(
            f"Fan_Blade_{bi}", (0.10, 0.015, 0.22),
            (math.sin(ang) * 0.14, -0.04, 1.38 + math.cos(ang) * 0.14),
            col_dug, m["steel_brushed"], rot=(0.0, ang, -0.45), bevel=0.004, pivot_bottom=False,
        )
        bld.parent = fan_root
    animate_buildup(fan_root, rev_dug["start"] + 18, duration=10, mode="POP_UP")

    # Framed Opal Mining Map + Hanging Industrial Copper Pendant Lamps!
    make_sign_plane("Sign_OpalMap", 1.75, 1.18, (95.02, 25.0, 1.75), 90.0, col_dug, m["sign_opal_map"], m["wood_warm"])
    for idx_l, (lx, ly) in enumerate([(98.6, 26.8), (102.6, 26.8), (100.2, 30.8)]):
        cord = make_cylinder(f"LampCord_{idx_l}", 0.018, 0.85, (lx, ly, 2.52), col_dug, m["wrought_iron"], segs=6)
        shd = make_cylinder(f"CopperShade_{idx_l}", 0.28, 0.22, (0.0, 0.0, -0.18), col_dug, m["copper_lamp"], segs=14, r_top=0.08)
        blb = make_cylinder(f"LampBulb_{idx_l}", 0.08, 0.09, (0.0, 0.0, -0.24), col_dug, m["neon_glow"], segs=10)
        shd.parent = cord
        blb.parent = cord
        animate_buildup(cord, rev_dug["start"] + 20 + idx_l * 2, duration=10, mode="SLIDE_IN", offset=(0, 0, 1.0))

    # HERO PROP: Sharp Multi-Faceted 3D Rainbow Opal Crystal Cluster + Elena's Focused LED Beam!
    opal_root = bpy.data.objects.new("Hero_OpalVeinCluster", None)
    opal_root.location = (104.92, 30.8, 1.42)
    link_obj(opal_root, col_dug)
    crystal_specs = [
        (0.0, -0.34, -0.06, 0.14, 0.24, 0.18, 0.2),
        (-0.04, 0.0, 0.06, 0.18, 0.34, 0.26, -0.3),
        (-0.02, 0.32, -0.08, 0.15, 0.26, 0.20, 0.4),
        (-0.03, -0.14, -0.24, 0.13, 0.22, 0.16, 0.1),
        (-0.03, 0.16, 0.24, 0.12, 0.20, 0.18, -0.2),
        (-0.06, 0.06, -0.04, 0.16, 0.18, 0.28, 0.5),
    ]
    for oi, (ox, oy, oz, sx, sy, sz, rot_x) in enumerate(crystal_specs):
        cr = make_sculpted_rock(
            f"OpalFacet_{oi}", (sx, sy, sz), (ox, oy, oz),
            col_dug, m["opal_vein"], seed=510 + oi, subdiv=1, rough=0.38, smooth=False,  # Sharp gem crystal facets!
        )
        cr.rotation_euler = (rot_x, 0.2, 0.15 * oi)
        cr.parent = opal_root
    animate_buildup(opal_root, rev_dug["start"] + 26, duration=12, mode="POP_UP")

    # Narrow LED lens at Elena's flashlight hand (103.55, 29.75) widening naturally onto the Opal Crystal Cluster (104.88, 30.78)!
    beam = make_cylinder(
        "Prop_Elena_FlashBeam", 0.30, 1.55, (104.22, 30.26, 1.40), col_dug, m["flash_beam"],
        segs=18, r_top=0.035, rot=(math.radians(90.0), 0.0, math.radians(-50.0)), pivot_bottom=False,
    )
    beam.visible_shadow = False

    # ---- COOBER PEDY LOCALIZED LIGHTS (Strictly inside LOC_02_CooberPedy!) ----
    def _lgt(name, ltype, loc, rot_deg, energy, color, size=1.0, spot_deg=38.0):
        ld = bpy.data.lights.new(name=name, type=ltype)
        ld.energy = energy
        ld.color = color
        if ltype == "AREA": ld.size = size
        elif ltype == "POINT": ld.shadow_soft_size = size
        elif ltype == "SPOT":
            ld.spot_size = math.radians(spot_deg)
            ld.spot_blend = 0.45
            ld.shadow_soft_size = size
        elif ltype == "SUN": ld.angle = math.radians(1.5)
        o = bpy.data.objects.new(name, ld)
        o.location = loc
        o.rotation_euler = tuple(math.radians(a) for a in rot_deg)
        return link_obj(o, col_lgt)

    _lgt("Coober_OutbackSun", "SUN", (105.0, -15.0, 30.0), (42.0, 0.0, -32.0), 4.8, (1.0, 0.90, 0.72))
    for lx, ly in [(98.6, 26.8), (102.4, 26.8), (100.2, 30.6)]:
        _lgt(f"Coober_DugoutLamp_{lx:.0f}_{ly:.0f}", "POINT", (lx, ly, 2.25), (0, 0, 0), 240.0, (1.0, 0.78, 0.52), size=0.5)
    _lgt("Light_Elena_Flashlight", "SPOT", (103.3, 29.5, 1.38), (88.0, 0.0, -52.0), 340.0, (0.72, 0.95, 1.0), size=0.14, spot_deg=38.0)


# ============================================================================
# LOC_03_Setenil — CALLE CUEVAS DEL SOL, NATURAL LIMESTONE OVERHANG & BAR LA ROCA
# ============================================================================
def build_loc03_setenil(m: dict[str, bpy.types.Material], root_col: bpy.types.Collection) -> None:
    col_st = ensure_collection("Setenil_Street", root_col)
    col_bl = ensure_collection("Setenil_Balcony", root_col)
    col_lgt = ensure_collection("Setenil_Lights", root_col)

    # 1. Cobblestone Street Unrolling Forward (f=1520..1532, extended far past bridge arch!)
    st_road = make_bevel_box("Setenil_CobbleStreet", (16.0, 82.0, 0.4), (200.0, 28.0, -0.4), col_st, m["cobblestone"], bevel=0.0)
    make_bevel_box("Setenil_TerraceCurb", (3.2, 42.0, 0.06), (204.2, 18.0, 0.0), col_st, m["cobblestone"], bevel=0.02)
    animate_buildup(st_road, DYNAMIC_REVEALS["setenil_street_build"]["start"], duration=12, mode="POP_UP", offset=(0, 0, 0.5))

    # 2. Pueblos Blancos Whitewashed Stucco Houses with Louvered Green Shutters, Brass Handles & Ceramic Numbers!
    rev_houses = DYNAMIC_REVEALS["setenil_houses_arch"]
    house_specs = [
        (205.5,  7.0, 4.2, 5.6, 4.7, 1, "12"),
        (205.5, 13.0, 4.2, 5.8, 4.6, 2, "14"),
        (205.5, 19.2, 4.4, 6.0, 4.6, 3, "16"),  # Bar La Roca building!
        (205.5, 25.6, 4.2, 6.2, 5.6, 4, "18"),  # 2nd-floor balcony house!
        (205.5, 32.0, 4.2, 5.8, 5.4, 5, "20"),
        # Opposite sunlit canyon side white houses (X=193.6)
        (193.6,  8.5, 4.0, 6.2, 6.8, 6, "11"),
        (193.6, 15.5, 4.0, 6.6, 7.4, 7, "13"),
        (193.6, 23.0, 4.0, 6.8, 7.2, 8, "15"),
        (193.8, 30.5, 4.0, 6.2, 6.5, 9, "17"),
    ]
    for idx, (hx, hy, hw, hd, hh, tag, num) in enumerate(house_specs):
        hs = make_bevel_box(f"Setenil_WhiteHouse_{tag}", (hw, hd, hh), (hx, hy, 0.0), col_st, m["white_stucco"], bevel=0.08)
        fx = -hw * 0.50 - 0.03 if hx > 200.0 else hw * 0.50 + 0.03
        out_dir = -1.0 if hx > 200.0 else 1.0
        # Framed Windows + Open Louvered Dark-Green Wooden Shutters on BOTH sides!
        for wy in (-1.45, 1.45):
            wf = make_bevel_box(f"SetWinFr_{tag}_{wy:.1f}", (0.10, 0.78, 1.28), (fx, wy, 1.55), col_st, m["wood_warm"], bevel=0.015)
            wg = make_bevel_box(f"SetWinGl_{tag}_{wy:.1f}", (0.12, 0.62, 1.12), (fx, wy, 1.63), col_st, m["apt_lit"], bevel=0.01)
            wm = make_bevel_box(f"SetWinMul_{tag}_{wy:.1f}", (0.14, 0.05, 1.14), (fx, wy, 1.62), col_st, m["white_stucco"], bevel=0.005)
            # Left & Right Opened Louvered Green Wooden Shutters!
            sh_l = make_bevel_box(f"ShutterL_{tag}_{wy:.1f}", (0.06, 0.36, 1.24), (fx + out_dir * 0.05, wy - 0.56, 1.57), col_st, m["shutter_green"], bevel=0.01)
            sh_r = make_bevel_box(f"ShutterR_{tag}_{wy:.1f}", (0.06, 0.36, 1.24), (fx + out_dir * 0.05, wy + 0.56, 1.57), col_st, m["shutter_green"], bevel=0.01)
            for p in (wf, wg, wm, sh_l, sh_r):
                p.parent = hs
        # Arched Timber Door + Brass Handle + Ceramic House Number Tile!
        door = make_bevel_box(f"SetDoor_{tag}", (0.14, 1.12, 2.24), (fx, 0.0, 0.0), col_st, m["wood_warm"], bevel=0.025)
        d_kn = make_cylinder(f"SetKnob_{tag}", 0.04, 0.10, (fx + out_dir * 0.10, 0.38, 1.05), col_st, m["brass"], segs=8, rot=(0, math.pi * 0.5, 0), pivot_bottom=False)
        tile = make_bevel_box(f"HouseNumTile_{tag}", (0.04, 0.24, 0.24), (fx + out_dir * 0.04, -0.78, 1.98), col_st, m["spanish_plate"], bevel=0.01)
        # Antique Wrought-Iron Wall Lantern!
        brkt = make_bevel_box(f"LanternArm_{tag}", (0.32, 0.05, 0.05), (fx + out_dir * 0.18, 0.88, 2.86), col_st, m["wrought_iron"], bevel=0.01)
        lant = make_cylinder(f"SetLantern_{tag}", 0.13, 0.34, (fx + out_dir * 0.30, 0.88, 2.52), col_st, m["wrought_iron"], segs=6, r_top=0.16)
        bulb = make_cylinder(f"SetBulb_{tag}", 0.09, 0.20, (fx + out_dir * 0.30, 0.88, 2.56), col_st, m["amber_glow"], segs=8)
        for p in (door, d_kn, tile, brkt, lant, bulb):
            p.parent = hs
        if hx < 200.0:
            roof = make_bevel_box(f"SetRoof_{tag}", (hw + 0.38, hd + 0.2, 0.34), (0.0, 0.0, hh), col_st, m["terracotta"], rot=(0.0, math.radians(-12.0), 0.0), bevel=0.03)
            roof.parent = hs
        animate_buildup(hs, rev_houses["start"] + idx * rev_houses["stagger"], duration=rev_houses["dur"], mode="POP_UP")

    # 3. COLOSSAL SMOOTH-SCULPTED NATURAL LIMESTONE OVERHANGING CLIFF -> HEAVY DROP LOCK (f=1554..1570 + Camera Shake!)
    # Carefully positioned strictly ABOVE house roofs (underside Z>=4.8m) & vertical canyon wall tucked behind X=211.6 (ZERO clipping through facades/signs!)
    rev_cliff = DYNAMIC_REVEALS["setenil_cliff_drop"]
    cliff_blocks = [
        (203.4,  5.5, 9.6, 7.6, 5.6, 3.7, 601),
        (202.8, 12.5, 9.4, 7.8, 6.1, 3.6, 602),
        (202.5, 19.5, 9.2, 7.8, 6.3, 3.5, 603),  # Directly over Mateo's Bar La Roca terrace (clears balconies & sign cleanly!)
        (202.8, 26.8, 9.5, 7.6, 6.1, 3.7, 604),
        (203.5, 33.8, 9.8, 7.4, 5.6, 3.8, 605),
        (212.2, 19.0, 7.0, 5.2, 24.0, 7.6, 606), # Vertical canyon wall behind houses (inner edge >= X=205.6 -> ZERO facade clip!)
    ]
    for idx, (cx, cy, cz, sx, sy, sz, sd) in enumerate(cliff_blocks):
        cl = make_sculpted_rock(
            f"Setenil_OverhangCliff_{idx}", (sx, sy, sz), (cx, cy, cz),
            col_st, m["cliff_rock"], seed=sd, subdiv=4, rough=0.20, stratify=0.06, smooth=True,  # High-subdiv smooth natural limestone!
        )
        animate_buildup(cl, rev_cliff["start"] + idx * rev_cliff["stagger"], duration=rev_cliff["dur"], mode="DROP_LOCK", offset=(0, 0, 14.0))

    # 4. 2nd-Floor Curved Wrought-Iron Juliet Balconies, Leafy Geraniums & Catenary Clothesline!
    rev_cafe = DYNAMIC_REVEALS["setenil_cafe_wave"]
    for bi_idx, by in enumerate((19.5, 23.8, 27.2)):
        bal = make_bevel_box(f"SetBalconyFloor_{by:.1f}", (0.98, 2.5, 0.14), (202.8, by, 3.85), col_bl, m["wrought_iron"], bevel=0.02)
        for rx in range(9):
            rail = make_cylinder(f"BalBar_{by:.1f}_{rx}", 0.02, 0.94, (-0.44, -1.12 + rx * 0.28, 0.14), col_bl, m["wrought_iron"], segs=6)
            rail.parent = bal
        top_r = make_bevel_box(f"BalTopRail_{by:.1f}", (0.06, 2.48, 0.05), (-0.44, 0.0, 1.06), col_bl, m["wrought_iron"], bevel=0.01)
        top_r.parent = bal
        for gi in range(3):
            gy = -0.78 + gi * 0.78
            gp = build_leafy_geranium_pot(
                f"BalGeranium_{bi_idx}_{gi}", (-0.36, gy, 0.14), col_bl,
                m["terracotta"], m["geranium_leaf"], m["geranium_red"] if gi % 2 == 0 else m["geranium_pink"], seed=710 + bi_idx * 10 + gi,
            )
            gp.parent = bal
        animate_buildup(bal, rev_cafe["start"] + bi_idx * 3, duration=10, mode="SLIDE_IN", offset=(1.2, 0, 0))

    # Real Catenary-Curved Sagging Clothesline Rope stretched across Alley (X=195.7..203.2, Y=24.8, Z=5.1m)!
    rope_segs = 12
    for ri in range(rope_segs):
        u0 = ri / float(rope_segs)
        u1 = (ri + 1) / float(rope_segs)
        x0, x1 = 195.7 + u0 * 7.5, 195.7 + u1 * 7.5
        z0 = 5.15 - math.sin(u0 * math.pi) * 0.42
        z1 = 5.15 - math.sin(u1 * math.pi) * 0.42
        seg_len = math.hypot(x1 - x0, z1 - z0)
        seg_ang = math.atan2(z1 - z0, x1 - x0)
        make_cylinder(
            f"LaundryRope_{ri:02d}", 0.016, seg_len, ((x0 + x1) * 0.5, 24.8, (z0 + z1) * 0.5),
            col_bl, m["wrought_iron"], segs=6, rot=(0.0, math.pi * 0.5 - seg_ang, 0.0), pivot_bottom=False,
        )
    for li, (lx, lmat) in enumerate([(197.8, m["laundry_cream"]), (199.2, m["laundry_coral"]), (200.6, m["laundry_cream"])]):
        u_s = (lx - 195.7) / 7.5
        z_line = 5.15 - math.sin(u_s * math.pi) * 0.42
        sh = make_bevel_box(f"LaundrySheet_{li}", (0.86, 0.035, 1.05), (lx, 24.8, z_line - 0.52), col_bl, lmat, bevel=0.01, pivot_bottom=False)
        for pin_x in (-0.34, 0.34):
            pin = make_bevel_box(f"ClothesPin_{li}_{pin_x:.2f}", (0.04, 0.06, 0.10), (pin_x, 0.0, 0.52), col_bl, m["wood_warm"], bevel=0.005)
            pin.parent = sh
        for kf in range(1520, 2283, 24):
            ang = math.radians(10.0 + math.sin((kf + li * 17) * 0.12) * 16.0)
            sh.rotation_euler = (ang, 0.0, 0.0)
            sh.keyframe_insert("rotation_euler", frame=kf)
        _set_bezier_ease(sh)

    # 5. Bar La Roca Terrace: Unobstructed Menu Board + Marble-Iron Bistro Tables + 4-Legged Wicker Chairs + Wine Barrels!
    bar_sign = make_sign_plane("Sign_BarLaRoca", 1.05, 1.38, (202.85, 17.5, 1.15), -24.0, col_st, m["sign_bar_laroca"], m["wood_warm"])
    animate_buildup(bar_sign, DYNAMIC_REVEALS["bar_sign_popup"]["start"], duration=12, mode="POP_UP")

    table_ys = [11.5, 14.0, 16.4, 19.6, 22.8]
    for ti, ty in enumerate(table_ys):
        tx = 201.9 if ti != 3 else 201.4
        tbl = make_cylinder(f"BistroTable_{ti}", 0.045, 0.76, (tx, ty, 0.0), col_st, m["wrought_iron"], segs=10)
        base = make_cylinder(f"BistroBase_{ti}", 0.28, 0.05, (0.0, 0.0, 0.0), col_st, m["wrought_iron"], segs=12)
        top = make_cylinder(f"BistroMarble_{ti}", 0.54, 0.05, (0.0, 0.0, 0.75), col_st, m["marble_top"], segs=18)
        runner = make_bevel_box(f"BistroRunner_{ti}", (0.44, 1.02, 0.015), (0.0, 0.0, 0.80), col_st, m["table_cloth"], bevel=0.005)
        plate = make_cylinder(f"TapasPlate_{ti}", 0.18, 0.025, (0.08, -0.05, 0.815), col_st, m["spanish_plate"], segs=14)
        bread = make_bevel_box(f"TapasBread_{ti}", (0.15, 0.09, 0.05), (0.08, -0.05, 0.84), col_st, m["tapas_bread"], bevel=0.015)
        oj = make_cylinder(f"OrangeJuice_{ti}", 0.04, 0.13, (-0.18, 0.12, 0.815), col_st, m["box_yellow"], segs=10)
        for p in (base, top, runner, plate, bread, oj):
            p.parent = tbl
        ch1 = build_wicker_cafe_chair(f"WickerChairA_{ti}", (0.0, 0.72, 0.0), 0.0, col_st, m["wrought_iron"], m["wicker_tan"])
        ch2 = build_wicker_cafe_chair(f"WickerChairB_{ti}", (0.0, -0.72, 0.0), 180.0, col_st, m["wrought_iron"], m["wicker_tan"])
        ch1.parent = tbl
        ch2.parent = tbl
        animate_buildup(tbl, rev_cafe["start"] + ti * rev_cafe["stagger"], duration=10, mode="POP_UP")

    # Iron-Hooped Oak Wine Barrels & Hanging Leafy Geranium Pots along Street!
    for bi, by in enumerate([10.0, 18.2, 24.4]):
        bar = make_cylinder(f"WineBarrel_{bi}", 0.34, 0.92, (202.9, by, 0.0), col_st, m["wood_warm"], segs=16)
        for hz in (0.18, 0.74):
            hp = make_cylinder(f"BarrelHoop_{bi}_{hz:.2f}", 0.352, 0.05, (0.0, 0.0, hz), col_st, m["wrought_iron"], segs=16)
            hp.parent = bar
        animate_buildup(bar, rev_cafe["start"] + (bi + 5) * rev_cafe["stagger"], duration=10, mode="POP_UP")

    for gi, gy in enumerate([9.0, 12.2, 15.4, 18.6, 21.8, 25.0]):
        gp = build_leafy_geranium_pot(
            f"StreetGeranium_{gi}", (203.05, gy, 1.85), col_st,
            m["terracotta"], m["geranium_leaf"], m["geranium_red"] if gi % 2 == 0 else m["geranium_pink"], seed=810 + gi,
        )
        animate_buildup(gp, rev_cafe["start"] + (gi + 2) * rev_cafe["stagger"], duration=10, mode="POP_UP")

    # Background Canyon Horizon: Authentic Arched Andalusian Stone Bridge + Sunlit Hillside & Tiered Terracotta Village (ZERO sky void under arch!)
    make_bevel_box("Setenil_BridgeDeck", (13.0, 3.2, 0.85), (200.0, 42.5, 2.5), col_st, m["cliff_rock"], bevel=0.10)
    make_bevel_box("Setenil_BridgePierL", (3.2, 3.2, 2.8), (195.2, 42.5, 0.0), col_st, m["cliff_rock"], bevel=0.10)
    make_bevel_box("Setenil_BridgePierR", (3.2, 3.2, 2.8), (204.8, 42.5, 0.0), col_st, m["cliff_rock"], bevel=0.10)
    make_bevel_box("Setenil_BridgeRail", (13.0, 0.25, 0.85), (200.0, 41.0, 3.3), col_st, m["white_stucco"], bevel=0.04)
    # Sunlit Andalusian hillside rising smoothly behind the tiered hilltop village (leaves village houses bright & prominent!)
    make_sculpted_rock("Setenil_FarHill", (26.0, 16.0, 4.8), (200.0, 68.0, 0.0), col_st, m["cliff_rock"], seed=909, subdiv=3, rough=0.18, smooth=True, flatten_bottom=True)
    # Distant Andalusian hilltop white houses with sloped terracotta tile roofs & green shutters (visible THROUGH & ABOVE arch!)
    for dh, (dx, dy, dz, dw, dd, dhh) in enumerate([
        (197.6, 48.0, 0.0, 3.8, 3.8, 4.2),
        (201.8, 49.0, 0.0, 4.0, 3.8, 4.5),
        (195.0, 52.0, 2.8, 4.4, 4.2, 4.8),
        (199.8, 53.5, 3.8, 4.6, 4.2, 5.2),
        (204.6, 52.5, 3.4, 4.4, 4.2, 4.9),
        (197.5, 58.0, 6.4, 5.0, 4.4, 5.4),
    ]):
        vh = make_bevel_box(f"VillageHouse_{dh}", (dw, dd, dhh), (dx, dy, dz), col_st, m["white_stucco"], bevel=0.06)
        vr = make_bevel_box(f"VillageRoof_{dh}", (dw + 0.4, dd + 0.4, 0.45), (0, 0, dhh), col_st, m["terracotta"], rot=(math.radians(14.0), 0, 0), bevel=0.04)
        vw = make_bevel_box(f"VillageWin_{dh}", (0.85, 0.14, 1.15), (0, -dd * 0.5 - 0.03, dhh * 0.52), col_st, m["shutter_green"], bevel=0.02)
        vr.parent = vh
        vw.parent = vh

    # Soft Diagonal Golden Hour God Rays + Gliding Canyon Birds!
    for ri, ry in enumerate([10.5, 22.5, 31.5]):
        ray = make_cylinder(
            f"GoldenGodRay_{ri}", 0.82, 11.0, (196.6, ry, 5.8), col_bl, m["god_ray_gold"],
            segs=18, r_top=0.34, rot=(0.0, math.radians(-38.0), math.radians(10.0)), pivot_bottom=False,
        )
        ray.visible_shadow = False

    for bi in range(3):
        bird = make_bevel_box(f"SetenilBird_{bi}", (0.55, 0.14, 0.06), (192.0 + bi * 2.2, 36.0 + bi * 3.0, 9.5 + bi * 0.9), col_bl, m["wrought_iron"], bevel=0.01)
        bird.keyframe_insert("location", frame=1520)
        bird.location = (208.0 + bi * 1.5, 42.0 + bi * 2.0, 10.9 + bi * 0.7)
        bird.keyframe_insert("location", frame=2282)

    # ---- SETENIL GOLDEN HOUR LIGHTS (Strictly inside LOC_03_Setenil!) ----
    def _lgt(name, ltype, loc, rot_deg, energy, color, size=1.0):
        ld = bpy.data.lights.new(name=name, type=ltype)
        ld.energy = energy
        ld.color = color
        if ltype == "AREA": ld.size = size
        elif ltype == "POINT": ld.shadow_soft_size = size
        elif ltype == "SUN": ld.angle = math.radians(2.0)
        o = bpy.data.objects.new(name, ld)
        o.location = loc
        o.rotation_euler = tuple(math.radians(a) for a in rot_deg)
        return link_obj(o, col_lgt)

    _lgt("Setenil_GoldenSun", "SUN", (180.0, 10.0, 18.0), (76.0, 0.0, -58.0), 4.6, (1.0, 0.78, 0.46))
    _lgt("Setenil_WarmBounce1", "AREA", (197.2, 12.0, 3.2), (65.0, 0.0, -74.0), 480.0, (1.0, 0.80, 0.50), size=6.0)
    _lgt("Setenil_WarmBounce2", "AREA", (197.2, 22.0, 3.4), (65.0, 0.0, -74.0), 520.0, (1.0, 0.78, 0.46), size=6.5)
    _lgt("Setenil_CafeGlow", "POINT", (201.6, 19.0, 2.75), (0, 0, 0), 130.0, (1.0, 0.82, 0.52), size=0.5)


# ============================================================================
# GROUND-LOCKED 2.5D CHARACTER CARDS & 9:16 VERTICAL CAMERA RIG
# ============================================================================
def build_character_cards() -> None:
    col_c = ensure_collection("Characters_25D_Hybrid")
    vis_frac = 0.8365
    bot_margin = 0.0779
    aspect = 480.0 / 1040.0

    actor_heights = {
        "fajar": 1.72, "pak_arthur": 1.68, "maya": 1.56,
        "jack": 1.72, "elena": 1.66, "mateo": 1.74,
        "npc_whittier_1": 1.66, "npc_whittier_2": 1.70,
        "npc_setenil_1": 1.64, "npc_setenil_2": 1.68, "npc_setenil_3": 1.66,
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
        default_img = SPRITES_ROOT / slug / "frame_0025.png"
        if not default_img.exists() and (SPRITES_ROOT / slug).exists():
            cands = sorted((SPRITES_ROOT / slug).glob("*.png"))
            if cands:
                default_img = cands[0]
        obj.data.materials.append(make_character_card_material(f"Mat_Actor_{slug}", default_img))
        link_obj(obj, col_c)


def build_camera_and_render_settings() -> None:
    col_cam = ensure_collection("Camera_Rig")
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 0
    scene.frame_end = TOTAL_FRAMES - 1

    # VERTICAL 9:16 PRODUCTION STANDARD (1080x1920 default; overridden cleanly by --res in draft!)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.05
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 3
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 1
    scene.cycles.transparent_max_bounces = 12

    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.12

    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Punchy"
    except Exception:
        scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.12

    tgt = bpy.data.objects.new("CameraTarget", None)
    tgt.empty_display_type = "SPHERE"
    tgt.empty_display_size = 0.35
    link_obj(tgt, col_cam)

    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.sensor_fit = "VERTICAL"  # Consistent 9:16 vertical FOV!
    cam_data.lens = 25.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 450.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    link_obj(cam_obj, col_cam)
    scene.camera = cam_obj

    trk = cam_obj.constraints.new(type="TRACK_TO")
    trk.target = tgt
    trk.track_axis = "TRACK_NEGATIVE_Z"
    trk.up_axis = "UP_Y"

    for f in range(0, TOTAL_FRAMES, 4):
        pos, look, lens = get_camera_state(f)
        cam_obj.location = pos
        tgt.location = look
        cam_data.lens = lens
        cam_obj.keyframe_insert("location", frame=f)
        tgt.keyframe_insert("location", frame=f)
        cam_data.keyframe_insert("lens", frame=f)


def _collect_col_objects(col: bpy.types.Collection) -> list[bpy.types.Object]:
    seen = set()
    out: list[bpy.types.Object] = []
    def _walk(c: bpy.types.Collection) -> None:
        for o in list(c.objects):
            if o is not None and o.name not in seen:
                seen.add(o.name)
                out.append(o)
        for ch in list(c.children):
            _walk(ch)
    _walk(col)
    return out


def keyframe_location_isolation() -> None:
    """Bake hide_render/hide_viewport on every object in each location collection for Blender GUI playback.
    (Note: Collection.hide_render is not keyframeable in Blender 4.2; render_blender_chunk.py ALSO sets
    collection visibility directly per frame for 100% double-locked location isolation.)"""
    for loc_name, (f0, f1) in LOCATION_RANGES.items():
        col = bpy.data.collections.get(loc_name)
        if not col:
            continue
        keyframes = [
            (0, loc_name != "LOC_01_Whittier"),
            (835, loc_name != "LOC_01_Whittier"),
            (836, loc_name != "LOC_02_CooberPedy"),
            (1518, loc_name != "LOC_02_CooberPedy"),
            (1519, loc_name != "LOC_03_Setenil"),
            (2282, loc_name != "LOC_03_Setenil"),
        ]
        for obj in _collect_col_objects(col):
            for f_test, hidden in keyframes:
                obj.hide_render = hidden
                obj.hide_viewport = hidden
                obj.keyframe_insert("hide_render", frame=f_test)
                obj.keyframe_insert("hide_viewport", frame=f_test)
            if obj.animation_data and obj.animation_data.action:
                for fc in obj.animation_data.action.fcurves:
                    if fc.data_path in ("hide_render", "hide_viewport"):
                        for kp in fc.keyframe_points:
                            kp.interpolation = "CONSTANT"


def main() -> None:
    print("Building V2 VERTICAL 9:16 3D Master Scene: 3 Kota Paling Unik di Dunia...")
    clear_scene()
    worlds = create_natural_worlds()
    bpy.context.scene.world = worlds["whittier_ext"]

    mats = create_materials()
    col_loc1 = ensure_collection("LOC_01_Whittier")
    col_loc2 = ensure_collection("LOC_02_CooberPedy")
    col_loc3 = ensure_collection("LOC_03_Setenil")

    build_loc01_whittier(mats, col_loc1)
    build_loc02_coober_pedy(mats, col_loc2)
    build_loc03_setenil(mats, col_loc3)
    build_character_cards()
    build_camera_and_render_settings()
    keyframe_location_isolation()

    PROD_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    print(f"SUCCESS! Saved V2 Vertical 9:16 Master Scene: {BLEND_OUT}")


if __name__ == "__main__":
    main()
