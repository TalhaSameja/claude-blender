"""Low-poly humanoid built from primitives and driven by empty "joints".

Deliberately NOT a rigged armature: joints are plain empties, so a shot can be
posed from a dict of angles and keyframed without touching bone data. That
keeps episodes writable as plain data instead of hand-animated .blend files.

The character is 100% procedural, which is the whole point -- the channel owns
the IP, and nothing in a frame needs a licence.
"""
import bpy, math
from .style import paint

TAU = math.pi * 2
D = math.radians


def _empty(name, loc, parent=None):
    """loc is a LOCAL offset from parent. We never set matrix_parent_inverse:
    reading parent.matrix_world here would be stale (the depsgraph has not run
    yet while the figure is still being assembled)."""
    e = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(e)
    e.location = loc
    e.empty_display_size = 0.12
    if parent:
        e.parent = parent
    return e


def _limb(name, parent, length, radius, color, offset=(0, 0, 0)):
    """A capsule hanging downward from its parent joint's origin."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius,
                                        depth=length, location=(0, 0, 0))
    seg = bpy.context.object
    seg.name = name
    paint(seg, color)
    seg.location = (offset[0], offset[1], offset[2] - length / 2)
    seg.parent = parent
    return seg


def build(name="hero", loc=(0, 0, 0), hoodie="hoodie", trouser="trouser",
          skin="skin", scale=1.0):
    """Returns (root_empty, joints_dict). Height is ~1.8 units at scale=1."""
    root = _empty(f"{name}_root", loc)
    joints = {"root": root}

    hips = _empty(f"{name}_hips", (0, 0, 0.92 * scale), root)
    joints["hips"] = hips

    # torso: slightly tapered box reads as a hoodie at this poly level
    bpy.ops.mesh.primitive_cube_add(size=1)
    torso = bpy.context.object
    torso.name = f"{name}_torso"
    torso.scale = (0.40 * scale, 0.26 * scale, 0.62 * scale)
    torso.location = (0, 0, 0.31 * scale)
    torso.parent = hips
    paint(torso, hoodie)
    bpy.ops.object.shade_smooth()

    neck = _empty(f"{name}_neck", (0, 0, 0.64 * scale), hips)
    joints["neck"] = neck

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10,
                                         radius=0.21 * scale)
    head = bpy.context.object
    head.name = f"{name}_head"
    head.scale = (0.92, 1.0, 1.08)
    head.location = (0, 0, 0.19 * scale)
    head.parent = neck
    paint(head, skin)
    bpy.ops.object.shade_smooth()
    joints["head"] = head

    # hair cap
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8,
                                         radius=0.215 * scale)
    hair = bpy.context.object
    hair.name = f"{name}_hair"
    hair.scale = (0.94, 1.02, 0.78)
    hair.location = (0, 0, 0.26 * scale)
    hair.parent = neck
    paint(hair, "hair")
    bpy.ops.object.shade_smooth()

    # eyes -- two flat dots, the only facial feature. Keeps it readable small.
    for sx in (-0.085, 0.085):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6,
                                             radius=0.030 * scale)
        eye = bpy.context.object
        eye.location = (sx * scale, -0.185 * scale, 0.20 * scale)
        eye.parent = neck
        paint(eye, "black", shading="flat")
        bpy.ops.object.shade_smooth()

    for side, sx in (("l", -1), ("r", 1)):
        sh = _empty(f"{name}_sh_{side}", (sx * 0.23 * scale, 0, 0.54 * scale), hips)
        upper = _limb(f"{name}_uarm_{side}", sh, 0.34 * scale, 0.085 * scale, hoodie)
        el = _empty(f"{name}_el_{side}", (0, 0, -0.34 * scale), sh)
        fore = _limb(f"{name}_farm_{side}", el, 0.32 * scale, 0.075 * scale, hoodie)
        hand = _limb(f"{name}_hand_{side}", el, 0.12 * scale, 0.085 * scale,
                     skin, offset=(0, 0, -0.32 * scale))
        joints[f"sh_{side}"] = sh
        joints[f"el_{side}"] = el

        hp = _empty(f"{name}_hip_{side}", (sx * 0.13 * scale, 0, 0), hips)
        thigh = _limb(f"{name}_thigh_{side}", hp, 0.46 * scale, 0.105 * scale, trouser)
        kn = _empty(f"{name}_kn_{side}", (0, 0, -0.46 * scale), hp)
        shin = _limb(f"{name}_shin_{side}", kn, 0.42 * scale, 0.088 * scale, trouser)
        bpy.ops.mesh.primitive_cube_add(size=1)
        foot = bpy.context.object
        foot.name = f"{name}_foot_{side}"
        foot.scale = (0.11 * scale, 0.22 * scale, 0.07 * scale)
        foot.location = (0, -0.05 * scale, -0.455 * scale)
        foot.parent = kn
        paint(foot, "shoe")
        joints[f"hip_{side}"] = hp
        joints[f"kn_{side}"] = kn

    pose(joints, IDLE)
    return root, joints


# ---- poses: dicts of joint -> (rx, ry, rz) in degrees -------------------

IDLE = {
    "sh_l": (8, 0, -6), "sh_r": (8, 0, 6),
    "el_l": (12, 0, 0), "el_r": (12, 0, 0),
    "hip_l": (0, 0, 0), "hip_r": (0, 0, 0),
    "kn_l": (3, 0, 0), "kn_r": (3, 0, 0),
    "neck": (0, 0, 0),
}

SHRUG = {
    "sh_l": (-70, 0, -40), "sh_r": (-70, 0, 40),
    "el_l": (-55, 0, 0), "el_r": (-55, 0, 0),
    "neck": (6, 0, 0),
}

POINT = {
    "sh_l": (8, 0, -6), "sh_r": (-95, 0, 8),
    "el_l": (12, 0, 0), "el_r": (-6, 0, 0),
    "neck": (0, 0, 10),
}

HOLD = {   # both arms forward, as if gripping a handle
    "sh_l": (-78, 0, -10), "sh_r": (-78, 0, 10),
    "el_l": (-20, 0, 0), "el_r": (-20, 0, 0),
}


def pose(joints, p, frame=None):
    for jname, rot in p.items():
        j = joints.get(jname)
        if not j:
            continue
        j.rotation_euler = tuple(D(a) for a in rot)
        if frame is not None:
            j.keyframe_insert("rotation_euler", frame=frame)


def walk(joints, root, frame_start, frame_end, step_frames=12, stride=28,
         distance=None, direction=(0, 1)):
    """Keyframe a looping walk cycle and optionally translate the root."""
    f = frame_start
    phase = 0
    while f <= frame_end:
        s = stride if phase % 2 == 0 else -stride
        p = {
            "hip_l": (s, 0, 0), "hip_r": (-s, 0, 0),
            "kn_l": (max(0, -s * 0.7) + 4, 0, 0),
            "kn_r": (max(0, s * 0.7) + 4, 0, 0),
            "sh_l": (-s * 0.5 + 8, 0, -6), "sh_r": (s * 0.5 + 8, 0, 6),
            "el_l": (12, 0, 0), "el_r": (12, 0, 0),
        }
        pose(joints, p, frame=f)
        # subtle body bob sells the weight
        root.location.z = 0.0 + (0.035 if phase % 2 else 0.0)
        root.keyframe_insert("location", frame=f)
        f += step_frames
        phase += 1

    if distance:
        x0, y0, z0 = root.location.x, root.location.y, 0.0
        root.location = (x0, y0, z0)
        root.keyframe_insert("location", frame=frame_start)
        root.location = (x0 + direction[0] * distance,
                         y0 + direction[1] * distance, z0)
        root.keyframe_insert("location", frame=frame_end)
