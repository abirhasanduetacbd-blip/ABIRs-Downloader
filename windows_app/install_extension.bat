@echo off
title ABIRs Downloader - Chrome/Edge Extension Setup
echo ============================================================
echo ABIRs Downloader - Browser Extension Setup
echo ============================================================
echo.
echo 1. Opening Chrome Extensions page...
start chrome chrome://extensions
echo 2. Enable "Developer mode" in the top-right corner.
echo 3. Click "Load unpacked".
echo 4. Select the following folder:
echo    %~dp0..\extension
echo.
echo Press any key to exit setup...
pause > nul
