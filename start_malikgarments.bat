@echo off
title Malik Garments - Server
color 0A

:: ============================================
:: MALIK GARMENTS - Auto Setup & Launch Script
:: ============================================

cd /d "%~dp0"

echo.
echo ================================================
echo   MALIK GARMENTS - Starting Application
echo ================================================
echo.

:: Step 1: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nahi mila is computer par!
    echo.
    echo Please pehle Python install karein:
    echo 1. python.org kholein
    echo 2. Latest version download karein
    echo 3. Install karte waqt "Add Python to PATH" ZAROOR tick karein
    echo 4. Install hone ke baad is file ko dobara chalayein
    echo.
    pause
    exit /b
)

:: Step 2: Check if this is FIRST TIME setup (venv doesn't exist)
if not exist "venv\" (
    echo [SETUP] Pehli baar chal raha hai - sab kuch install ho raha hai...
    echo Ye sirf ek baar hoga, thoda time lagega. Please wait...
    echo.

    python -m venv venv
    call venv\Scripts\activate.bat

    echo [SETUP] Requirements install ho rahi hain...
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt

    echo [SETUP] Database taiyar ki ja rahi hai...
    python manage.py migrate

    echo.
    echo [SETUP] Setup complete! Ab app khul rahi hai...
    echo.
) else (
    :: Already set up - just activate
    call venv\Scripts\activate.bat
)

:: Step 3: Get local IP address for phone access
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set LOCALIP=%%a
    goto :found
)
:found
set LOCALIP=%LOCALIP: =%

echo ================================================
echo   Server chalu ho raha hai...
echo ================================================
echo.
echo   Is computer par kholne ke liye:
echo   http://127.0.0.1:8000
echo.
echo   Phone se kholne ke liye (same WiFi par):
echo   http://%LOCALIP%:8000
echo.
echo   Band karne ke liye ye window band kar dein
echo ================================================
echo.

:: Step 4: Open browser automatically after a short delay
start "" cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8000"

:: Step 5: Start the Django server (network-wide)
python manage.py runserver 0.0.0.0:8000

pause
