# 桌面宠物 Desktop Pet 🏀

一只悬浮在 Windows 桌面上的透明 2D 小宠物：**眼睛跟着鼠标转、每 60 秒拍三下篮球、点一下随机发声、右键还能切换大小**。

![Windows](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)

## 功能

- **透明悬浮窗**：无边框、始终置顶、可自由拖拽
- **眼睛全局跟随**：鼠标在屏幕任意位置，眼珠都会朝那个方向看，且限制在眼白范围内不会穿模
- **拍篮球**：每 60 秒拍三下，带 sin 振荡动画
- **点击发声**：单击随机播放 `sounds/` 里的音频
- **大小三档**：右键菜单切换 大 / 中 / 小（宽 320 / 256 / 200 像素）
- **可扩展**：Behavior 注册式框架，加新互动只需写一个类再注册一行

## 下载与安装

### 方式一：下载 ZIP（不用装 Git，最简单）

1. 在本页面点右上角绿色 **`Code`** 按钮 → **`Download ZIP`**
2. 解压到任意目录（例如 `D:\DesktopPet`）
3. 按下面「安装依赖」操作

### 方式二：git clone

```bash
git clone https://github.com/Jy-Levent/desktop-pet-ikun.git
cd desktop-pet-ikun
```

### 方式三：直接下载 exe（如果作者发布了 Release）

到仓库右侧 **`Releases`** 页面下载 `DesktopPet.zip`，解压后双击 `DesktopPet.exe` 即可，**不需要安装 Python**。

> 首次运行若弹出 Windows SmartScreen 的「已保护你的电脑」，点 **更多信息 → 仍要运行** 即可（未签名程序的正常提示）。

## 安装依赖

需要 **Python 3.10+**，仅支持 **Windows**（透明悬浮窗依赖 Windows 特性）。

1. 安装 Python：<https://www.python.org/downloads/>
   安装时**务必勾选** `Add Python to PATH`
2. 进入项目目录，打开 PowerShell 或 CMD，执行：

```bash
pip install -r requirements.txt
```

依赖只有两个：`pillow`（图像处理）、`pygame`（音频播放）。

## 启动

```bash
python main.py
```

或者直接双击项目里的 **`run.bat`**（用 `pythonw` 启动，不会弹出黑色控制台窗口）。

如果 Python 没加进 PATH，可以显式指定解释器：

```bat
set PET_PYTHON=C:\path\to\pythonw.exe
run.bat
```

## 操作说明

| 操作 | 效果 |
|---|---|
| 左键拖拽 | 移动桌宠位置 |
| 单击 | 随机播放一个音频 |
| 右键 | 弹出菜单：切换 大 / 中 / 小号、退出 |
| Esc | 退出程序 |

## 音频

`sounds/` 目录里已附几段示例音效，点击桌宠时会随机播放其中一个。

想换成自己的：把 `.mp3` / `.wav` / `.ogg` / `.m4a` 丢进 `sounds/` 目录即可，**不需要改代码**。没有音频文件时点击不会有声音，其他功能不受影响。

> 仓库内示例音效仅用于演示，版权归原作者，请勿商用。

## 目录结构

```
desktop_pet/
├── main.py                入口（注册渲染顺序 + 创建窗口）
├── run.bat                Windows 双击启动
├── requirements.txt       依赖清单
├── pet/
│   ├── config.py          全部可调参数（图层位置 / 尺寸档位 / 拍球 / 色键）
│   ├── behavior.py        Behavior 基类 + BehaviorManager（事件派发）
│   └── window.py          透明悬浮窗（拖拽 / 全局鼠标轮询 / 尺寸切换）
├── behaviors/
│   ├── eye_follow.py          眼珠跟随鼠标（限制在眼白内）
│   ├── basketball_bounce.py   定时拍球
│   ├── click_audio.py         点击随机音频
│   └── static_layer.py        通用静态层（眼白 / 头发）
├── assets/
│   └── layers/            从 PSD 导出的图层：人物 / 篮球 / 眼白 / 眼珠 / 头发
├── sounds/                点击音效
├── export_psd.py          从 PSD 导出图层（需 psd-tools）
├── parse_psd.py           查看 PSD 图层树与 bbox
└── render_preview.py      不开 GUI，直接渲染各状态预览 PNG
```

## 调参

所有位置和尺寸集中在 `pet/config.py`：

| 参数 | 说明 |
|---|---|
| `SIZES` | 大小档位 `[("大",(320,315)), ("中",(256,252)), ("小",(200,197))]` |
| `PUPIL_POS` / `PUPIL_CENTER_OFFSET` | 眼珠基准位置 |
| `PUPIL_MAX_OFFSET_X/Y` | 眼珠相对眼白中心的最大位移 |
| `BOUNCE_INTERVAL_MS` / `BOUNCE_COUNT` / `BOUNCE_AMPLITUDE` | 拍球间隔 / 次数 / 幅度 |
| `TRANSPARENT_COLOR` | 透明色键（同时在 `window.py` 里做 alpha 二值化去紫边） |

改完不用启动桌宠，直接渲染预览图看效果：

```bash
python render_preview.py
```

## 换成自己的角色

1. 准备一份 PSD，图层命名参照：`人物` / `篮球` / `眼白` / `眼珠` / `头发`（从下到上）
2. 安装 PSD 解析库：`pip install psd-tools`
3. 导出图层：`python export_psd.py 你的文件.psd`（默认读取项目根目录的 `卡通5.psd`）
4. 按输出的 bbox 更新 `pet/config.py` 里的图层位置

> 仓库内**不包含** PSD 源文件，只包含导出好的图层 PNG。

## 打包成 exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name DesktopPet main.py
```

打包完成后，把 `assets/` 和 `sounds/` 复制到 `dist/DesktopPet/` 下，双击 `DesktopPet.exe` 即可运行。

> 如果打包后启动报 `Tcl version conflict`，说明 PyInstaller 从 conda 环境收错了 tcl/tk DLL：把 `dist/DesktopPet/_internal/` 下的 `tcl86t.dll`、`tk86t.dll` 换成当前 Python 环境 `Library/bin/` 里的同名文件即可。

## 常见问题

**启动报 `ModuleNotFoundError: No module named 'PIL'` 或 `pygame`**
依赖没装好，在项目目录重新执行 `pip install -r requirements.txt`。

**双击 `run.bat` 闪一下就没了**
多半是 `pythonw` 不在 PATH。先用命令行 `python main.py` 跑，能看到具体报错。

**点击没有声音**
检查 `sounds/` 目录里是否有音频文件；音频格式建议用 `.mp3` 或 `.wav`。

**桌宠找不到了**
它可能被拖到了屏幕边缘外。关掉程序重新启动，会回到屏幕右下角。
