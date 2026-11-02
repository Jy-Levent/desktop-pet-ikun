"""解析 PSD 的图层树：图层名、类型、可见性、bbox（画布坐标）、尺寸。

用法：
    python parse_psd.py [psd路径]     # 省略则用项目根目录的 卡通5.psd
"""
import sys
from pathlib import Path
from psd_tools import PSDImage

ROOT = Path(__file__).parent
PSD_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "卡通5.psd"
if not PSD_PATH.exists():
    sys.exit(f"找不到 PSD 文件：{PSD_PATH}\n用法：python parse_psd.py [psd路径]")

psd = PSDImage.open(PSD_PATH)
print(f"画布尺寸: {psd.width} x {psd.height}")
print(f"顶层图层数: {len(psd)}")
print()

def walk(layers, indent=0):
    for layer in layers:
        prefix = "  " * indent
        kind = layer.kind
        vis = "可见" if layer.visible else "隐藏"
        # bbox 是全局画布坐标
        bbox = (layer.left, layer.top, layer.right, layer.bottom)
        print(f"{prefix}[{kind}] '{layer.name}'  {vis}")
        print(f"{prefix}    bbox=({layer.left},{layer.top},{layer.right},{layer.bottom}) "
              f"size={layer.width}x{layer.height}")
        if layer.is_group():
            walk(layer, indent + 1)

walk(psd)
