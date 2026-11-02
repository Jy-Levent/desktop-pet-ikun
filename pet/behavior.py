"""
Behavior 框架：所有交互模块（眼随鼠标、拍球、点击音频…）继承 Behavior。
BehaviorManager 统一派发事件，主循环每帧调用 on_tick + on_render。
新增行为：写一个继承 Behavior 的类，on_attach / on_render 即可。
"""
from __future__ import annotations
from typing import Any, Callable, List


class Behavior:
    """所有行为的基类。子类可重写下面的钩子，无需全部实现。"""
    def __init__(self, name: str = "behavior"):
        self.name = name
        self.enabled = True

    def on_attach(self, ctx) -> None:
        """被注册到窗口时调用。可启动定时器等。"""

    def on_detach(self) -> None:
        """被注销时调用。"""

    def on_tick(self, ctx, dt_ms: int) -> None:
        """每帧调用（主循环 FRAME_MS 一次）。"""

    def on_mouse_move(self, ctx, x_root: int, y_root: int) -> None:
        """全局鼠标移动。"""

    def on_click(self, ctx, x_root: int, y_root: int, button: str) -> None:
        """鼠标点击（区分过拖拽阈值后算点击）。"""

    def on_render(self, ctx, canvas) -> None:
        """在每帧 canvas（PIL Image）上绘制自己的图层。先于基图合成调用，
        通过 alpha_composite 把内容叠到 canvas 上即可。"""

    def on_resize(self, ctx, scale: float, **kw) -> None:
        """窗口尺寸变化（切换大小档位）时调用，scale = 新宽 / 画布宽。
        需要按新比例重建内部缩放图层/位置的行为重写此方法。"""


class BehaviorManager:
    def __init__(self):
        self.behaviors: List[Behavior] = []

    def register(self, b: Behavior):
        self.behaviors.append(b)

    def unregister(self, b: Behavior):
        if b in self.behaviors:
            self.behaviors.remove(b)

    def dispatch(self, event: str, **kw):
        for b in list(self.behaviors):
            if not b.enabled:
                continue
            fn = getattr(b, event, None)
            if fn is None:
                continue
            # fn 是 bound method，self 已绑；不要再传 b
            try:
                fn(**kw)
            except TypeError as e:
                print(f"[Behavior:{b.name}] {event} signature mismatch: {e}")
            except Exception as e:
                print(f"[Behavior:{b.name}] {event} error: {e}")
