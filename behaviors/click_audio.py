"""
行为3：点击随机播放音频。
首次启动时扫描 sounds/ 目录，支持 mp3/wav/ogg/m4a。
用 pygame.mixer，无音频时静默。
"""
from __future__ import annotations
import random

from pet.behavior import Behavior
from pet import config


class ClickAudio(Behavior):
    EXTS = ('.mp3', '.wav', '.ogg', '.m4a')

    def __init__(self):
        super().__init__("click_audio")
        self.sounds = []
        self.mixer_inited = False
        self._pygame = None

    def on_attach(self, ctx):
        self._scan_sounds()
        self._init_mixer()

    def _scan_sounds(self):
        if not config.SOUNDS.exists():
            return
        self.sounds = [p for p in config.SOUNDS.iterdir()
                       if p.suffix.lower() in self.EXTS and p.is_file()]

    def _init_mixer(self):
        if self.mixer_inited:
            return
        try:
            import pygame
            self._pygame = pygame
            pygame.mixer.init()
            self.mixer_inited = True
        except Exception as e:
            print(f"[ClickAudio] mixer init failed: {e}")

    def on_click(self, ctx, x_root, y_root, button, **kw):
        if button != 'left':
            return
        if not self.sounds:
            return  # 没音频，静默
        if not self.mixer_inited:
            self._init_mixer()
        if not self.mixer_inited:
            return
        try:
            sp = str(random.choice(self.sounds))
            self._pygame.mixer.music.load(sp)
            self._pygame.mixer.music.play()
        except Exception as e:
            print(f"[ClickAudio] play failed: {e}")
