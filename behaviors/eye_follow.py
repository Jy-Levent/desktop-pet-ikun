"""
行为1：眼睛跟随鼠标（眼珠只在眼白范围内移动）。
- 加载眼珠.png（从 PSD 导出）
- 基准位置 = PUPIL_POS + PUPIL_CENTER_OFFSET（眼珠居中）
- 鼠标方向 → 眼珠朝该方向偏移，范围限制在眼白内（±PUPIL_MAX_OFFSET）
- 支持窗口尺寸切换：on_resize 时按新比例重建缩放眼珠图
"""
from __future__ import annotations
import math

from PIL import Image
from pet.behavior import Behavior
from pet import config


class EyeFollow(Behavior):
    def __init__(self):
        super().__init__("eye_follow")
        self._src = Image.open(config.LAYER_PUPIL).convert("RGBA")
        self.scale = config.SCALE
        self.img = None
        # 眼珠层居中后的基准位置（画布坐标，渲染时再乘 scale）
        self.base_px = config.PUPIL_POS[0] + config.PUPIL_CENTER_OFFSET[0]
        self.base_py = config.PUPIL_POS[1] + config.PUPIL_CENTER_OFFSET[1]
        self.max_ox = config.PUPIL_MAX_OFFSET_X
        self.max_oy = config.PUPIL_MAX_OFFSET_Y
        self.mouse_x_root = 0
        self.mouse_y_root = 0
        self._apply_scale()

    def _apply_scale(self):
        s = self.scale
        self.img = self._src.resize(
            (max(1, int(self._src.width * s)),
             max(1, int(self._src.height * s))),
            Image.LANCZOS,
        )

    def on_resize(self, ctx, scale=None, **kw):
        if scale is not None and abs(scale - self.scale) > 1e-9:
            self.scale = scale
            self._apply_scale()

    def on_mouse_move(self, ctx, x_root, y_root, **kw):
        self.mouse_x_root = x_root
        self.mouse_y_root = y_root

    def on_render(self, ctx, canvas, **kw):
        # 桌宠屏幕中心
        cx = ctx.root.winfo_rootx() + ctx.display_w / 2
        cy = ctx.root.winfo_rooty() + ctx.display_h / 2
        dx = self.mouse_x_root - cx
        dy = self.mouse_y_root - cy
        dist = math.hypot(dx, dy)
        # 全局跟随：鼠标在屏幕任何位置，眼珠都朝该方向满偏移；
        # 只在鼠标贴近桌宠中心时设死区，让眼珠居中（避免方向抖动）
        if dist < 8.0:
            off_x = off_y = 0.0
        else:
            off_x = (dx / dist) * self.max_ox
            off_y = (dy / dist) * self.max_oy
        px = int(round((self.base_px + off_x) * self.scale))
        py = int(round((self.base_py + off_y) * self.scale))
        canvas.alpha_composite(self.img, dest=(px, py))
