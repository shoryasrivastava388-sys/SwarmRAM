@echo off
title SwarmRAM - Worker Node (Share Your RAM)
echo ========================================================
echo        Starting SwarmRAM Worker Node                   
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
