"""Procedural set dressing. Primitives only -- no imported assets, so the
whole visual library is original work the channel owns outright."""
import bpy, random, math
from .style import paint, PALETTE

WALLS = ["wall_a", "wall_b", "wall_c", "wall_d"]


def _add(primitive, **kw):
    getattr(bpy.ops.mesh, primitive)(**kw)
    return bpy.context.object


def ground(size=120, color="ground"):
    g = _add("primitive_plane_add", size=size)
    return paint(g, color)


def box(loc, scale, color, name="box"):
    b = _add("primitive_cube_add", size=1, location=loc)
    b.scale = scale
    b.name = name
    return paint(b, color)


def building(loc, w=4, d=4, floors=3, color=None, seed=0):
    """A blocky pastel building with window strips."""
    rnd = random.Random(seed)
    color = color or rnd.choice(WALLS)
    h = floors * 1.6
    parts = [box((loc[0], loc[1], h / 2), (w, d, h), color, "wall")]
    for f in range(floors):
        z = 0.9 + f * 1.6
        for sx, sy, rot in ((0, -d / 2, 0), (0, d / 2, 0)):
            win = box((loc[0] + sx, loc[1] + sy, z), (w * 0.62, 0.06, 0.7),
                      "window", "win")
    return parts


def tree(loc, h=2.6, seed=0):
    rnd = random.Random(seed)
    t = _add("primitive_cylinder_add", vertices=8, radius=0.13, depth=h,
             location=(loc[0], loc[1], h / 2))
    paint(t, "trunk")
    crown = _add("primitive_ico_sphere_add", subdivisions=2,
                 radius=0.75 + rnd.random() * 0.25,
                 location=(loc[0], loc[1], h + 0.35))
    crown.scale = (1, 1, 1.15)
    bpy.ops.object.shade_smooth()
    paint(crown, "leaf")
    return t, crown


def road(length=120, width=7):
    r = box((0, 0, 0.02), (width, length, 0.04), "road", "road")
    for i in range(-int(length // 2), int(length // 2), 4):
        box((0, i, 0.05), (0.18, 1.6, 0.02), "white", "dash")
    return r


def street(n=6, spacing=9, seed=1):
    """Two rows of buildings with trees, flanking a road down +Y."""
    ground()
    road()
    rnd = random.Random(seed)
    for i in range(n):
        y = -n * spacing / 2 + i * spacing + spacing / 2
        for side in (-1, 1):
            x = side * (7 + rnd.random() * 1.5)
            building((x, y, 0), w=5, d=6,
                     floors=rnd.randint(2, 5), seed=seed * 31 + i * 7 + side)
        tree((side * 5.0, y - spacing / 2, 0), seed=i)
        tree((-5.0, y + spacing / 3, 0), seed=i + 50)


def suitcase(loc=(0, 0, 0), rot=(0, 0, 0), color="hoodie", scale=1.0):
    """Hero prop: a wheeled case, built from boxes + cylinders.

    Parts are built at LOCAL offsets around the origin and then parented to an
    empty that carries the world placement -- building them at `loc` and also
    moving the parent would double the offset."""
    parts = []
    loc0 = (0.0, 0.0, 0.0)
    body = box((loc0[0], loc0[1], loc0[2] + 0.45 * scale),
               (0.52 * scale, 0.22 * scale, 0.78 * scale), color, "case")
    parts.append(body)
    for sx in (-0.34, 0.34):
        for sy in (-0.07, 0.07):
            w = _add("primitive_cylinder_add", vertices=12, radius=0.07 * scale,
                     depth=0.06 * scale,
                     location=(loc0[0] + sx * scale, loc0[1] + sy * scale,
                               loc0[2] + 0.07 * scale),
                     rotation=(0, math.pi / 2, 0))
            parts.append(paint(w, "black"))
    handle = box((loc0[0], loc0[1], loc0[2] + 1.0 * scale),
                 (0.30 * scale, 0.04 * scale, 0.12 * scale), "black", "handle")
    parts.append(handle)
    grp = bpy.data.objects.new("suitcase", None)
    bpy.context.collection.objects.link(grp)
    grp.location = loc
    grp.rotation_euler = rot
    for p in parts:
        p.parent = grp
    return grp
