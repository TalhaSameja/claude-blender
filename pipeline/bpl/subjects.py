"""Story props: the things an episode is ABOUT.

A line like "a cloud has been charged" has to be *shown* -- a narrator talking
over an empty street loses the viewer in three seconds. Everything here is
built from primitives like the rest of the kit, so it stays licence-clean.
"""
import bpy, math, random
from .style import paint, PALETTE
from . import kit

D = math.radians


def _ico(r, loc, subdiv=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=r,
                                          location=loc)
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    return o


def _group(name, parts, loc=(0, 0, 0), rot=(0, 0, 0)):
    g = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(g)
    for p in parts:
        p.parent = g
    g.location = loc
    g.rotation_euler = rot
    return g


def cloud(loc=(0, 0, 6), scale=1.0, seed=0, grumpy=True):
    """The hero character of the NOTHING NEWS pilot. Lobes of varying size so
    it does not read as a row of identical balls, plus eyes so the audience
    reads it as a defendant rather than weather."""
    rnd = random.Random(seed)
    parts = []
    lobes = [(-1.5, 0, 0, 0.85), (-0.6, 0.15, 0.18, 1.15), (0.5, -0.1, 0.1, 1.0),
             (1.5, 0.05, -0.05, 0.78), (0.0, 0.3, -0.28, 0.9),
             (-0.9, -0.25, -0.2, 0.72)]
    for lx, ly, lz, lr in lobes:
        r = lr * scale * (0.92 + rnd.random() * 0.16)
        o = _ico(r, (lx * scale, ly * scale, lz * scale))
        o.scale = (1.0, 0.82, 0.86)
        paint(o, "cloud_body", rgb=(0.93, 0.93, 0.95))
        parts.append(o)
    if grumpy:
        for sx in (-0.52, 0.52):
            e = _ico(0.13 * scale, (sx * scale, -0.78 * scale, 0.16 * scale), 2)
            paint(e, "black", shading="flat")
            parts.append(e)
        # flat brow bars read as "unimpressed" at thumbnail size
        for sx in (-0.52, 0.52):
            b = kit.box((sx * scale, -0.80 * scale, 0.36 * scale),
                        (0.30 * scale, 0.05 * scale, 0.07 * scale), "black")
            b.rotation_euler = (0, D(14 if sx < 0 else -14), 0)
            parts.append(b)
    return _group("cloud", parts, loc)


def rain(under=(0, 0, 5), w=3.0, d=2.0, drop=3.0, n=90, seed=0):
    rnd = random.Random(seed)
    parts = []
    for _ in range(n):
        x = under[0] + (rnd.random() - 0.5) * w
        y = under[1] + (rnd.random() - 0.5) * d
        z = under[2] - rnd.random() * drop
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=4, radius=0.016, depth=0.26 + rnd.random() * 0.2,
            location=(x, y, z))
        o = bpy.context.object
        paint(o, "rain", rgb=(0.62, 0.72, 0.82))
        parts.append(o)
    return _group("rain", parts)


def car(loc=(0, 0, 0), yaw=0, color="wall_d", seed=0):
    parts = []
    body = kit.box((0, 0, 0.42), (1.7, 3.6, 0.52), color, "car_body")
    cabin = kit.box((0, -0.15, 0.86), (1.45, 1.9, 0.5), color, "car_cabin")
    glass = kit.box((0, -0.15, 0.88), (1.49, 1.6, 0.36), "window", "glass")
    parts += [body, cabin, glass]
    for sx in (-0.86, 0.86):
        for sy in (-1.25, 1.25):
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=12, radius=0.33, depth=0.22,
                location=(sx, sy, 0.3), rotation=(0, D(90), 0))
            parts.append(paint(bpy.context.object, "black"))
    return _group("car", parts, loc, (0, 0, D(yaw)))


def car_park(rows=2, per_row=4, seed=3):
    """Tarmac, painted bays, and a few parked cars."""
    rnd = random.Random(seed)
    kit.box((0, 0, 0.01), (26, 26, 0.02), "road", "tarmac")
    cols = ["wall_d", "wall_c", "roof", "white", "wall_b"]
    for r in range(rows):
        y = -5 + r * 10
        for i in range(per_row):
            x = -9 + i * 5.2
            for bx in (x - 1.3, x + 1.3):       # bay lines
                kit.box((bx, y, 0.03), (0.12, 4.4, 0.02), "white", "bay")
            if rnd.random() < 0.72:
                car((x, y, 0), yaw=0, color=rnd.choice(cols), seed=r * 9 + i)
    for lx in (-12.5, 12.5):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.1, depth=6,
                                            location=(lx, 0, 3))
        paint(bpy.context.object, "black")
        kit.box((lx, 0, 6.1), (0.7, 0.3, 0.16), "accent", "lamp")


def microphone(loc=(0, 0, 0), yaw=0, color="black"):
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=1.1,
                                        location=(0, 0, 0.55))
    parts.append(paint(bpy.context.object, color))
    head = _ico(0.11, (0, -0.06, 1.14), 2)
    parts.append(paint(head, color))
    flag = kit.box((0, -0.06, 0.92), (0.19, 0.19, 0.16), "accent", "mic_flag")
    parts.append(flag)
    return _group("mic", parts, loc, (0, 0, D(yaw)))


def press_pack(target=(0, 0, 1.2), radius=1.5, n=5, seed=0):
    """A half-ring of microphones thrust toward the subject."""
    for i in range(n):
        a = D(-55 + i * (110 / max(1, n - 1)))
        x = target[0] + math.sin(a) * radius
        y = target[1] - math.cos(a) * radius
        m = microphone((x, y, 0), yaw=math.degrees(-a))
        m.rotation_euler = (D(-22), 0, D(math.degrees(a)))


def courtroom(seed=0, judge=True):
    """Judge's bench, dock, rail, flag, panelled walls.

    Floor, walls, panelling and bench are deliberately four different values
    -- at this shading level same-ish browns merge into one flat mass and the
    set stops reading as a room.
    """
    kit.box((0, 0, 0.02), (24, 24, 0.04), "court_floor", "floor")
    for (px, py, sx, sy) in ((0, 7.5, 24, 0.4), (-8, 0, 0.4, 16),
                             (8, 0, 0.4, 16)):
        kit.box((px, py, 3.4), (sx, sy, 6.8), "stone_light", "wall")
        # dado panelling breaks the wall up and gives the eye a horizon
        kit.box((px, py - (0.22 if py > 0 else 0), sx * 0 + 1.1),
                (sx * 0.995, sy * 0.995 + 0.12, 2.2), "wood", "panel")
    # bench on a riser
    kit.box((0, 5.4, 0.45), (9.0, 3.0, 0.9), "wood_dark", "riser")
    kit.box((0, 4.2, 1.55), (7.2, 0.5, 1.3), "wood_dark", "bench")
    kit.box((0, 4.9, 2.26), (7.4, 1.5, 0.16), "wood", "bench_top")
    # seal behind the judge
    sl = _ico(1.05, (0, 7.25, 4.6), 3)
    sl.scale = (1, 0.16, 1)
    paint(sl, "accent")
    if judge:
        from . import human
        r, j = human.build("judge", loc=(0, 5.9, 1.4),
                           hoodie="black", trouser="black")
        r.rotation_euler = (0, 0, D(180))
        human.pose(j, human.IDLE)
    # the dock, where the defendant stands
    for (px, py, sx, sy) in ((0, -1.4, 3.4, 0.28), (-1.7, -0.3, 0.28, 2.4),
                             (1.7, -0.3, 0.28, 2.4)):
        kit.box((px, py, 0.65), (sx, sy, 1.3), "wood_dark", "dock")
    # gallery benches
    for i in range(3):
        kit.box((0, -4.8 - i * 1.9, 0.6), (12, 0.5, 1.2), "wood", "pew")


def courthouse(seed=0):
    """Neoclassical facade: steps, columns, pediment."""
    kit.ground(120, "ground")
    for i in range(5):
        kit.box((0, 6 + i * 0.9, 0.18 + i * 0.36),
                (16 - i * 0.6, 1.0, 0.36), "stone", "step")
    kit.box((0, 13.5, 4.6), (16, 6, 9.2), "stone", "mass")
    for i in range(6):
        x = -6.5 + i * 2.6
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.46,
                                            depth=7.2, location=(x, 10.2, 3.6))
        paint(bpy.context.object, "stone_light")
        kit.box((x, 10.2, 7.35), (1.25, 1.25, 0.3), "stone_light", "cap")
    kit.box((0, 10.2, 7.8), (15.5, 2.4, 0.6), "stone_light", "arch")
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=8.6, depth=2.6,
                                    location=(0, 10.2, 9.3),
                                    rotation=(D(90), 0, 0))
    p = bpy.context.object
    p.scale = (1, 1, 0.34)
    paint(p, "stone_light")


def briefcase(loc=(0, 0, 0), yaw=0):
    parts = [kit.box((0, 0, 0.22), (0.62, 0.18, 0.44), "wood_dark", "case"),
             kit.box((0, 0, 0.48), (0.2, 0.05, 0.08), "black", "handle")]
    return _group("briefcase", parts, loc, (0, 0, D(yaw)))


def document(loc=(0, 0, 1.0), yaw=0):
    parts = [kit.box((0, 0, 0), (0.5, 0.02, 0.7), "white", "paper")]
    for i in range(4):
        parts.append(kit.box((0, -0.02, 0.2 - i * 0.12),
                             (0.34, 0.01, 0.025), "road", "textline"))
    return _group("doc", parts, loc, (D(-12), 0, D(yaw)))


def wheel(loc=(0, 0, 0), radius=0.9, yaw=0, tread=True):
    """A standalone wheel, for the beat where someone looks at one."""
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=radius,
                                        depth=radius * 0.36,
                                        location=(0, 0, 0),
                                        rotation=(0, D(90), 0))
    parts.append(paint(bpy.context.object, "black"))
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius * 0.46,
                                        depth=radius * 0.40,
                                        location=(0, 0, 0),
                                        rotation=(0, D(90), 0))
    parts.append(paint(bpy.context.object, "stone_light"))
    if tread:
        for i in range(10):
            a = D(i * 36)
            parts.append(kit.box(
                (0, math.sin(a) * radius * 0.78, math.cos(a) * radius * 0.78),
                (radius * 0.40, radius * 0.12, radius * 0.12), "wood_dark"))
    return _group("wheel", parts, (loc[0], loc[1], loc[2] + radius),
                  (0, 0, D(yaw)))


def kerb(loc=(0, 0, 0), length=18.0, height=0.40, yaw=0):
    """Raised pavement edge -- the obstacle the wheels meet."""
    parts = [kit.box((0, 0, height / 2), (3.4, length, height),
                     "stone_light", "pavement"),
             kit.box((-1.72, 0, height / 2 + 0.01), (0.26, length, height + 0.05),
                     "road", "kerbstone")]
    return _group("kerb", parts, loc, (0, 0, D(yaw)))


def crowd(n=5, centre=(0, 0, 0), spread=(5.0, 2.4), yaw=0, seed=0,
          angry=True):
    """A row of onlookers. Varied colour and slight rotation keeps them from
    reading as clones, which is what kills a crowd at this poly level."""
    rnd = random.Random(seed)
    from . import human
    tops = ["hoodie", "wall_c", "wall_d", "roof", "accent", "wall_a"]
    legs = ["trouser", "black", "wood_dark"]
    out = []
    for i in range(n):
        x = centre[0] + (i - (n - 1) / 2) * (spread[0] / max(1, n - 1))
        y = centre[1] + (rnd.random() - 0.5) * spread[1]
        r, j = human.build(f"crowd{i}", loc=(x, y, centre[2]),
                           hoodie=rnd.choice(tops), trouser=rnd.choice(legs))
        r.rotation_euler = (0, 0, D(yaw + (rnd.random() - 0.5) * 26))
        human.pose(j, human.SHRUG if (angry and i % 2 == 0) else human.IDLE)
        out.append(r)
    return out


def luggage_pile(loc=(0, 0, 0), n=4, seed=0):
    """Old-style cases with no wheels, stacked."""
    rnd = random.Random(seed)
    cols = ["wood_dark", "roof", "wall_c", "wood"]
    parts = []
    z = 0.0
    for i in range(n):
        w = 0.95 - i * 0.09
        h = 0.26 + rnd.random() * 0.08
        parts.append(kit.box((rnd.uniform(-.08, .08), rnd.uniform(-.06, .06),
                              z + h / 2), (w, w * 0.62, h),
                             cols[i % len(cols)], "case"))
        parts.append(kit.box((0, 0, z + h), (w * 0.22, 0.05, 0.07),
                             "black", "handle"))
        z += h
    return _group("luggage", parts, loc)


def text3d(body, loc=(0, 0, 0), size=0.3, color="black", yaw=0, rx=0,
           align="CENTER", extrude=0.01, bold=True):
    """Real 3D text. Needed wherever the gag IS the words -- a case number
    read aloud has to be legible on screen or the beat is wasted."""
    bpy.ops.object.text_add(location=(0, 0, 0))
    t = bpy.context.object
    t.data.body = body
    t.data.size = size
    t.data.align_x = align
    t.data.align_y = "CENTER"
    t.data.extrude = extrude
    t.data.space_character = 1.05
    if bold:
        t.data.bevel_depth = size * 0.012
    paint(t, color, shading="flat")
    t.location = loc
    t.rotation_euler = (D(90 + rx), 0, D(yaw))
    return t


def case_file(loc=(0, 0, 1.25), number="704", defendant="CLOUD", yaw=0,
              rx=-10):
    """A stamped case file. The number is the punchline, so it is set large."""
    parts = [kit.box((0, 0, 0), (1.15, 0.03, 1.5), "white", "paper")]
    parts.append(kit.box((0, -0.02, 0.56), (0.95, 0.01, 0.035), "road", "rule"))
    g = _group("case_file", parts, loc, (D(rx), 0, D(yaw)))
    txts = [
        text3d("CASE No.", (0, -0.035, 0.30), 0.105, "road"),
        text3d(number, (0, -0.045, 0.02), 0.38, "accent"),
        text3d("DEFENDANT", (0, -0.035, -0.34), 0.075, "road"),
        text3d(defendant, (0, -0.040, -0.50), 0.155, "black"),
    ]
    for t in txts:
        t.rotation_euler = (D(90), 0, 0)
        t.parent = g
    return g


def sign(body, loc=(0, 0, 0), size=0.45, width=None, color="accent",
         text_color="white", yaw=0, post=True):
    """A standing sign board with real lettering."""
    w = width or (len(body) * size * 0.46 + 0.4)
    parts = [kit.box((0, 0, 0), (w, 0.08, size * 1.9), color, "board")]
    if post:
        parts.append(kit.box((0, 0, -size * 1.9), (0.1, 0.1, size * 1.9),
                             "wood_dark", "post"))
    g = _group("sign", parts, loc, (0, 0, D(yaw)))
    t = text3d(body, (0, -0.06, 0), size, text_color)
    t.rotation_euler = (D(90), 0, 0)
    t.parent = g
    return g


def year_card(year="1970", loc=(0, 0, 1.6), size=0.9, yaw=0):
    """A big date stamp for an era cut."""
    t = text3d(str(year), loc, size, "accent", yaw=yaw)
    return t
