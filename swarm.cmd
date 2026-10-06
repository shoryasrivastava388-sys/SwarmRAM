@echo off
if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    "%LOCALAPPDATA%\Python\bin\python.exe" "%~dp0swarm_cli.py" %*
    exit /b %errorlevel%
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" "%~dp0swarm_cli.py" %*
    exit /b %errorlevel%
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%~dp0swarm_cli.py" %*
    exit /b %errorlevel%
)
where python >nul 2>nul
if %errorlevel% equ 0 (
    python "%~dp0swarm_cli.py" %*
    exit /b %errorlevel%
)

echo [!] Python not found. Please install Python or add it to PATH.
exit /b 1
