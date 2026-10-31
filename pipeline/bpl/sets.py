"""Reusable sets + camera rigs. An episode picks a set by name and never
touches Blender directly -- that is what makes 2 videos/day survivable."""
import bpy, math, random
from . import kit, world, subjects
from .style import paint, PALETTE
from . import human

D = math.radians


def _car_interior(seed=0):
    """Dashboard + wheel + door frame, shot from the passenger side."""
    kit.box((0, 1.15, 0.55), (2.4, 0.55, 0.45), "wall_d", "dash")
    kit.box((0, 1.5, 1.35), (2.4, 0.06, 1.0), "window", "windscreen")
    bpy.ops.mesh.primitive_torus_add(major_radius=0.30, minor_radius=0.045,
                                     location=(-0.55, 0.88, 0.95),
                                     rotation=(D(72), 0, 0))
    paint(bpy.context.object, "black")
    kit.box((-1.45, 0.2, 0.75), (0.12, 2.2, 1.6), "hoodie", "door")
    kit.box((0, -1.4, 0.4), (2.4, 0.3, 0.9), "wall_b", "seatback")


def _suburb(seed=1):
    kit.ground(140, "grass")
    kit.road(140, 8)
    rnd = random.Random(seed)
    for i in range(5):
        y = -18 + i * 11
        kit.building((9.5, y, 0), w=6, d=7, floors=rnd.randint(1, 2), seed=i)
        kit.tree((6.2, y - 4, 0), h=3.0, seed=i)
        kit.tree((-6.2, y + 3, 0), h=2.6, seed=i + 9)


def _void(seed=0):
    """Empty studio backdrop -- for a prop held up against nothing."""
    kit.ground(60, "wall_b")


def _carpark(seed=3):
    kit.ground(140, "grass")
    subjects.car_park(seed=seed)


def _courtroom(seed=0):
    subjects.courtroom(seed=seed)


def _courthouse(seed=0):
    subjects.courthouse(seed=seed)


def _pavement(seed=0):
    kit.ground(140, "ground")
    kit.road(140, 8)
    subjects.kerb(loc=(4.6, 0, 0), length=40)


def _sky(seed=0):
    """Nothing but sky -- for a shot where the cloud IS the subject."""
    pass


SETS = {"street": kit.street, "suburb": _suburb,
        "car": _car_interior, "void": _void,
        "carpark": _carpark, "courtroom": _courtroom,
        "courthouse": _courthouse, "sky": _sky,
        "pavement": _pavement}


def build_set(name, seed=0):
    fn = SETS.get(name)
    if fn is None:
        raise KeyError(f"unknown set {name!r}; have {sorted(SETS)}")
    try:
        fn(seed=seed)
    except TypeError:
        fn()


# ---- camera rigs -------------------------------------------------------

def rig(kind, subject=(0, 0, 1.0), frame_start=1, frame_end=48, seed=0):
    """Place the camera and keyframe a slow move. Static-ish moves read as
    'deliberate' at this art style and cost nothing extra to render."""
    sx, sy, sz = subject
    presets = {
        # (start_loc, end_loc, look_at, lens)
        "closeup":  ((sx + 0.75, sy - 2.9, sz + 0.70),
                     (sx + 0.60, sy - 2.7, sz + 0.66), (sx, sy, sz + 0.60), 46),
        "medium":   ((sx + 1.9, sy - 4.0, sz + 0.55),
                     (sx + 1.5, sy - 3.7, sz + 0.50), (sx, sy, sz + 0.15), 40),
        "wide":     ((sx + 4.2, sy - 6.4, sz + 1.8),
                     (sx + 3.4, sy - 5.9, sz + 1.6), (sx, sy, sz - 0.1), 35),
        "low":      ((sx + 1.5, sy - 3.0, 0.40),
                     (sx + 1.2, sy - 2.8, 0.55), (sx, sy, sz + 0.45), 36),
        "topdown":  ((sx + 0.5, sy - 2.0, 9.0),
                     (sx + 0.2, sy - 1.4, 8.2), (sx, sy, 0.4), 40),
        "orbit":    ((sx + 4.0, sy - 4.0, sz + 1.6),
                     (sx - 3.0, sy - 5.0, sz + 1.6), (sx, sy, sz), 40),
    }
    a, b, look, lens = presets.get(kind, presets["medium"])
    cam, tgt = world.camera(a, look, lens)
    cam.location = a
    cam.keyframe_insert("location", frame=frame_start)
    cam.location = b
    cam.keyframe_insert("location", frame=frame_end)
    return cam   # interpolation default is set to LINEAR in world.new_scene
