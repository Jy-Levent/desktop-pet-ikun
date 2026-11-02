"""
行为2：每 60 秒拍三下篮球（幅度较大）。
- 加载篮球.png（从 PSD 导出）
- 基准位置 = BALL_POS；拍球时 y 方向 sin 振荡
- 支持窗口尺寸切换：on_resize 时按新比例重建
"""
from __future__ import annotations
import math

from PIL import Image
from pet.behavior import Behavior
from pet import config


class BasketballBounce(Behavior):
    def __init__(self):
        super().__init__("basketball_bounce")
        self._src = Image.open(config.LAYER_BALL).convert("RGBA")
        self.scale = config.SCALE
        self.img = None
        self.px = self.base_py = 0
        self.amp = 0
        self.ctx = None
        self.bouncing = False
        self.bounce_frame = 0
        self.bounce_total = config.BOUNCE_COUNT * 3  # 3 下 = 6 帧
        self._apply_scale()

    def _apply_scale(self):
        s = self.scale
        self.img = self._src.resize(
            (max(1, int(self._src.width * s)),
             max(1, int(self._src.height * s))),
            Image.LANCZOS,
        )
        self.px = int(config.BALL_POS[0] * s)
        self.base_py = int(config.BALL_POS[1] * s)
        self.amp = config.BOUNCE_AMPLITUDE * s

    def on_resize(self, ctx, scale=None, **kw):
        if scale is not None and abs(scale - self.scale) > 1e-9:
            self.scale = scale
            self._apply_scale()

    def on_attach(self, ctx):
        self.ctx = ctx
        self._schedule()

    def _schedule(self):
        if self.ctx is None:
            return
        self.ctx.after(config.BOUNCE_INTERVAL_MS, self._start)

    def _start(self):
        if not self.enabled:
            self._schedule()
            return
        self.bouncing = True
        self.bounce_frame = 0
        self._step()

    def _step(self):
        if not self.bouncing:
            return
        self.bounce_frame += 1
        if self.bounce_frame >= self.bounce_total:
            self.bouncing = False
            self._schedule()
            return
        self.ctx.after(config.BOUNCE_STEP_MS, self._step)

    def on_render(self, ctx, canvas, **kw):
        offset_y = 0
        if self.bouncing:
            t = (self.bounce_frame + 1) / self.bounce_total
            offset_y = -self.amp * abs(math.sin(t * math.pi * config.BOUNCE_COUNT))
        py = self.base_py + int(round(offset_y))
        canvas.alpha_composite(self.img, dest=(self.px, py))
