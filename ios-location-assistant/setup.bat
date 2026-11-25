@echo off
setlocal
cd /d "%~dp0"
echo The GUI will ask before creating an isolated environment or downloading dependencies.
call launch.bat
