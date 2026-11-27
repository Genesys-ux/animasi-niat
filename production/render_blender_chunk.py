"""
V2 Blender 4.2 Vertical 9:16 Headless Chunk Renderer with STRICT 3-Location Collection Isolation!
- Forces Vertical 9:16 sensor fit (`camera.data.sensor_fit = 'VERTICAL'`)
- Strictly isolates LOC_01_Whittier, LOC_02_CooberPedy, and LOC_03_Setenil via hide_render & hide_viewport
  (ZERO cross-location mountain/building bleed ever possible!)
- Dynamically switches physical Nishita / Arctic Cloud / Cozy Interior World shaders per scene!
- Updates ground-locked 2.5D Open Free-Rig character cards + 3D held hero props per frame!

Usage:
  blender --background production/three_unique_cities.blend --python production/render_blender_chunk.py -- --frames 25,445,765,975,1395,1465,1855 --res 540x960 --samples 12
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPRITES_ROOT = PROJECT_ROOT / "production" / "char_sprites"
OUT_FRAMES_DEFAULT = PROJECT_ROOT / "production" / "rendered_frames"
sys.path.insert(0, str(PROJECT_ROOT / "production"))

from timeline_data import (
    get_active_location,
    get_camera_state,
    get_character_states,
    get_scene_id,
)

ACTOR_SLUGS = {
    "Fajar": "fajar",
    "Pak Arthur": "pak_arthur",
    "Maya": "maya",
    "Jack": "jack",
    "Elena": "elena",
    "Mateo": "mateo",
    "NPC_Whittier_1": "npc_whittier_1",
    "NPC_Whittier_2": "npc_whittier_2",
    "NPC_Setenil_1": "npc_setenil_1",
    "NPC_Setenil_2": "npc_setenil_2",
    "NPC_Setenil_3": "npc_setenil_3",
}

ALL_LOC_COLLECTIONS = ("LOC_01_Whittier", "LOC_02_CooberPedy", "LOC_03_Setenil")

SCENE_TINTS = {
    "whittier_ext":    (0.86, 0.93, 1.00, 1.0),
    "whittier_lobby":  (1.00, 0.95, 0.87, 1.0),
    "whittier_tunnel": (0.94, 0.97, 1.00, 1.0),
    "coober_desert":   (1.00, 0.92, 0.80, 1.0),
    "coober_dugout":   (0.98, 0.91, 0.82, 1.0),
    "setenil_street":  (1.00, 0.94, 0.83, 1.0),
    "setenil_balcony": (1.00, 0.92, 0.80, 1.0),
    "setenil_outro":   (1.00, 0.90, 0.76, 1.0),
}

SCENE_TO_WORLD = {
    "whittier_ext":    "World_Whittier_Arctic",
    "whittier_lobby":  "World_Interior_Cozy",
    "whittier_tunnel": "World_Interior_Cozy",
    "coober_desert":   "World_CooberPedy_Desert",
    "coober_dugout":   "World_Interior_Cozy",
    "setenil_street":  "World_Setenil_Golden",
    "setenil_balcony": "World_Setenil_Golden",
    "setenil_outro":   "World_Setenil_Golden",
}


def update_frame_state(scene: bpy.types.Scene, frame: int) -> None:
    scene.frame_set(frame)
    scene_id = get_scene_id(frame)
    active_loc = get_active_location(frame)
    cam_pos, cam_tgt, cam_lens = get_camera_state(frame)

    # 1. STRICT 3-LOCATION COLLECTION ISOLATION (Zero cross-location visual/light bleed!)
    for loc_name in ALL_LOC_COLLECTIONS:
        col = bpy.data.collections.get(loc_name)
        if col:
            is_active = (loc_name == active_loc)
            col.hide_render = not is_active
            col.hide_viewport = not is_active

    # 2. Switch Physical Natural World Sky (Arctic Cloud / Outback Nishita / Spanish Golden Hour!)
    world_name = SCENE_TO_WORLD.get(scene_id, "World_Whittier_Arctic")
    w = bpy.data.worlds.get(world_name)
    if w:
        scene.world = w

    # 3. Exact 9:16 Vertical Camera Transform & Lens
    cam_obj = bpy.data.objects.get("MainCamera")
    tgt_obj = bpy.data.objects.get("CameraTarget")
    if cam_obj and tgt_obj:
        cam_obj.location = cam_pos
        tgt_obj.location = cam_tgt
        cam_obj.data.lens = cam_lens
        cam_obj.data.sensor_fit = "VERTICAL"

    # 4. Update all 2.5D Hybrid Character Cards (ground-locked + cylindrical yaw + frame sprite)
    tint = SCENE_TINTS.get(scene_id, (1.0, 1.0, 1.0, 1.0))
    char_states = get_character_states(frame)
    for name, st in char_states.items():
        slug = ACTOR_SLUGS[name]
        obj = bpy.data.objects.get(f"Actor_{slug}")
        if not obj:
            continue
        vis = bool(st["visible"])
        obj.hide_render = not vis
        obj.hide_viewport = not vis
        if not vis:
            continue

        px, py, pz = st["pos"]
        obj.location = (px, py, pz)
        dx = cam_pos[0] - px
        dy = cam_pos[1] - py
        yaw = math.atan2(dy, dx) - math.pi * 0.5
        obj.rotation_euler = (0.0, 0.0, yaw)

        sprite_path = SPRITES_ROOT / slug / f"frame_{frame:04d}.png"
        if sprite_path.exists() and obj.data.materials:
            mat = obj.data.materials[0]
            if mat and mat.use_nodes:
                tex_node = mat.node_tree.nodes.get("CharTex")
                if tex_node:
                    img_name = f"spr_{slug}_{frame:04d}"
                    img = bpy.data.images.get(img_name)
                    if img is None:
                        img = bpy.data.images.load(str(sprite_path), check_existing=False)
                        img.name = img_name
                    tex_node.image = img
                tint_node = mat.node_tree.nodes.get("EnvTint")
                if tint_node:
                    tint_node.inputs["B"].default_value = tint

    # 5. Sync 3D Hero Held Props (Pak Arthur mug, Hero Vent Cap match-cut clear, Elena flashlight beam!)
    mug = bpy.data.objects.get("Prop_Whittier_Mug")
    if mug and "Pak Arthur" in char_states and char_states["Pak Arthur"]["visible"]:
        ax, ay, az = char_states["Pak Arthur"]["pos"]
        if frame < 426:
            mug.location = (ax + 0.44, ay - 0.16, az + 0.88)
        else:
            mug.location = (-3.22, 26.25, 1.18)

    hv_cap = bpy.data.objects.get("HeroVentPipe_Cap")
    if hv_cap:
        cap_hide = 836 <= frame <= 848
        hv_cap.hide_render = cap_hide or (active_loc != "LOC_02_CooberPedy")
        hv_cap.hide_viewport = hv_cap.hide_render

    flash_cone = bpy.data.objects.get("Prop_Elena_FlashBeam")
    flash_spot = bpy.data.objects.get("Light_Elena_Flashlight")
    if flash_cone and flash_spot:
        en = 1093 <= frame <= 1518
        flash_cone.hide_render = not en
        flash_spot.hide_render = not en
        if en:
            boost = 1.0 + max(0.0, (frame - 1425) / 60.0) * 3.4
            flash_spot.data.energy = 260.0 * boost

    bpy.context.view_layer.update()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Render Vertical 9:16 Blender 4.2 frames")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--frames", type=str, default="")
    parser.add_argument("--res", type=str, default="720x1280", help="Vertical 9:16 resolution (540x960, 720x1280, 1080x1920)")
    parser.add_argument("--samples", type=int, default=14)
    parser.add_argument("--out-dir", type=str, default=str(OUT_FRAMES_DEFAULT))
    parser.add_argument("--engine", type=str, default="CYCLES")
    args = parser.parse_args(argv)

    w_str, h_str = args.res.lower().split("x")
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    scene.render.engine = args.engine
    scene.render.resolution_x = int(w_str)
    scene.render.resolution_y = int(h_str)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    if args.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = args.samples
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.05
        scene.cycles.use_denoising = True
        scene.cycles.max_bounces = 3
        scene.cycles.diffuse_bounces = 2
        scene.cycles.glossy_bounces = 1
        scene.cycles.transparent_max_bounces = 12

    if args.frames.strip():
        frame_list = [int(x.strip()) for x in args.frames.split(",") if x.strip()]
    else:
        frame_list = list(range(args.start, args.end + 1))

    print(f"Rendering {len(frame_list)} VERTICAL 9:16 frames @ {w_str}x{h_str} ({args.engine}, samples={args.samples}) -> {out_dir}")
    for idx, f in enumerate(frame_list, 1):
        update_frame_state(scene, f)
        out_file = out_dir / f"frame_{f:04d}.png"
        scene.render.filepath = str(out_file)
        bpy.ops.render.render(write_still=True)
        if idx % 12 == 0:
            for img in list(bpy.data.images):
                if img.name.startswith("spr_") and img.users == 0:
                    bpy.data.images.remove(img)
        if idx % 10 == 0 or idx == len(frame_list):
            print(f"  [Blender 9:16] {idx}/{len(frame_list)} (frame {f:04d})", flush=True)


if __name__ == "__main__":
    main()
