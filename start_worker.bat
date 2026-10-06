@echo off
title SwarmRAM - Worker Node (Share Your RAM)
echo ========================================================
echo        ⚡ SwarmRAM — Sharing RAM With Your Friends ⚡    
echo ========================================================
echo  This lets your computer donate a slice of free RAM to 
echo  your friend's cluster so you can run AI models together.
echo.
echo  * You choose exactly how much RAM to share.
echo  * It leaves 1.2 GB+ free so your PC stays completely smooth.
echo  * Press Ctrl+C at any time to instantly reclaim your RAM.
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Python not found on standard PATH. Attempting local AppData Python...
    if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
        "%LOCALAPPDATA%\Python\bin\python.exe" run_worker.py
        goto end
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" run_worker.py
        goto end
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" run_worker.py
        goto end
    )
    echo [-] Python is not installed. Please install Python from https://www.python.org/
    pause
    exit /b 1
)

python run_worker.py

:end
pause
