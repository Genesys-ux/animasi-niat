"""
V2 Mid-Poly Cel-Shaded Semi-Realistic Material & Natural Geology / Sky Library for Blender 4.2 Cycles.

Eliminates ALL artificial "corrugated cardboard" Wave stripes and flat "plasticine" surfaces:
  - Multi-scale Object-coordinate Natural Rock shader: Macro FBM Noise strata + Voronoi
    (DISTANCE_TO_EDGE) natural stone fractures/mossy crevices + Micro sand grain grit!
  - Slope-aware Snowy Mountain shader: Dark rocky Alaskan granite peeking through steep slopes
    with bright wind-sculpted snow on ridges!
  - True Individual Cobblestone Street shader: Voronoi edge mortar grooves + per-stone tan/grey
    variation + subtle foot-traffic roughness variation!
  - Soft Lime-Plaster Stucco shader for Setenil Pueblos Blancos walls!
  - Multi-faceted Iridescent Rainbow Opal Crystal shader for Coober Pedy!
  - Physical Natural World Skies (Arctic Cloud Overcast, Outback Nishita High-Dust Sun,
    Spanish Golden Hour 12° Low Sun Nishita Sky)!
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Tuple

import bpy

TEX_DIR = Path(__file__).resolve().parent / "textures"
TEX_DIR.mkdir(parents=True, exist_ok=True)


def _srgb_to_linear(c: Tuple[float, float, float]) -> Tuple[float, float, float, float]:
    def conv(v: float) -> float:
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (conv(c[0]), conv(c[1]), conv(c[2]), 1.0)


def get_sign_texture_paths() -> dict[str, Path]:
    names = [
        "sign_begich_ext",
        "sign_directory",
        "sign_post_office",
        "sign_kozy_korner",
        "sign_school_tunnel",
        "sign_danger_shafts",
        "sign_opal_map",
        "sign_bar_laroca",
    ]
    return {nm: TEX_DIR / f"{nm}.png" for nm in names}


def _wire_cel_surface(
    nt: bpy.types.NodeTree,
    albedo_socket,
    normal_socket,
    shadow_rgb: Tuple[float, float, float],
    highlight_rgb: Tuple[float, float, float],
    roughness: float = 0.75,
    metallic: float = 0.0,
    emission_rgb: Tuple[float, float, float] | None = None,
    emission_strength: float = 0.0,
    rim_strength: float = 0.20,
) -> None:
    """Shared Semi-Realistic Cel-Shaded BSDF output block (Toon + Principled + Blue Shade AO + Warm Rim)."""
    nodes, links = nt.nodes, nt.links
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1050, 0)

    # Fast 1-sample Ambient Occlusion -> Crisp Blue Shade in crevices & contact seams!
    ao = nodes.new("ShaderNodeAmbientOcclusion")
    ao.samples = 1
    ao.inputs["Distance"].default_value = 1.4
    ao.location = (220, 360)
    links.new(albedo_socket, ao.inputs["Color"])

    ao_ramp = nodes.new("ShaderNodeValToRGB")
    ao_ramp.location = (400, 360)
    ao_ramp.color_ramp.elements[0].position = 0.22
    ao_ramp.color_ramp.elements[0].color = _srgb_to_linear(shadow_rgb)
    ao_ramp.color_ramp.elements[1].position = 0.78
    ao_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(ao.outputs["AO"], ao_ramp.inputs["Fac"])

    albedo_ao = nodes.new("ShaderNodeMix")
    albedo_ao.data_type = "RGBA"
    albedo_ao.blend_type = "MULTIPLY"
    albedo_ao.inputs["Factor"].default_value = 0.68
    albedo_ao.location = (560, 240)
    links.new(albedo_socket, albedo_ao.inputs["A"])
    links.new(ao_ramp.outputs["Color"], albedo_ao.inputs["B"])

    toon = nodes.new("ShaderNodeBsdfToon")
    toon.component = "DIFFUSE"
    toon.location = (640, 120)
    toon.inputs["Size"].default_value = 0.70
    toon.inputs["Smooth"].default_value = 0.16
    links.new(albedo_ao.outputs["Result"], toon.inputs["Color"])
    if normal_socket is not None:
        links.new(normal_socket, toon.inputs["Normal"])

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (640, -140)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    links.new(albedo_ao.outputs["Result"], bsdf.inputs["Base Color"])
    if normal_socket is not None:
        links.new(normal_socket, bsdf.inputs["Normal"])
    if emission_rgb and emission_strength > 0.0:
        bsdf.inputs["Emission Color"].default_value = _srgb_to_linear(emission_rgb)
        bsdf.inputs["Emission Strength"].default_value = emission_strength * 2.2

    cel_mix = nodes.new("ShaderNodeMixShader")
    cel_mix.location = (840, 40)
    cel_mix.inputs["Fac"].default_value = 0.85 if (metallic > 0.4 or emission_strength > 0.0) else 0.45
    links.new(toon.outputs["BSDF"], cel_mix.inputs[1])
    links.new(bsdf.outputs["BSDF"], cel_mix.inputs[2])

    if rim_strength > 0.01:
        lw = nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.22
        rim_ramp = nodes.new("ShaderNodeValToRGB")
        rim_ramp.color_ramp.elements[0].position = 0.70
        rim_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        rim_ramp.color_ramp.elements[1].position = 0.90
        rim_ramp.color_ramp.elements[1].color = (rim_strength, rim_strength, rim_strength, 1.0)
        links.new(lw.outputs["Facing"], rim_ramp.inputs["Fac"])

        rim_em = nodes.new("ShaderNodeEmission")
        rim_em.inputs["Color"].default_value = _srgb_to_linear(highlight_rgb)
        rim_em.inputs["Strength"].default_value = 1.08

        final_sh = nodes.new("ShaderNodeMixShader")
        final_sh.location = (940, 20)
        links.new(rim_ramp.outputs["Color"], final_sh.inputs["Fac"])
        links.new(cel_mix.outputs["Shader"], final_sh.inputs[1])
        links.new(rim_em.outputs["Emission"], final_sh.inputs[2])
        links.new(final_sh.outputs["Shader"], out.inputs["Surface"])
    else:
        links.new(cel_mix.outputs["Shader"], out.inputs["Surface"])


def make_natural_rock_material(
    name: str,
    col_crevice: Tuple[float, float, float],
    col_mid: Tuple[float, float, float],
    col_ochre: Tuple[float, float, float],
    col_moss: Tuple[float, float, float],
    shadow_rgb: Tuple[float, float, float] = (0.14, 0.18, 0.28),
    macro_scale: float = 0.55,
    crack_scale: float = 1.85,
    grain_scale: float = 18.0,
    z_strata_stretch: float = 2.4,
    bump_strength: float = 0.45,
) -> bpy.types.Material:
    """
    True Natural Multi-Octave Geology Shader (ZERO corrugated cardboard stripes AND ZERO giraffe Voronoi cells!):
    Object Coordinates -> Distorted Sedimentary Strata Noise + Medium Weathering Patch Noise
    + Fine Sand Grain Grit -> Rich organic stone ColorRamp + subtle mossy patch staining + dual-stage tactile Bump!
    """
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()

    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, z_strata_stretch)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])

    # 1. Broad sedimentary strata noise (distorted organic layers)
    n_macro = n.new("ShaderNodeTexNoise")
    n_macro.inputs["Scale"].default_value = macro_scale
    n_macro.inputs["Detail"].default_value = 10.0
    n_macro.inputs["Roughness"].default_value = 0.66
    n_macro.inputs["Distortion"].default_value = 0.65
    l.new(mp.outputs["Vector"], n_macro.inputs["Vector"])

    # 2. Medium weathered mineral patch noise (organic mottled limestone/sandstone variation)
    n_med = n.new("ShaderNodeTexNoise")
    n_med.inputs["Scale"].default_value = macro_scale * 3.4
    n_med.inputs["Detail"].default_value = 8.0
    n_med.inputs["Roughness"].default_value = 0.62
    n_med.inputs["Distortion"].default_value = 0.25
    l.new(tc.outputs["Object"], n_med.inputs["Vector"])

    # 3. Micro sandstone/limestone sand grain grit
    n_grain = n.new("ShaderNodeTexNoise")
    n_grain.inputs["Scale"].default_value = grain_scale
    n_grain.inputs["Detail"].default_value = 6.0
    n_grain.inputs["Roughness"].default_value = 0.72
    l.new(tc.outputs["Object"], n_grain.inputs["Vector"])

    # Combine macro strata (0.58) + medium weathering (0.26) + fine sand grit (0.16)
    mix_1 = n.new("ShaderNodeMath")
    mix_1.operation = "MULTIPLY_ADD"
    mix_1.inputs[1].default_value = 0.64
    l.new(n_macro.outputs["Fac"], mix_1.inputs[0])
    m_med = n.new("ShaderNodeMath")
    m_med.operation = "MULTIPLY"
    m_med.inputs[1].default_value = 0.36
    l.new(n_med.outputs["Fac"], m_med.inputs[0])
    l.new(m_med.outputs["Value"], mix_1.inputs[2])

    mix_h = n.new("ShaderNodeMath")
    mix_h.operation = "MULTIPLY_ADD"
    mix_h.inputs[1].default_value = 0.82
    l.new(mix_1.outputs["Value"], mix_h.inputs[0])
    m_gr = n.new("ShaderNodeMath")
    m_gr.operation = "MULTIPLY"
    m_gr.inputs[1].default_value = 0.18
    l.new(n_grain.outputs["Fac"], m_gr.inputs[0])
    l.new(m_gr.outputs["Value"], mix_h.inputs[2])

    # Rich natural stone ColorRamp (crevice dark -> base rock -> sunlit warm ochre)
    stone_ramp = n.new("ShaderNodeValToRGB")
    e = stone_ramp.color_ramp.elements
    e[0].position, e[0].color = 0.26, _srgb_to_linear(col_crevice)
    e[1].position, e[1].color = 0.54, _srgb_to_linear(col_mid)
    e2 = e.new(0.80)
    e2.color = _srgb_to_linear(col_ochre)
    l.new(mix_h.outputs["Value"], stone_ramp.inputs["Fac"])

    # Subtle organic moss/mineral patches (soft low-frequency noise, NEVER grid lines!)
    moss_ramp = n.new("ShaderNodeValToRGB")
    moss_ramp.color_ramp.elements[0].position = 0.62
    moss_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    moss_ramp.color_ramp.elements[1].position = 0.86
    moss_ramp.color_ramp.elements[1].color = (0.35, 0.35, 0.35, 1.0)
    l.new(n_med.outputs["Fac"], moss_ramp.inputs["Fac"])

    mix_moss = n.new("ShaderNodeMix")
    mix_moss.data_type = "RGBA"
    l.new(moss_ramp.outputs["Color"], mix_moss.inputs["Factor"])
    l.new(stone_ramp.outputs["Color"], mix_moss.inputs["A"])
    mix_moss.inputs["B"].default_value = _srgb_to_linear(col_moss)

    # Dual-stage organic rock Bump (broad geological strata + crisp micro sand grit!)
    bump1 = n.new("ShaderNodeBump")
    bump1.inputs["Strength"].default_value = bump_strength * 0.65
    bump1.inputs["Distance"].default_value = 0.14
    l.new(mix_1.outputs["Value"], bump1.inputs["Height"])

    bump2 = n.new("ShaderNodeBump")
    bump2.inputs["Strength"].default_value = bump_strength * 0.45
    bump2.inputs["Distance"].default_value = 0.04
    l.new(n_grain.outputs["Fac"], bump2.inputs["Height"])
    l.new(bump1.outputs["Normal"], bump2.inputs["Normal"])

    _wire_cel_surface(
        nt, mix_moss.outputs["Result"], bump2.outputs["Normal"],
        shadow_rgb=shadow_rgb, highlight_rgb=(0.98, 0.88, 0.72),
        roughness=0.90, rim_strength=0.14,
    )
    return mat


def make_desert_sand_material(name: str = "Mat_RedDesertSand") -> bpy.types.Material:
    """Authentic Australian Outback red-ochre dusty soil & wind-rippled desert sand (ZERO rock grid!)."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()

    tc = n.new("ShaderNodeTexCoord")
    mp_rip = n.new("ShaderNodeMapping")
    mp_rip.inputs["Scale"].default_value = (0.28, 1.45, 1.0)
    l.new(tc.outputs["Object"], mp_rip.inputs["Vector"])

    n_macro = n.new("ShaderNodeTexNoise")
    n_macro.inputs["Scale"].default_value = 0.14
    n_macro.inputs["Detail"].default_value = 7.0
    n_macro.inputs["Roughness"].default_value = 0.58
    n_macro.inputs["Distortion"].default_value = 0.35
    l.new(mp_rip.outputs["Vector"], n_macro.inputs["Vector"])

    n_grit = n.new("ShaderNodeTexNoise")
    n_grit.inputs["Scale"].default_value = 16.0
    n_grit.inputs["Detail"].default_value = 6.0
    n_grit.inputs["Roughness"].default_value = 0.72
    l.new(tc.outputs["Object"], n_grit.inputs["Vector"])

    sand_ramp = n.new("ShaderNodeValToRGB")
    e = sand_ramp.color_ramp.elements
    e[0].position, e[0].color = 0.25, _srgb_to_linear((0.58, 0.24, 0.12))  # Deep terracotta red earth
    e[1].position, e[1].color = 0.55, _srgb_to_linear((0.78, 0.36, 0.18))  # Classic Coober Pedy red ochre
    e2 = e.new(0.84)
    e2.color = _srgb_to_linear((0.89, 0.52, 0.28))                        # Sun-baked sandy ochre dust
    l.new(n_macro.outputs["Fac"], sand_ramp.inputs["Fac"])

    bump1 = n.new("ShaderNodeBump")
    bump1.inputs["Strength"].default_value = 0.18
    bump1.inputs["Distance"].default_value = 0.08
    l.new(n_macro.outputs["Fac"], bump1.inputs["Height"])

    bump2 = n.new("ShaderNodeBump")
    bump2.inputs["Strength"].default_value = 0.24
    bump2.inputs["Distance"].default_value = 0.025
    l.new(n_grit.outputs["Fac"], bump2.inputs["Height"])
    l.new(bump1.outputs["Normal"], bump2.inputs["Normal"])

    _wire_cel_surface(
        nt, sand_ramp.outputs["Color"], bump2.outputs["Normal"],
        shadow_rgb=(0.38, 0.16, 0.14), highlight_rgb=(1.0, 0.84, 0.62),
        roughness=0.92, rim_strength=0.06,
    )
    return mat


def make_snow_mountain_material(name: str = "Mat_ChugachMountain") -> bpy.types.Material:
    """Alaskan Glacier Peak shader: Exposed blue-grey slate granite cliffs on steep faces + rich snow ridges!"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()

    geom = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(geom.outputs["Normal"], sep.inputs["Vector"])

    tc = n.new("ShaderNodeTexCoord")
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.28
    noise.inputs["Detail"].default_value = 9.0
    noise.inputs["Roughness"].default_value = 0.68
    noise.inputs["Distortion"].default_value = 0.4
    l.new(tc.outputs["Object"], noise.inputs["Vector"])

    # Slope + Noise mask: upward ridges & gullies collect thick snow, steeper faces expose misty blue-grey granite!
    add_n = n.new("ShaderNodeMath")
    add_n.operation = "ADD"
    l.new(sep.outputs["Z"], add_n.inputs[0])
    mul_n = n.new("ShaderNodeMath")
    mul_n.operation = "MULTIPLY"
    mul_n.inputs[1].default_value = 0.48
    l.new(noise.outputs["Fac"], mul_n.inputs[0])
    l.new(mul_n.outputs["Value"], add_n.inputs[1])

    ramp = n.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.36, _srgb_to_linear((0.28, 0.37, 0.49))  # Misty Alaskan slate granite
    e[1].position, e[1].color = 0.62, _srgb_to_linear((0.92, 0.96, 1.00))  # Crisp glacier snow
    l.new(add_n.outputs["Value"], ramp.inputs["Fac"])

    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.58
    bump.inputs["Distance"].default_value = 0.45
    l.new(noise.outputs["Fac"], bump.inputs["Height"])

    _wire_cel_surface(
        nt, ramp.outputs["Color"], bump.outputs["Normal"],
        shadow_rgb=(0.28, 0.40, 0.58), highlight_rgb=(0.94, 0.98, 1.0),
        roughness=0.78, rim_strength=0.16,
    )
    return mat


def make_cobblestone_material(name: str = "Mat_SetenilCobble") -> bpy.types.Material:
    """Authentic Andalusian individual cobblestone pavers with dark mortar grout & per-stone variation!"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()

    tc = n.new("ShaderNodeTexCoord")
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (3.8, 3.8, 1.0)
    l.new(tc.outputs["Object"], mp.inputs["Vector"])

    vor_edge = n.new("ShaderNodeTexVoronoi")
    vor_edge.feature = "DISTANCE_TO_EDGE"
    vor_edge.inputs["Scale"].default_value = 1.65
    vor_edge.inputs["Randomness"].default_value = 0.65
    l.new(mp.outputs["Vector"], vor_edge.inputs["Vector"])

    vor_col = n.new("ShaderNodeTexVoronoi")
    vor_col.feature = "F1"
    vor_col.inputs["Scale"].default_value = 1.65
    vor_col.inputs["Randomness"].default_value = 0.65
    l.new(mp.outputs["Vector"], vor_col.inputs["Vector"])

    grout = n.new("ShaderNodeValToRGB")
    grout.color_ramp.elements[0].position = 0.04
    grout.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    grout.color_ramp.elements[1].position = 0.14
    grout.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    l.new(vor_edge.outputs["Distance"], grout.inputs["Fac"])

    stone_tint = n.new("ShaderNodeValToRGB")
    stone_tint.color_ramp.elements[0].position = 0.1
    stone_tint.color_ramp.elements[0].color = _srgb_to_linear((0.46, 0.42, 0.39))
    stone_tint.color_ramp.elements[1].position = 0.9
    stone_tint.color_ramp.elements[1].color = _srgb_to_linear((0.68, 0.62, 0.55))
    l.new(vor_col.outputs["Color"], stone_tint.inputs["Fac"])

    mix_g = n.new("ShaderNodeMix")
    mix_g.data_type = "RGBA"
    l.new(grout.outputs["Color"], mix_g.inputs["Factor"])
    mix_g.inputs["A"].default_value = _srgb_to_linear((0.18, 0.16, 0.16))  # Recessed mortar grout
    l.new(stone_tint.outputs["Color"], mix_g.inputs["B"])

    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.52
    bump.inputs["Distance"].default_value = 0.06
    l.new(grout.outputs["Color"], bump.inputs["Height"])

    _wire_cel_surface(
        nt, mix_g.outputs["Result"], bump.outputs["Normal"],
        shadow_rgb=(0.20, 0.22, 0.34), highlight_rgb=(1.0, 0.92, 0.78),
        roughness=0.46, rim_strength=0.12,
    )
    return mat


def make_cel_material(
    name: str,
    base_rgb: Tuple[float, float, float],
    shadow_rgb: Tuple[float, float, float] = (0.14, 0.22, 0.36),
    highlight_rgb: Tuple[float, float, float] | None = None,
    roughness: float = 0.72,
    metallic: float = 0.0,
    tex_type: str = "noise",
    tex_scale: float = 8.0,
    tex_contrast: float = 0.14,
    bump_strength: float = 0.15,
    emission_rgb: Tuple[float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    if tex_type == "speckle_linoleum":
        tex = nodes.new("ShaderNodeTexVoronoi")
        tex.feature = "F1"
        tex.inputs["Scale"].default_value = tex_scale
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Color"]
    elif tex_type == "brick":
        tex = nodes.new("ShaderNodeTexBrick")
        tex.inputs["Scale"].default_value = tex_scale
        tex.inputs["Mortar Size"].default_value = 0.03
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Fac"]
    elif tex_type == "wood":
        mapping.inputs["Scale"].default_value = (1.0, 1.0, 5.5)
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = tex_scale
        tex.inputs["Detail"].default_value = 7.0
        tex.inputs["Distortion"].default_value = 1.4
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Fac"]
    else:
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = tex_scale
        tex.inputs["Detail"].default_value = 6.0
        tex.inputs["Roughness"].default_value = 0.62
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Fac"]

    dark_var = tuple(max(0.0, v * (1.0 - tex_contrast)) for v in base_rgb)
    light_var = tuple(min(1.0, v * (1.0 + tex_contrast * 0.7)) for v in base_rgb)
    mix_col = nodes.new("ShaderNodeMix")
    mix_col.data_type = "RGBA"
    mix_col.inputs["A"].default_value = _srgb_to_linear(dark_var)
    mix_col.inputs["B"].default_value = _srgb_to_linear(light_var)
    links.new(fac_out, mix_col.inputs["Factor"])

    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.06
    links.new(fac_out, bump.inputs["Height"])

    _wire_cel_surface(
        nt, mix_col.outputs["Result"], bump.outputs["Normal"],
        shadow_rgb=shadow_rgb,
        highlight_rgb=highlight_rgb if highlight_rgb else (1.0, 0.96, 0.88),
        roughness=roughness, metallic=metallic,
        emission_rgb=emission_rgb, emission_strength=emission_strength,
        rim_strength=0.18 if emission_strength == 0.0 else 0.0,
    )
    return mat


def make_opal_iridescent_material(name: str = "Mat_Opal_Vein") -> bpy.types.Material:
    """Sharp multi-faceted Coober Pedy rainbow Opal crystal cluster (Blue -> Turquoise -> Emerald -> Magenta)!"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()

    out = n.new("ShaderNodeOutputMaterial")
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.48
    vor = n.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 28.0
    tc = n.new("ShaderNodeTexCoord")
    l.new(tc.outputs["Object"], vor.inputs["Vector"])

    add_n = n.new("ShaderNodeMath")
    add_n.operation = "ADD"
    l.new(lw.outputs["Facing"], add_n.inputs[0])
    l.new(vor.outputs["Distance"], add_n.inputs[1])

    ramp = n.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.12, _srgb_to_linear((0.04, 0.30, 1.00))
    e[1].position, e[1].color = 0.44, _srgb_to_linear((0.04, 0.98, 0.82))
    e2 = e.new(0.72)
    e2.color = _srgb_to_linear((0.18, 1.00, 0.38))
    e3 = e.new(0.94)
    e3.color = _srgb_to_linear((0.96, 0.18, 0.98))
    l.new(add_n.outputs["Value"], ramp.inputs["Fac"])

    bsdf = n.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.08
    bsdf.inputs["Metallic"].default_value = 0.35
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Emission Strength"].default_value = 3.8
    l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    l.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_glass_material(name: str = "Mat_Frosted_Glass", tint=(0.76, 0.88, 0.96), alpha: float = 0.32) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    bsdf = n.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = _srgb_to_linear(tint)
    bsdf.inputs["Roughness"].default_value = 0.10
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["Specular IOR Level"].default_value = 0.85
    l.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_volumetric_beam_material(name: str, rgb=(1.0, 0.86, 0.56), strength: float = 0.14) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    transp = n.new("ShaderNodeBsdfTransparent")
    em = n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = _srgb_to_linear(rgb)
    em.inputs["Strength"].default_value = 1.4

    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.55
    inv = n.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    l.new(lw.outputs["Facing"], inv.inputs[1])

    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    l.new(inv.outputs["Value"], mul.inputs[0])

    mix = n.new("ShaderNodeMixShader")
    l.new(mul.outputs["Value"], mix.inputs["Fac"])
    l.new(transp.outputs["BSDF"], mix.inputs[1])
    l.new(em.outputs["Emission"], mix.inputs[2])
    l.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat


def make_sign_material(name: str, img_path: Path, emission_boost: float = 0.15) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    tex = n.new("ShaderNodeTexImage")
    img = bpy.data.images.load(str(img_path), check_existing=True)
    img.pack()
    tex.image = img
    em = n.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.90 + emission_boost
    l.new(tex.outputs["Color"], em.inputs["Color"])
    l.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def make_character_card_material(name: str, default_img_path: Path) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()

    out = n.new("ShaderNodeOutputMaterial")
    tex = n.new("ShaderNodeTexImage")
    tex.name = "CharTex"
    tex.extension = "CLIP"
    if default_img_path.exists():
        tex.image = bpy.data.images.load(str(default_img_path), check_existing=True)

    tint = n.new("ShaderNodeMix")
    tint.name = "EnvTint"
    tint.data_type = "RGBA"
    tint.blend_type = "MULTIPLY"
    tint.inputs["Factor"].default_value = 0.20
    tint.inputs["B"].default_value = (1.0, 1.0, 1.0, 1.0)
    l.new(tex.outputs["Color"], tint.inputs["A"])

    em = n.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.04
    l.new(tint.outputs["Result"], em.inputs["Color"])

    # Camera sees sharp 2.5D ink cel art; shadow rays see solid opaque diffuse silhouette (casts true 3D shadow!)
    lp = n.new("ShaderNodeLightPath")
    diff = n.new("ShaderNodeBsdfDiffuse")
    l.new(tint.outputs["Result"], diff.inputs["Color"])
    cam_mix = n.new("ShaderNodeMixShader")
    l.new(lp.outputs["Is Camera Ray"], cam_mix.inputs["Fac"])
    l.new(diff.outputs["BSDF"], cam_mix.inputs[1])
    l.new(em.outputs["Emission"], cam_mix.inputs[2])

    transp = n.new("ShaderNodeBsdfTransparent")
    mix_sh = n.new("ShaderNodeMixShader")
    l.new(tex.outputs["Alpha"], mix_sh.inputs["Fac"])
    l.new(transp.outputs["BSDF"], mix_sh.inputs[1])
    l.new(cam_mix.outputs["Shader"], mix_sh.inputs[2])
    l.new(mix_sh.outputs["Shader"], out.inputs["Surface"])
    return mat


def create_natural_worlds() -> dict[str, bpy.types.World]:
    """
    Create 3 Physically-Grounded Natural Sky Worlds (swapped dynamically per scene!):
      1. World_Whittier_Arctic  : Layered volumetric-look cloud overcast gradient in cool Arctic slate-blue + mist!
      2. World_CooberPedy_Desert: Physical Nishita Sky (high Outback sun, high desert dust -> warm hazy horizon!)
      3. World_Setenil_Golden   : Physical Nishita Sky (12° Spanish Golden Hour low sun slicing into alley!)
      4. World_Interior_Cozy    : Dark controlled warm indirect bounce for enclosed lobby/tunnel/dugout!
    """
    worlds: dict[str, bpy.types.World] = {}

    # 1. Whittier Arctic Cloud Overcast Sky
    w1 = bpy.data.worlds.new("World_Whittier_Arctic")
    w1.use_nodes = True
    n, l = w1.node_tree.nodes, w1.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputWorld")
    bg = n.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.05
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs["Vector"])

    # Soft multi-layer Arctic cloud strata
    mp = n.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.6, 1.6, 5.5)
    l.new(tc.outputs["Generated"], mp.inputs["Vector"])
    cld = n.new("ShaderNodeTexNoise")
    cld.inputs["Scale"].default_value = 4.2
    cld.inputs["Detail"].default_value = 7.0
    cld.inputs["Roughness"].default_value = 0.62
    l.new(mp.outputs["Vector"], cld.inputs["Vector"])

    sky_grad = n.new("ShaderNodeValToRGB")
    sky_grad.color_ramp.elements[0].position = 0.02
    sky_grad.color_ramp.elements[0].color = _srgb_to_linear((0.68, 0.78, 0.88))  # Misty icy horizon
    sky_grad.color_ramp.elements[1].position = 0.45
    sky_grad.color_ramp.elements[1].color = _srgb_to_linear((0.32, 0.44, 0.62))  # Deep Arctic slate-blue sky
    l.new(sep.outputs["Z"], sky_grad.inputs["Fac"])

    mix_cld = n.new("ShaderNodeMix")
    mix_cld.data_type = "RGBA"
    cld_ramp = n.new("ShaderNodeValToRGB")
    cld_ramp.color_ramp.elements[0].position = 0.42
    cld_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    cld_ramp.color_ramp.elements[1].position = 0.72
    cld_ramp.color_ramp.elements[1].color = (0.62, 0.62, 0.62, 1.0)
    l.new(cld.outputs["Fac"], cld_ramp.inputs["Fac"])
    l.new(cld_ramp.outputs["Color"], mix_cld.inputs["Factor"])
    l.new(sky_grad.outputs["Color"], mix_cld.inputs["A"])
    mix_cld.inputs["B"].default_value = _srgb_to_linear((0.86, 0.90, 0.95))  # Soft snow-cloud layer
    l.new(mix_cld.outputs["Result"], bg.inputs["Color"])
    l.new(bg.outputs["Background"], out.inputs["Surface"])
    worlds["whittier_ext"] = w1

    # 2. Coober Pedy Outback Nishita Physical Sky (Scorching midday sun + high red desert dust!)
    w2 = bpy.data.worlds.new("World_CooberPedy_Desert")
    w2.use_nodes = True
    n, l = w2.node_tree.nodes, w2.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputWorld")
    bg = n.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.38
    sky = n.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_disc = True
    sky.sun_elevation = math.radians(48.0)
    sky.sun_rotation = math.radians(-38.0)
    sky.air_density = 1.4
    sky.dust_density = 3.6
    sky.ozone_density = 1.2
    l.new(sky.outputs["Color"], bg.inputs["Color"])
    l.new(bg.outputs["Background"], out.inputs["Surface"])
    worlds["coober_desert"] = w2

    # 3. Setenil de las Bodegas Spanish Golden Hour Nishita Physical Sky (Low 12° Sun!)
    w3 = bpy.data.worlds.new("World_Setenil_Golden")
    w3.use_nodes = True
    n, l = w3.node_tree.nodes, w3.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputWorld")
    bg = n.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.55
    sky3 = n.new("ShaderNodeTexSky")
    sky3.sky_type = "NISHITA"
    sky3.sun_disc = True
    sky3.sun_elevation = math.radians(12.5)
    sky3.sun_rotation = math.radians(128.0)
    sky3.air_density = 1.6
    sky3.dust_density = 2.4
    sky3.ozone_density = 1.8
    l.new(sky3.outputs["Color"], bg.inputs["Color"])
    l.new(bg.outputs["Background"], out.inputs["Surface"])
    worlds["setenil"] = w3

    # 4. Controlled Cozy Interior Ambient World (Lobby / Tunnel / Dugout)
    w4 = bpy.data.worlds.new("World_Interior_Cozy")
    w4.use_nodes = True
    n, l = w4.node_tree.nodes, w4.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputWorld")
    bg = n.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = _srgb_to_linear((0.18, 0.14, 0.11))
    bg.inputs["Strength"].default_value = 0.25
    l.new(bg.outputs["Background"], out.inputs["Surface"])
    worlds["interior"] = w4

    return worlds
