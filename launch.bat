@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3.14 main.py
) else (
  python main.py
)
if errorlevel 1 (
  echo Launch failed. Install Python 3.14 with Tcl/Tk, or run main.py with your Python.
  pause
)
