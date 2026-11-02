"""从 PSD 导出所有可见图层为独立 PNG，并输出 bbox 供精确定位。
同时测量眼白层两个椭圆 + 眼珠层两个黑珠的中心/半径。

用法：
    python export_psd.py [psd路径]     # 省略则用项目根目录的 卡通5.psd
"""
import sys
from pathlib import Path
from psd_tools import PSDImage
from PIL import Image

ROOT = Path(__file__).parent
PSD_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "卡通5.psd"
OUT_DIR = ROOT / "assets" / "layers"
if not PSD_PATH.exists():
    sys.exit(f"找不到 PSD 文件：{PSD_PATH}\n用法：python export_psd.py [psd路径]")
OUT_DIR.mkdir(parents=True, exist_ok=True)

psd = PSDImage.open(PSD_PATH)
print("画布:", psd.width, "x", psd.height)
print()

# 1. 导出所有可见图层
meta = {}
for layer in psd:
    if not layer.visible:
        continue
    img = layer.composite()
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    fname = f"{layer.name}.png"
    img.save(OUT_DIR / fname)
    meta[layer.name] = {
        'bbox': (layer.left, layer.top, layer.right, layer.bottom),
        'size': (layer.width, layer.height),
    }
    print(f"导出 {fname:20s} bbox=({layer.left},{layer.top},{layer.right},{layer.bottom}) "
          f"size={layer.width}x{layer.height}")


def find_blobs(img, color_fn, label):
    """找符合 color_fn 的像素聚类，返回中心列表。"""
    W, H = img.size
    px = img.load()
    pts = []
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if color_fn(r, g, b, a):
                pts.append((x, y))
    return pts


def cluster_2_groups(pts):
    """按 x 中线分成左右两组，返回两组中心+半径。"""
    if not pts:
        return []
    xs = sorted(p[0] for p in pts)
    mid = (min(xs) + max(xs)) / 2
    groups = [[], []]
    for p in pts:
        groups[0 if p[0] < mid else 1].append(p)
    out = []
    for g in groups:
        if not g:
            continue
        cx = sum(p[0] for p in g) / len(g)
        cy = sum(p[1] for p in g) / len(g)
        rx = (max(p[0] for p in g) - min(p[0] for p in g)) / 2
        ry = (max(p[1] for p in g) - min(p[1] for p in g)) / 2
        out.append((cx, cy, rx, ry, len(g)))
    return out


# 2. 测量眼白层
print()
print("=== 眼白层（白色椭圆）===")
white_pts = find_blobs(
    Image.open(OUT_DIR / "眼白.png"),
    lambda r, g, b, a: a > 200 and r > 200 and g > 200 and b > 200,
    "white",
)
print(f"白色像素: {len(white_pts)}")
for blob in cluster_2_groups(white_pts):
    print(f"  椭圆: 中心=({blob[0]:.1f},{blob[1]:.1f}) 半轴=({blob[2]:.1f},{blob[3]:.1f}) 像素={blob[4]}")

# 3. 测量眼珠层
print()
print("=== 眼珠层（黑珠）===")
black_pts = find_blobs(
    Image.open(OUT_DIR / "眼珠.png"),
    lambda r, g, b, a: a > 200 and r < 60 and g < 60 and b < 60,
    "black",
)
print(f"黑色像素: {len(black_pts)}")
for blob in cluster_2_groups(black_pts):
    print(f"  眼珠: 中心=({blob[0]:.1f},{blob[1]:.1f}) 半径=({blob[2]:.1f},{blob[3]:.1f}) 像素={blob[4]}")

# 4. 篮球层（smart object，测量圆形范围）
print()
print("=== 篮球层 ===")
ball = Image.open(OUT_DIR / "篮球.png")
bW, bH = ball.size
bpx = ball.load()
ball_pts = []
for y in range(bH):
    for x in range(bW):
        r, g, b, a = bpx[x, y]
        if a > 200:
            ball_pts.append((x, y))
if ball_pts:
    cx = sum(p[0] for p in ball_pts) / len(ball_pts)
    cy = sum(p[1] for p in ball_pts) / len(ball_pts)
    rx = (max(p[0] for p in ball_pts) - min(p[0] for p in ball_pts)) / 2
    ry = (max(p[1] for p in ball_pts) - min(p[1] for p in ball_pts)) / 2
    print(f"  篮球本体: 局部中心=({cx:.1f},{cy:.1f}) 半径=({rx:.1f},{ry:.1f}) 像素={len(ball_pts)}")
