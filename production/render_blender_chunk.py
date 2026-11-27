"""
Blender 4.2 Headless Chunk Renderer for both Local Verification & GitHub Actions Parallel Matrix!
Loads production/three_unique_cities.blend, dynamically updates character RGBA sprites per frame
with 100% camera-facing cylindrical tracking + environmental lighting mood tint, and renders crisp
PNG frames ready for FFmpeg MP4 assembly with audio/master_mix.wav!

Usage:
  blender --background production/three_unique_cities.blend --python production/render_blender_chunk.py -- --start 0 --end 115 --res 1280x720
  blender --background production/three_unique_cities.blend --python production/render_blender_chunk.py -- --frames 25,220,445,765,975,1395,1465,1760,1855,2180 --res 1280x720
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

from timeline_data import get_camera_state, get_character_states, get_scene_id

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

# Dynamic Story Mood Tint per Location (keeps 2.5D characters grounded in 3D atmosphere!)
SCENE_TINTS = {
    "whittier_ext":    (0.84, 0.92, 1.00, 1.0),  # Crisp Arctic Overcast Blue-Grey
    "whittier_lobby":  (1.00, 0.95, 0.87, 1.0),  # Cozy 3400K Warm Tungsten
    "whittier_tunnel": (0.94, 0.97, 1.00, 1.0),  # Caged Fluorescent Underground
    "coober_desert":   (1.00, 0.92, 0.80, 1.0),  # Scorching Outback Sun
    "coober_dugout":   (0.98, 0.90, 0.82, 1.0),  # Warm Copper Sandstone Glow
    "setenil_street":  (1.00, 0.94, 0.84, 1.0),  # Golden Hour Andalusian Bounce
    "setenil_balcony": (1.00, 0.93, 0.82, 1.0),  # Golden Hour Warm Sunlight
    "setenil_outro":   (1.00, 0.91, 0.78, 1.0),  # Rich Golden Hour Sunset
}

# World Sky & Atmospheric Haze shifts when the story turns!
SCENE_WORLD = {
    "whittier_ext":    ((0.46, 0.58, 0.72), (0.72, 0.80, 0.88), 0.75),
    "whittier_lobby":  ((0.18, 0.14, 0.10), (0.34, 0.25, 0.16), 0.35),
    "whittier_tunnel": ((0.06, 0.08, 0.12), (0.12, 0.16, 0.22), 0.20),
    "coober_desert":   ((0.96, 0.68, 0.36), (0.52, 0.74, 0.96), 1.35),
    "coober_dugout":   ((0.12, 0.07, 0.04), (0.18, 0.10, 0.05), 0.18),
    "setenil_street":  ((0.98, 0.74, 0.42), (0.36, 0.56, 0.84), 1.15),
    "setenil_balcony": ((0.98, 0.70, 0.38), (0.32, 0.50, 0.80), 1.20),
    "setenil_outro":   ((0.98, 0.62, 0.30), (0.26, 0.42, 0.74), 1.25),
}


def update_frame_state(scene: bpy.types.Scene, frame: int) -> None:
    """Update world mood, character sprite textures, positions, and billboard facing for exact frame."""
    scene.frame_set(frame)
    scene_id = get_scene_id(frame)
    cam_pos, cam_tgt, cam_lens = get_camera_state(frame)

    # 1. Exact camera transform & lens
    cam_obj = bpy.data.objects.get("MainCamera")
    tgt_obj = bpy.data.objects.get("CameraTarget")
    if cam_obj and tgt_obj:
        cam_obj.location = cam_pos
        tgt_obj.location = cam_tgt
        cam_obj.data.lens = cam_lens

    # 2. Dynamic Story World Atmosphere (changes dramatically across all 3 cities!)
    world = scene.world
    if world and world.use_nodes:
        nt = world.node_tree
        hor_col, zen_col, bg_str = SCENE_WORLD.get(scene_id, SCENE_WORLD["whittier_ext"])
        ramp = nt.nodes.get("SkyRamp")
        bg = nt.nodes.get("WorldBG")
        if ramp:
            ramp.color_ramp.elements[0].color = (*hor_col, 1.0)
            ramp.color_ramp.elements[1].color = (*zen_col, 1.0)
        if bg:
            bg.inputs["Strength"].default_value = bg_str

    # 3. Update every 2.5D character card (exact ground-locked 3D pos + sprite image + cylindrical yaw!)
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
        # Cylindrical Z-billboard facing camera cleanly in XY plane (zero tilting distortion!)
        dx = cam_pos[0] - px
        dy = cam_pos[1] - py
        yaw = math.atan2(dy, dx) - math.pi * 0.5
        obj.rotation_euler = (0.0, 0.0, yaw)

        # Swap crisp frame sprite texture
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

    # 4. Sync Hero 3D Held Props (Pak Arthur mug on Post Office counter, Elena LED flashlight cone!)
    mug = bpy.data.objects.get("Prop_Whittier_Mug")
    if mug and "Pak Arthur" in char_states and char_states["Pak Arthur"]["visible"]:
        ax, ay, az = char_states["Pak Arthur"]["pos"]
        if frame < 426:
            mug.location = (ax + 0.42, ay - 0.12, az + 0.88)
        else:
            # Set neatly on top of the Post Office brass counter right beside Pak Arthur!
            mug.location = (-3.32, 26.35, 1.18)

    flash_cone = bpy.data.objects.get("Prop_Elena_FlashBeam")
    flash_spot = bpy.data.objects.get("Light_Elena_Flashlight")
    if flash_cone and flash_spot:
        en = 1093 <= frame <= 1518
        flash_cone.hide_render = not en
        flash_spot.hide_render = not en
        if en:
            # Pulse intensity brightly right as Elena reveals the billion-rupiah Opal Vein!
            boost = 1.0 + max(0.0, (frame - 1425) / 65.0) * 3.2
            flash_spot.data.energy = 140.0 * boost

    # Flush depsgraph before render
    bpy.context.view_layer.update()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description="Render Blender 4.2 frames for 3 Unique Cities")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--frames", type=str, default="")
    parser.add_argument("--res", type=str, default="1280x720")
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--out-dir", type=str, default=str(OUT_FRAMES_DEFAULT))
    parser.add_argument("--engine", type=str, default="CYCLES", help="CYCLES (headless safe) or BLENDER_EEVEE_NEXT")
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

    if args.engine == "BLENDER_EEVEE_NEXT":
        scene.eevee.taa_render_samples = args.samples
        scene.eevee.use_shadows = True
        scene.eevee.use_raytracing = False
    elif args.engine == "CYCLES":
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

    print(f"Rendering {len(frame_list)} frames @ {w_str}x{h_str} ({args.engine}, samples={args.samples}) -> {out_dir}")
    for idx, f in enumerate(frame_list, 1):
        update_frame_state(scene, f)
        out_file = out_dir / f"frame_{f:04d}.png"
        scene.render.filepath = str(out_file)
        bpy.ops.render.render(write_still=True)
        # Periodically purge old dynamically loaded sprite images to keep RAM tiny
        if idx % 12 == 0:
            for img in list(bpy.data.images):
                if img.name.startswith("spr_") and img.users == 0:
                    bpy.data.images.remove(img)
        if idx % 10 == 0 or idx == len(frame_list):
            print(f"  [Blender] {idx}/{len(frame_list)} (frame {f:04d})", flush=True)


if __name__ == "__main__":
    main()
