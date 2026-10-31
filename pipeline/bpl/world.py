"""Scene bootstrap + render configuration.

The render settings here are the result of benchmarking on a 4-core CPU box
with no GPU. The headline finding: for flat/toon shading the OpenImageDenoise
pass costs ~10x more than the sampling it is cleaning up, and there is almost
no noise to clean. Turning the denoiser OFF and dropping to 4 samples took
1080x1920 from 12.2s/frame to 1.14s/frame with no visible quality loss.
"""
import bpy
from . import style

RES = {"1080": (1080, 1920), "720": (720, 1280), "540": (540, 960)}


def new_scene(res="1080", fps=24, samples=4, shading="soft", sky=None,
              theme="pastel", fill=False):
    bpy.ops.preferences.addon_enable(module="cycles")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Blender 5.x uses slotted actions, so walking action.fcurves to fix
    # interpolation no longer works. Setting the default up front is both
    # version-proof and cheaper.
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    style.use_theme(theme)

    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = RES[res]
    sc.render.resolution_percentage = 100
    sc.render.fps = fps
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False          # the big win -- see docstring
    sc.cycles.max_bounces = 0                # direct light only
    sc.cycles.use_adaptive_sampling = False
    sc.cycles.blur_glossy = 0
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.compression = 15
    sc.view_settings.view_transform = "Standard"   # keep pastels punchy

    w = bpy.data.worlds.new("world")
    sc.world = w
    w.use_nodes = True
    col = style._srgb_to_linear(sky or style.PALETTE["sky"])
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*col, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

    if shading == "soft":
        key_light()
        if fill:
            # Interiors get no ambient: with max_bounces=0 the world sky is
            # not a light source, so surfaces facing away from the key go
            # black. A soft opposing fill costs one extra shadow ray.
            key_light(angle=(1.25, 0.0, -2.3), energy=1.15)
    return sc


def key_light(angle=(0.95, 0.0, 0.6), energy=3.2):
    bpy.ops.object.light_add(type="SUN", rotation=angle)
    sun = bpy.context.object
    sun.data.energy = energy
    sun.data.angle = 0.0         # hard sun: soft shadows are the ONLY noise
                                 # source at this shading level, and killing
                                 # them lets 4 samples render clean.
    return sun


def camera(loc, look_at=(0, 0, 1), lens=40):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.data.lens = lens
    tgt = bpy.data.objects.new("cam_target", None)
    bpy.context.collection.objects.link(tgt)
    tgt.location = look_at
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    cam["target"] = tgt.name
    return cam, tgt
