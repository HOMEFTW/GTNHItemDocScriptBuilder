@echo off
setlocal
cd /d "%~dp0"
python -m PyInstaller build.spec
endlocal
