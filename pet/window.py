"""
透明悬浮窗：无边框、置顶、可拖拽、单击触发。
每帧：基图（角色） + 行为叠加 → 应用透明色键 → 转 ImageTk → 刷新 Label。
支持运行时切换大小档位（大/中/小）：右键菜单触发，保持窗口中心不动。
"""
from __future__ import annotations
from typing import Callable
import tkinter as tk
from PIL import Image, ImageTk

from pet import config


class PetWindow:
    DRAG_THRESHOLD = 4  # 像素，超过则算拖拽

    def __init__(self, root: tk.Tk,
                 base_builder: Callable[[int, int], Image.Image],
                 display_size, behavior_manager):
        self.root = root
        self.display_w, self.display_h = display_size
        self.bm = behavior_manager
        self._base_builder = base_builder          # build_base(w, h) → 人物底图

        # 基图 = 人物层（已缩放到当前显示尺寸，含透明画布）
        self.base_img = self._build_base()

        # 当前帧
        self.current_frame = None
        self.tk_img = None  # 必须保持引用，否则 tkinter 释放

        # 鼠标
        self.mouse_x_root = 0
        self.mouse_y_root = 0

        # 拖拽
        self.dragging = False
        self.drag_off_x = 0
        self.drag_off_y = 0
        self.drag_moved = False
        self.press_x_root = 0
        self.press_y_root = 0

        # Label
        self.label = tk.Label(root, bd=0, highlightthickness=0,
                              bg=config.TRANSPARENT_COLOR)
        self.label.pack()

        # 透明色键（重要：先 apply transparentcolor，再设 topmost/overrideredirect）
        root.wm_attributes('-transparentcolor', config.TRANSPARENT_COLOR)
        root.overrideredirect(True)
        root.wm_attributes('-topmost', True)

        # 初始合成 + 几何
        self._render()
        root.geometry(f'{self.display_w}x{self.display_h}')

        # 事件
        self.label.bind('<Button-1>', self._on_press)
        self.label.bind('<B1-Motion>', self._on_drag)
        self.label.bind('<ButtonRelease-1>', self._on_release)
        # 退出
        root.bind('<Escape>', lambda e: self.root.destroy())
        # 右键 → 大小菜单（含退出）
        self._build_menu()
        root.bind('<Button-3>', self._popup_menu)

    # -------- 大小切换 --------
    def _build_menu(self):
        menu = tk.Menu(self.root, tearoff=0)
        self.size_var = tk.StringVar(value=config.SIZE_DEFAULT)
        for key, _size in config.SIZES:
            menu.add_radiobutton(
                label=f"{key}号", value=key, variable=self.size_var,
                command=lambda k=key: self.set_size(k),
            )
        menu.add_separator()
        menu.add_command(label="退出", command=self.root.destroy)
        self.menu = menu

    def _popup_menu(self, e):
        try:
            self.menu.tk_popup(e.x_root, e.y_root)
        finally:
            self.menu.grab_release()

    def set_size(self, key: str):
        """切换到指定档位（config.SIZES 里的 key），保持窗口中心不动。"""
        for k, (w, h) in config.SIZES:
            if k != key:
                continue
            if (w, h) == (self.display_w, self.display_h):
                return
            cx = self.root.winfo_x() + self.display_w // 2
            cy = self.root.winfo_y() + self.display_h // 2
            self.display_w, self.display_h = w, h
            self.base_img = self._build_base()
            scale = w / config.CANVAS_W
            self.bm.dispatch('on_resize', ctx=self, scale=scale, w=w, h=h)
            self.root.geometry(f'{w}x{h}+{cx - w // 2}+{cy - h // 2}')
            self._render()
            return

    def _build_base(self):
        return self._base_builder(self.display_w, self.display_h)

    # -------- 鼠标 --------
    def _on_press(self, e):
        self.dragging = True
        self.drag_off_x = e.x
        self.drag_off_y = e.y
        self.press_x_root = self.root.winfo_rootx() + e.x
        self.press_y_root = self.root.winfo_rooty() + e.y
        self.drag_moved = False

    def _on_drag(self, e):
        if not self.dragging:
            return
        new_x = self.root.winfo_x() + (e.x - self.drag_off_x)
        new_y = self.root.winfo_y() + (e.y - self.drag_off_y)
        self.root.geometry(f'+{new_x}+{new_y}')
        if (abs(e.x_root - self.press_x_root) > self.DRAG_THRESHOLD or
                abs(e.y_root - self.press_y_root) > self.DRAG_THRESHOLD):
            self.drag_moved = True

    def _on_release(self, e):
        if self.dragging and not self.drag_moved:
            x_root = self.root.winfo_rootx() + e.x
            y_root = self.root.winfo_rooty() + e.y
            self.bm.dispatch('on_click', ctx=self, x_root=x_root, y_root=y_root, button='left')
        self.dragging = False

    def _on_motion(self, e):
        self.mouse_x_root = self.root.winfo_pointerx()
        self.mouse_y_root = self.root.winfo_pointery()
        self.bm.dispatch('on_mouse_move', ctx=self,
                         x_root=self.mouse_x_root, y_root=self.mouse_y_root)

    # -------- 渲染 --------
    def _apply_transparent_key(self, img: Image.Image) -> Image.Image:
        """把 RGBA 透明处替换为 transparentcolor RGB。
        关键：先二值化 alpha，砍掉半透明边缘，避免与色键混色产生紫边。"""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        tc = config.TRANSPARENT_COLOR.lstrip('#')
        r, g, b = int(tc[0:2], 16), int(tc[2:4], 16), int(tc[4:6], 16)
        # 二值化 alpha：>=128 → 不透明，<128 → 全透明（色键色）
        alpha = img.split()[3].point(lambda x: 255 if x >= 128 else 0)
        bg = Image.new('RGB', img.size, (r, g, b))
        bg.paste(img, mask=alpha)
        return bg

    def _render(self):
        canvas = self.base_img.copy()
        self.bm.dispatch('on_render', ctx=self, canvas=canvas)
        rgb = self._apply_transparent_key(canvas)
        self.current_frame = rgb
        self.tk_img = ImageTk.PhotoImage(rgb)
        self.label.config(image=self.tk_img)

    def tick(self, dt_ms: int):
        # 每帧主动轮询全局鼠标位置（屏幕绝对坐标），实现真正的全局跟随，
        # 不依赖 Motion 事件（那只在鼠标悬停在窗口上时触发）
        mx, my = self.root.winfo_pointerxy()
        self.mouse_x_root = mx
        self.mouse_y_root = my
        self.bm.dispatch('on_mouse_move', ctx=self, x_root=mx, y_root=my)
        self.bm.dispatch('on_tick', ctx=self, dt_ms=dt_ms)
        self._render()

    def after(self, ms, fn):
        return self.root.after(ms, fn)
