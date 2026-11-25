@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo This builds the GUI EXE. Phone operations still use an external Python runtime.
echo It will create .build-venv and download PyInstaller from PyPI.
set /p "GEOSHIFT_BUILD_OK=Type YES to continue: "
if /i not "%GEOSHIFT_BUILD_OK%"=="YES" exit /b 1
py -3.14 -m venv .build-venv
if errorlevel 1 exit /b 1
.build-venv\Scripts\python.exe -m pip install pyinstaller==6.22.3
if errorlevel 1 exit /b 1
.build-venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --manifest windows.manifest --onefile --windowed --name "虚拟定位助手" --distpath dist --workpath .build --specpath . main.py
if errorlevel 1 exit /b 1
start "" /wait "dist\虚拟定位助手.exe" --smoke-test build-smoke.json
if not exist build-smoke.json exit /b 1
echo Inspect build-smoke.json and launch "dist\虚拟定位助手.exe" for manual verification.
