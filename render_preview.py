"""
预览渲染：不开 GUI，直接用 Behavior 系统渲染若干状态并保存 PNG。
覆盖：眼珠跟鼠标（4 方向）+ 拍球中 + 正常态。

输出到 assets/preview_*.png，方便快速核对效果。
"""
from pathlib import Path
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

from pet import config
from pet.behavior import BehaviorManager
from behaviors.eye_follow import EyeFollow
from behaviors.basketball_bounce import BasketballBounce
from behaviors.static_layer import StaticLayer


def make_stub_ctx():
    class StubRoot:
        def winfo_rootx(self): return 0
        def winfo_rooty(self): return 0
    class StubCtx:
        display_w = config.DISPLAY_W
        display_h = config.DISPLAY_H
        root = StubRoot()
    return StubCtx()


def build_base():
    canvas = Image.new("RGBA", (config.DISPLAY_W, config.DISPLAY_H), (0, 0, 0, 0))
    person = Image.open(config.LAYER_PERSON).convert("RGBA")
    person = person.resize(
        (max(1, int(person.width * config.SCALE)),
         max(1, int(person.height * config.SCALE))), Image.LANCZOS)
    canvas.alpha_composite(person, dest=(int(config.PERSON_POS[0] * config.SCALE),
                                          int(config.PERSON_POS[1] * config.SCALE)))
    return canvas


def render_one(behaviors, mouse_dx, mouse_dy, bouncing_frame):
    canvas = build_base().copy()
    ctx = make_stub_ctx()
    # 设置眼珠的鼠标位置
    eye = next(b for b in behaviors if isinstance(b, EyeFollow))
    eye.mouse_x_root = ctx.display_w / 2 + mouse_dx
    eye.mouse_y_root = ctx.display_h / 2 + mouse_dy
    # 设置拍球状态
    bounce = next(b for b in behaviors if isinstance(b, BasketballBounce))
    if bouncing_frame is not None:
        bounce.bouncing = True
        bounce.bounce_frame = bouncing_frame
    else:
        bounce.bouncing = False
        bounce.bounce_frame = 0

    bm = BehaviorManager()
    for b in behaviors:
        bm.register(b)
    bm.dispatch('on_render', ctx=ctx, canvas=canvas)
    return canvas


def main():
    behaviors = [
        BasketballBounce(),
        StaticLayer("眼白", config.LAYER_WHITE, config.WHITE_POS),
        EyeFollow(),
        StaticLayer("头发", config.LAYER_HAIR, config.HAIR_POS),
    ]
    out_dir = config.ASSETS
    cases = [
        ("preview_normal.png",     0, 0, None),
        ("preview_mouse_left.png", -300, 0, None),
        ("preview_mouse_right.png", 300, 0, None),
        ("preview_mouse_up.png",     0, -300, None),
        ("preview_mouse_down.png",   0,  300, None),
        ("preview_bounce_mid.png",   0, 0, 1),
        ("preview_bounce_high.png",  0, 0, 3),
    ]
    for name, dx, dy, bf in cases:
        canvas = render_one(behaviors, dx, dy, bf)
        canvas.save(out_dir / name)
        print(f"  {name}  → {out_dir / name}")


if __name__ == "__main__":
    main()
