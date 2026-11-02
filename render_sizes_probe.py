"""临时验证：驱动 on_resize 切换 大/中/小，各渲一张正常态，检查对齐。"""
from pathlib import Path
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

from pet import config
from pet.behavior import BehaviorManager
from main import build_base
from behaviors.eye_follow import EyeFollow
from behaviors.basketball_bounce import BasketballBounce
from behaviors.static_layer import StaticLayer


def make_ctx(w, h):
    class StubRoot:
        def winfo_rootx(self): return 0
        def winfo_rooty(self): return 0
    class Ctx:
        display_w = w
        display_h = h
        root = StubRoot()
    return Ctx()


def main():
    for key, (w, h) in config.SIZES:
        # 构造全部渲染行为（初始是大号比例，再 dispatch on_resize 切到本档）
        behaviors = [
            BasketballBounce(),
            StaticLayer("眼白", config.LAYER_WHITE, config.WHITE_POS),
            EyeFollow(),
            StaticLayer("头发", config.LAYER_HAIR, config.HAIR_POS),
        ]
        ctx = make_ctx(w, h)
        scale = w / config.CANVAS_W
        bm = BehaviorManager()
        for b in behaviors:
            bm.register(b)
        bm.dispatch('on_resize', ctx=ctx, scale=scale, w=w, h=h)

        canvas = build_base(w, h)
        eye = next(b for b in behaviors if isinstance(b, EyeFollow))
        eye.mouse_x_root = w / 2
        eye.mouse_y_root = h / 2
        bm.dispatch('on_render', ctx=ctx, canvas=canvas)
        out = config.ASSETS / f"preview_size_{key}.png"
        canvas.save(out)
        print(f"  {key}号 {w}x{h}  scale={scale:.4f}  → {out}")


if __name__ == "__main__":
    main()
