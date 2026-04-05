@echo off
title WOFF2-to-TTF Builder
echo.
echo  ============================================
echo   Font Converter — Build Script
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo  [1/3] Installing dependencies...
pip install fonttools brotli tkinterdnd2 pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo  [ERROR] pip install failed.
    pause
    exit /b 1
)

echo  [2/3] Building executable...

:: Find tkinterdnd2 install location so PyInstaller can bundle it
for /f "delims=" %%i in ('python -c "import tkinterdnd2, os; print(os.path.dirname(tkinterdnd2.__file__))"') do set DND_PATH=%%i

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "FontConverter" ^
    --icon "icon.ico" ^
    --add-data "%DND_PATH%;tkinterdnd2" ^
    --add-data "icon.ico;." ^
    --hidden-import tkinterdnd2 ^
    --hidden-import fontTools ^
    --hidden-import fontTools.ttLib ^
    --hidden-import brotli ^
    converter.py

if errorlevel 1 (
    echo  [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo  [3/3] Done!
echo.
echo  Your EXE is at:  dist\FontConverter.exe
echo  Share that single file — no install needed on the other machine.
echo.
pause
