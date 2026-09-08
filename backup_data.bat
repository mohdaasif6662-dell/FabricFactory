@echo off
title Malik Garments - Backup
cd /d "%~dp0"

if not exist "backups\" mkdir backups

:: Create a backup filename with today's date
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set today=%%c-%%a-%%b)

copy db.sqlite3 "backups\db_backup_%today%.sqlite3" >nul

echo.
echo Backup ho gaya: backups\db_backup_%today%.sqlite3
echo Is file ko chaho to USB ya Google Drive mein bhi copy kar lein.
echo.
pause
