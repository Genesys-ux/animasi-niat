"""
Mid-Poly Cel-Shaded Semi-Realistic Material Library & Real-World Reference Signage Generator
for Blender 4.2 LTS (EEVEE Next).

Combines procedural realistic surface detail (concrete cracks, speckled linoleum, sandstone
tunnelling grooves, white stucco, cobblestone, red ochre dirt, wood grain, iridescent opal)
with crisp 3-band stylized cel-shading + Blue Shade cool shadows + Warm Rim highlights!
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
    """Return paths to pre-generated crisp PNG signage textures in production/textures/."""
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
    """
    Create a Mid-Poly Cel-Shaded Semi-Realistic EEVEE Next material:
    Realistic procedural surface texture + bump -> Principled BSDF -> ShaderToRGB
    -> Crisp 3-step stylized cel ramp blended with Blue Shade shadow tint & Rim Light!
    """
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (950, 0)

    # Coordinate + Procedural Surface Texture
    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-1000, 0)

    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-800, 0)
    links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    if tex_type == "wave_sandstone":
        # Authentic Coober Pedy tunnelling-machine parallel curved sandstone grooves!
        mapping.inputs["Scale"].default_value = (1.0, 1.0, 2.2)
        tex = nodes.new("ShaderNodeTexWave")
        tex.wave_type = "BANDS"
        tex.bands_direction = "Z"
        tex.inputs["Scale"].default_value = tex_scale
        tex.inputs["Distortion"].default_value = 3.2
        tex.inputs["Detail"].default_value = 4.0
        tex.inputs["Detail Roughness"].default_value = 0.6
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Fac"]
    elif tex_type == "brick":
        tex = nodes.new("ShaderNodeTexBrick")
        tex.inputs["Scale"].default_value = tex_scale
        tex.inputs["Mortar Size"].default_value = 0.035
        tex.inputs["Mortar Smooth"].default_value = 0.1
        tex.inputs["Color1"].default_value = _srgb_to_linear(base_rgb)
        tex.inputs["Color2"].default_value = _srgb_to_linear((base_rgb[0] * 0.86, base_rgb[1] * 0.86, base_rgb[2] * 0.88))
        tex.inputs["Mortar"].default_value = _srgb_to_linear((base_rgb[0] * 0.48, base_rgb[1] * 0.48, base_rgb[2] * 0.50))
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Fac"]
    elif tex_type == "voronoi_cobble":
        tex = nodes.new("ShaderNodeTexVoronoi")
        tex.feature = "DISTANCE_TO_EDGE"
        tex.inputs["Scale"].default_value = tex_scale
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Distance"]
    elif tex_type == "speckle_linoleum":
        tex = nodes.new("ShaderNodeTexVoronoi")
        tex.feature = "F1"
        tex.inputs["Scale"].default_value = tex_scale
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Color"]
    else:
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = tex_scale
        tex.inputs["Detail"].default_value = 6.0
        tex.inputs["Roughness"].default_value = 0.62
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        fac_out = tex.outputs["Fac"]
    tex.location = (-580, 120)

    # Mix Base Color with subtle procedural surface texture variation
    dark_var = (max(0.0, base_rgb[0] * (1.0 - tex_contrast)),
                max(0.0, base_rgb[1] * (1.0 - tex_contrast)),
                max(0.0, base_rgb[2] * (1.0 - tex_contrast)))
    light_var = (min(1.0, base_rgb[0] * (1.0 + tex_contrast * 0.7)),
                 min(1.0, base_rgb[1] * (1.0 + tex_contrast * 0.7)),
                 min(1.0, base_rgb[2] * (1.0 + tex_contrast * 0.7)))

    mix_col = nodes.new("ShaderNodeMix")
    mix_col.data_type = "RGBA"
    mix_col.location = (-340, 180)
    mix_col.inputs["A"].default_value = _srgb_to_linear(dark_var)
    mix_col.inputs["B"].default_value = _srgb_to_linear(light_var)
    links.new(fac_out, mix_col.inputs["Factor"])

    # Fast Ambient Occlusion -> Crisp Blue Shade in crevices & contact zones (1 sample = 8x faster in Cycles!)
    ao = nodes.new("ShaderNodeAmbientOcclusion")
    ao.samples = 1
    ao.inputs["Distance"].default_value = 1.4
    ao.location = (-340, 380)
    links.new(mix_col.outputs["Result"], ao.inputs["Color"])

    ao_ramp = nodes.new("ShaderNodeValToRGB")
    ao_ramp.location = (-120, 380)
    ao_ramp.color_ramp.elements[0].position = 0.22
    ao_ramp.color_ramp.elements[0].color = _srgb_to_linear(shadow_rgb)
    ao_ramp.color_ramp.elements[1].position = 0.78
    ao_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(ao.outputs["AO"], ao_ramp.inputs["Fac"])

    albedo_ao = nodes.new("ShaderNodeMix")
    albedo_ao.data_type = "RGBA"
    albedo_ao.blend_type = "MULTIPLY"
    albedo_ao.inputs["Factor"].default_value = 0.72
    albedo_ao.location = (120, 260)
    links.new(mix_col.outputs["Result"], albedo_ao.inputs["A"])
    links.new(ao_ramp.outputs["Color"], albedo_ao.inputs["B"])

    # Bump for realistic surface relief (stucco, sandstone grooves, concrete, cobblestone)
    bump = nodes.new("ShaderNodeBump")
    bump.location = (-340, -140)
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.08
    links.new(fac_out, bump.inputs["Height"])

    # Stylized Cel-Shaded Diffuse Toon BSDF (crisp stepped light-shadow terminator!)
    toon = nodes.new("ShaderNodeBsdfToon")
    toon.component = "DIFFUSE"
    toon.location = (320, 240)
    toon.inputs["Size"].default_value = 0.68
    toon.inputs["Smooth"].default_value = 0.14
    links.new(albedo_ao.outputs["Result"], toon.inputs["Color"])
    links.new(bump.outputs["Normal"], toon.inputs["Normal"])

    # Semi-Realistic Principled BSDF (adds subtle specular, metallic sheen & physical bounce!)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (320, -20)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    links.new(albedo_ao.outputs["Result"], bsdf.inputs["Base Color"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    if emission_rgb and emission_strength > 0.0:
        bsdf.inputs["Emission Color"].default_value = _srgb_to_linear(emission_rgb)
        bsdf.inputs["Emission Strength"].default_value = emission_strength * 2.2

    # Blend 58% Crisp Toon Cel + 42% Semi-Realistic Principled (pure metal stays more Principled!)
    cel_mix = nodes.new("ShaderNodeMixShader")
    cel_mix.location = (620, 120)
    cel_mix.inputs["Fac"].default_value = 0.85 if (metallic > 0.4 or emission_strength > 0.0) else 0.42
    links.new(toon.outputs["BSDF"], cel_mix.inputs[1])
    links.new(bsdf.outputs["BSDF"], cel_mix.inputs[2])

    # Crisp Warm Fresnel Rim Highlight on silhouettes (enhances 3D mid-poly depth separation!)
    lw = nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.24
    lw.location = (340, -320)
    rim_ramp = nodes.new("ShaderNodeValToRGB")
    rim_ramp.location = (520, -320)
    rim_ramp.color_ramp.elements[0].position = 0.68
    rim_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    rim_ramp.color_ramp.elements[1].position = 0.88
    rim_ramp.color_ramp.elements[1].color = (0.24, 0.24, 0.24, 1.0)
    links.new(lw.outputs["Facing"], rim_ramp.inputs["Fac"])

    hi = highlight_rgb if highlight_rgb else (1.0, 0.96, 0.88)
    rim_em = nodes.new("ShaderNodeEmission")
    rim_em.location = (620, -180)
    rim_em.inputs["Color"].default_value = _srgb_to_linear(hi)
    rim_em.inputs["Strength"].default_value = 1.15

    final_sh = nodes.new("ShaderNodeMixShader")
    final_sh.location = (800, 40)
    links.new(rim_ramp.outputs["Color"], final_sh.inputs["Fac"])
    links.new(cel_mix.outputs["Shader"], final_sh.inputs[1])
    links.new(rim_em.outputs["Emission"], final_sh.inputs[2])

    links.new(final_sh.outputs["Shader"], out.inputs["Surface"])
    return mat


def make_opal_iridescent_material(name: str = "Mat_Opal_Vein") -> bpy.types.Material:
    """Dazzling Coober Pedy blue-green-magenta iridescent opal vein shader!"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    n.clear()

    out = n.new("ShaderNodeOutputMaterial")
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.42
    vor = n.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 26.0
    tc = n.new("ShaderNodeTexCoord")
    l.new(tc.outputs["Object"], vor.inputs["Vector"])

    math_add = n.new("ShaderNodeMath")
    math_add.operation = "ADD"
    l.new(lw.outputs["Facing"], math_add.inputs[0])
    l.new(vor.outputs["Distance"], math_add.inputs[1])

    ramp = n.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.15, _srgb_to_linear((0.05, 0.32, 0.98))
    e[1].position, e[1].color = 0.48, _srgb_to_linear((0.08, 0.96, 0.78))
    e2 = e.new(0.75)
    e2.color = _srgb_to_linear((0.22, 0.98, 0.44))
    e3 = e.new(0.95)
    e3.color = _srgb_to_linear((0.92, 0.24, 0.96))
    l.new(math_add.outputs["Value"], ramp.inputs["Fac"])

    em = n.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 3.6
    l.new(ramp.outputs["Color"], em.inputs["Color"])
    l.new(em.outputs["Emission"], out.inputs["Surface"])
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
    bsdf.inputs["Roughness"].default_value = 0.12
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["Specular IOR Level"].default_value = 0.85
    l.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_volumetric_beam_material(name: str, rgb=(1.0, 0.86, 0.56), strength: float = 0.22) -> bpy.types.Material:
    """Clean, soft edge-faded volumetric God Ray / Flashlight cone (zero white-out!)."""
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
    em.inputs["Strength"].default_value = 1.6

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


def make_sign_material(name: str, img_path: Path, emission_boost: float = 0.18) -> bpy.types.Material:
    """Crisp UV-mapped signage material with subtle self-illumination for clean readability."""
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
    em.inputs["Strength"].default_value = 0.92 + emission_boost
    l.new(tex.outputs["Color"], em.inputs["Color"])
    l.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def make_character_card_material(name: str, default_img_path: Path) -> bpy.types.Material:
    """
    Hybrid 2.5D-in-3D Character Plane Shader:
    Preserves razor-sharp 2.5D variable-width ink outlines & cel fills while applying
    subtle environmental mood tinting via a driver/value node + transparent alpha cutout!
    """
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
        img = bpy.data.images.load(str(default_img_path), check_existing=True)
        tex.image = img

    tint = n.new("ShaderNodeMix")
    tint.name = "EnvTint"
    tint.data_type = "RGBA"
    tint.blend_type = "MULTIPLY"
    tint.inputs["Factor"].default_value = 0.22
    tint.inputs["B"].default_value = (1.0, 1.0, 1.0, 1.0)
    l.new(tex.outputs["Color"], tint.inputs["A"])

    em = n.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.05
    l.new(tint.outputs["Result"], em.inputs["Color"])

    # Prevent character card from emitting light onto nearby 3D walls while still casting real 3D shadows!
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
