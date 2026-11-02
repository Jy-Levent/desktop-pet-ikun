"""
资源路径与可调参数（数据全部来自 卡通5.psd，精确）。
集中改这里就行。
"""
import sys
from pathlib import Path


def _base_dir() -> Path:
    """根目录：
    - 开发模式（python main.py）：源码目录 desktop_pet/
    - 打包模式（PyInstaller exe）：exe 所在目录（资源复制在 exe 旁边）
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


# ---------- 路径 ----------
ROOT = _base_dir()
ASSETS = ROOT / "assets"
SOUNDS = ROOT / "sounds"
LAYERS = ASSETS / "layers"          # 从 PSD 导出的图层 PNG

LAYER_PERSON = LAYERS / "人物.png"   # 最底层
LAYER_BALL   = LAYERS / "篮球.png"
LAYER_WHITE  = LAYERS / "眼白.png"
LAYER_PUPIL  = LAYERS / "眼珠.png"
LAYER_HAIR   = LAYERS / "头发.png"   # 最顶层

# ---------- 画布与显示 ----------
CANVAS_W = 507                      # PSD 画布宽
CANVAS_H = 500                      # PSD 画布高
DISPLAY_W = 320
DISPLAY_H = 315                     # 500 * 320/507 ≈ 315，保持原比例
SCALE = DISPLAY_W / CANVAS_W        # 统一缩放因子（≈0.631）

# ---------- 大小档位（大 = 当前尺寸；中/小按同比例缩放） ----------
# 每档存 (宽, 高)，高 = int(宽 * CANVAS_H / CANVAS_W)，保持原比例
SIZES = [
    ("大", (320, 315)),
    ("中", (256, 252)),
    ("小", (200, 197)),
]
SIZE_DEFAULT = SIZES[0][0]          # 启动默认档位 = 大

# ---------- 各图层 paste 位置（PSD 画布坐标，左上角） ----------
PERSON_POS = (117, 92)              # 人物层（改衣服后 bbox 更新为 (117,92,490,500)）
BALL_POS   = (-6, 317)
WHITE_POS  = (244, 206)
PUPIL_POS  = (298, 238)             # PSD 原始位置（眼珠偏右）
HAIR_POS   = (65, 73)

# ---------- 眼珠居中偏移（让眼珠默认回到眼白中心） ----------
# 左眼珠(315.1,254.6)→左眼白(290.6,251.8)：(-24.5,-2.8)
# 右眼珠(415.1,254.6)→右眼白(396,252.5)：(-19.1,-2.1)
# 取折中
PUPIL_CENTER_OFFSET = (-22, -2)

# ---------- 眼珠移动范围（眼白半轴 - 眼珠半径，眼珠不出眼白） ----------
PUPIL_MAX_OFFSET_X = 26             # 右眼白半轴42 - 眼珠半径16
PUPIL_MAX_OFFSET_Y = 26

# ---------- 拍球 ----------
BOUNCE_INTERVAL_MS = 60_000        # 1 分钟
BOUNCE_COUNT = 3                    # 拍 3 下
BOUNCE_STEP_MS = 220                # 每次拍球动作时长
BOUNCE_AMPLITUDE = 28               # 上下幅度（原图坐标，比之前大）

# ---------- 主循环 ----------
FRAME_MS = 16                       # ~60fps

# ---------- 透明色键 ----------
TRANSPARENT_COLOR = "#FF00FF"       # magenta
