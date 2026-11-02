@echo off
rem 双击启动桌宠（用 pythonw，不弹控制台）
rem 想指定解释器：set PET_PYTHON=C:\path\to\pythonw.exe
cd /d "%~dp0"

if defined PET_PYTHON (
    start "" "%PET_PYTHON%" main.py
    goto :eof
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw main.py
) else (
    echo [错误] 未找到 pythonw，请先安装 Python 并加入 PATH，
    echo        或设置 PET_PYTHON 指向你的 pythonw.exe。
    pause
)
