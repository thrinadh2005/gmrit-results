@echo off
title GMRIT Results Scraper Launcher
setlocal enabledelayedexpansion

echo ======================================================
echo     GMRIT Results Scraper - Desktop Launcher
echo ======================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH!
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

:: First-time setup (optional but recommended)
if not exist "venv" (
    echo Creating virtual environment for the first time...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
    
    echo.
    set /p "create_shortcut=Would you like to create a desktop shortcut for easy access? (y/n): "
    if /i "!create_shortcut!"=="y" (
        echo Creating desktop shortcut...
        set "scriptPath=%~f0"
        set "shortcutName=GMRIT Results Scraper.lnk"
        set "desktopPath=%USERPROFILE%\Desktop"
        
        powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut(\"$desktopPath\!shortcutName!\"); $Shortcut.TargetPath = \"!scriptPath!\"; $Shortcut.WorkingDirectory = \"%~dp0\"; $Shortcut.IconLocation = \"powershell.exe\"; $Shortcut.Save()"
        echo Shortcut created on your desktop!
    )
) else (
    call venv\Scripts\activate
)

:: Launch the desktop app
echo Starting application...
python desktop_main.py

if %errorlevel% neq 0 (
    echo.
    echo Application closed with an error (Code: %errorlevel%).
    pause
)

endlocal
