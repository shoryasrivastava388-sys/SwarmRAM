@echo off
title SwarmRAM - Cluster Coordinator (Master)
echo ========================================================
echo        ⚡ SwarmRAM Coordinator (Master Node) ⚡          
echo ========================================================
echo.
echo  Cluster Modes:
echo    [1] Focused Mode (Recommended - all RAM used for your output)
echo    [2] Mesh Mode    (Shared - anyone on the Wi-Fi can run prompts)
echo.
set /p MODE_CHOICE="Choose mode [1 or 2, default 1]: "

set MODE_FLAG=focused
if "%MODE_CHOICE%"=="2" set MODE_FLAG=mesh

echo.
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Python not found on standard PATH. Attempting local AppData Python...
    if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
        "%LOCALAPPDATA%\Python\bin\python.exe" run_coordinator.py --mode %MODE_FLAG%
        goto end
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" run_coordinator.py --mode %MODE_FLAG%
        goto end
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" run_coordinator.py --mode %MODE_FLAG%
        goto end
    )
    echo [-] Python is not installed. Please install Python from https://www.python.org/
    pause
    exit /b 1
)

python run_coordinator.py --mode %MODE_FLAG%

:end
pause
