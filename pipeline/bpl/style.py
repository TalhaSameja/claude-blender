"""Palette + material library. Everything is generated in-code, so every
asset is original by construction -- there is no third-party art to license."""
import bpy

# Pastel "toy city" palette, sampled to match the reference look.
PALETTE = {
    "sky":        (0.52, 0.78, 0.94),
    "ground":     (0.83, 0.83, 0.80),
    "road":       (0.42, 0.44, 0.47),
    "grass":      (0.56, 0.74, 0.46),
    "wall_a":     (0.94, 0.86, 0.68),
    "wall_b":     (0.86, 0.90, 0.84),
    "wall_c":     (0.95, 0.78, 0.74),
    "wall_d":     (0.78, 0.84, 0.92),
    "roof":       (0.80, 0.42, 0.34),
    "window":     (0.30, 0.46, 0.56),
    "hoodie":     (0.13, 0.40, 0.82),
    "skin":       (0.92, 0.76, 0.62),
    "hair":       (0.18, 0.14, 0.12),
    "trouser":    (0.80, 0.76, 0.66),
    "shoe":       (0.95, 0.95, 0.95),
    "trunk":      (0.45, 0.33, 0.24),
    "leaf":       (0.33, 0.60, 0.33),
    "accent":     (0.98, 0.78, 0.18),
    "white":      (0.95, 0.95, 0.95),
    "black":      (0.08, 0.08, 0.09),
}

# Muted retro palette, sampled from the @ro14z_3f reference: desaturated
# sage/teal/cream with rust accents. Reads as "film stock", not "toy".
RETRO = {
    "sky":     (0.78, 0.80, 0.74),
    "ground":  (0.72, 0.73, 0.64),
    "road":    (0.52, 0.53, 0.49),
    "grass":   (0.63, 0.67, 0.50),
    "wall_a":  (0.87, 0.82, 0.70),
    "wall_b":  (0.74, 0.78, 0.74),
    "wall_c":  (0.80, 0.56, 0.44),
    "wall_d":  (0.40, 0.56, 0.56),
    "roof":    (0.66, 0.34, 0.28),
    "window":  (0.38, 0.50, 0.50),
    "hoodie":  (0.18, 0.22, 0.28),
    "skin":    (0.85, 0.72, 0.60),
    "hair":    (0.16, 0.14, 0.14),
    "trouser": (0.24, 0.26, 0.30),
    "shoe":    (0.14, 0.13, 0.13),
    "trunk":   (0.44, 0.35, 0.27),
    "leaf":    (0.47, 0.55, 0.40),
    "accent":  (0.84, 0.44, 0.24),
    "white":   (0.90, 0.89, 0.84),
    "black":   (0.10, 0.10, 0.11),
}

THEMES = {"pastel": None, "retro": RETRO}
_active = "pastel"
_base = dict(PALETTE)


def use_theme(name):
    """Swap the whole palette. Episodes set this once; every material built
    afterwards picks up the new colours."""
    global _active
    _active = name
    PALETTE.clear()
    PALETTE.update(_base)
    if THEMES.get(name):
        PALETTE.update(THEMES[name])
    reset_cache()


_cache = {}


def _srgb_to_linear(c):
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(name, rgb=None, shading="soft", roughness=0.75):
    """Return a cached material.

    shading="flat" -> pure emission. Zero light bounces needed, fastest.
    shading="soft" -> diffuse, lit by the key sun. Still cheap because the
                      scene renders with max_bounces=0 (direct light only).
    """
    key = (name, shading)
    if key in _cache and _cache[key].name in bpy.data.materials:
        return _cache[key]
    rgb = rgb if rgb is not None else PALETTE.get(name, (0.8, 0.8, 0.8))
    rgb = _srgb_to_linear(rgb)
    m = bpy.data.materials.new(f"{name}_{shading}")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if shading == "flat":
        sh = nt.nodes.new("ShaderNodeEmission")
        sh.inputs["Color"].default_value = (*rgb, 1)
    else:
        sh = nt.nodes.new("ShaderNodeBsdfDiffuse")
        sh.inputs["Color"].default_value = (*rgb, 1)
        sh.inputs["Roughness"].default_value = roughness
    nt.links.new(sh.outputs[0], out.inputs["Surface"])
    _cache[key] = m
    return m


def paint(obj, name, shading="soft", rgb=None):
    obj.data.materials.clear()
    obj.data.materials.append(mat(name, rgb, shading))
    return obj


def reset_cache():
    _cache.clear()
