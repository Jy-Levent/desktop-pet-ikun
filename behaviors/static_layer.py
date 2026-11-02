"""
通用静态图层：加载一张 PNG，按画布坐标 paste 到指定位置。
用于 眼白层、头发层 等不需要动画的图层。
支持窗口尺寸切换（on_resize 时按新比例重建缩放图层）。
"""
from __future__ import annotations
from PIL import Image
from pet.behavior import Behavior
from pet import config


class StaticLayer(Behavior):
    def __init__(self, name, path, pos):
        super().__init__(name)
        self.path = path
        self._pos = pos                            # 画布坐标（不随尺寸变）
        self._src = Image.open(path).convert("RGBA")  # 原始分辨率，重建缩放用
        self.scale = config.SCALE                  # 初始 = 当前默认尺寸比例
        self.img = None
        self.px = self.py = 0
        self._apply_scale()

    def _apply_scale(self):
        """按 self.scale 重建缩放图层与 paste 位置。"""
        s = self.scale
        self.img = self._src.resize(
            (max(1, int(self._src.width * s)),
             max(1, int(self._src.height * s))),
            Image.LANCZOS,
        )
        self.px = int(self._pos[0] * s)
        self.py = int(self._pos[1] * s)

    def on_resize(self, ctx, scale=None, **kw):
        if scale is not None and abs(scale - self.scale) > 1e-9:
            self.scale = scale
            self._apply_scale()

    def on_render(self, ctx, canvas, **kw):
        canvas.alpha_composite(self.img, dest=(self.px, self.py))
