"""
桌面宠物主程序。

渲染层级（按 PSD 从底到顶）：
  人物 → 篮球 → 眼白 → 眼珠 → 头发

启动：
    python main.py
或双击 run.bat（不弹控制台）。
"""
from __future__ import annotations
import time
import tkinter as tk
from PIL import Image

from pet import config
from pet.window import PetWindow
from pet.behavior import BehaviorManager
from behaviors.eye_follow import EyeFollow
from behaviors.basketball_bounce import BasketballBounce
from behaviors.click_audio import ClickAudio
from behaviors.static_layer import StaticLayer


def build_base(w: int = None, h: int = None) -> Image.Image:
    """构建最底层：透明画布 + 人物层（人物 bbox 超出画布，按坐标 paste 会被裁剪）。
    w/h 省略时用 config 默认档位（大号）。"""
    if w is None:
        w = config.DISPLAY_W
    if h is None:
        h = config.DISPLAY_H
    scale = w / config.CANVAS_W
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    person = Image.open(config.LAYER_PERSON).convert("RGBA")
    person = person.resize(
        (max(1, int(person.width * scale)),
         max(1, int(person.height * scale))),
        Image.LANCZOS,
    )
    canvas.alpha_composite(person, dest=(int(config.PERSON_POS[0] * scale),
                                          int(config.PERSON_POS[1] * scale)))
    return canvas


def main():
    root = tk.Tk()
    root.title("DesktopPet")

    # 行为注册（注册顺序 = 渲染顺序，从底到顶）
    bm = BehaviorManager()
    bounce = BasketballBounce()                       # 篮球（动态振荡）
    white = StaticLayer("眼白", config.LAYER_WHITE, config.WHITE_POS)
    eye = EyeFollow()                                  # 眼珠（跟随鼠标）
    hair = StaticLayer("头发", config.LAYER_HAIR, config.HAIR_POS)
    audio = ClickAudio()
    for b in (bounce, white, eye, hair, audio):
        bm.register(b)

    # 窗口（base_builder = 人物层，切尺寸时按新宽高重建）
    pet = PetWindow(root, build_base,
                    (config.DISPLAY_W, config.DISPLAY_H), bm)

    # attach（让行为拿到 ctx 启动定时器）
    for b in (eye, bounce, audio):
        b.on_attach(pet)

    # 初始位置：屏幕右下角
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f'+{sw - config.DISPLAY_W - 40}+{sh - config.DISPLAY_H - 80}')

    # 主循环
    last = time.monotonic()

    def loop():
        nonlocal last
        now = time.monotonic()
        dt_ms = int((now - last) * 1000)
        last = now
        pet.tick(dt_ms)
        root.after(config.FRAME_MS, loop)

    root.after(config.FRAME_MS, loop)

    print("=" * 60)
    print("桌宠已启动（数据来自 PSD）")
    print(f"  显示尺寸: {config.DISPLAY_W}x{config.DISPLAY_H}（档位: "
          + " / ".join(f"{k} {w}x{h}" for k, (w, h) in config.SIZES) + "）")
    print(f"  渲染层级: 人物 → 篮球 → 眼白 → 眼珠 → 头发")
    print(f"  行为: 眼珠在眼白内跟鼠标 | 每 {config.BOUNCE_INTERVAL_MS//1000}s 拍 3 下球 | "
          f"点击随机音频")
    print(f"  音频文件: {config.SOUNDS}（{len(audio.sounds)} 个）")
    print("  操作: 拖拽移动 | 单击播放音频 | 右键 切换大/中/小号 | Esc / 菜单 退出")
    print("=" * 60)

    root.mainloop()


if __name__ == "__main__":
    main()
