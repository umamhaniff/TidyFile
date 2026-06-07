@echo off
:: TidyFile - Script untuk merapikan folder tempat file .bat ini diletakkan.
:: Salin file ini ke folder mana saja, lalu klik dua kali untuk merapikannya!

set "TARGET_DIR=%~dp0"
:: Strip trailing backslash to prevent escaping issues with quotes in python arguments
if "%TARGET_DIR:~-1%"=="\" set "TARGET_DIR=%TARGET_DIR:~0,-1%"

cd /d "D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile"
if not exist ".venv\Scripts\python.exe" (
    echo Error: Folder project atau Python virtual environment tidak ditemukan di:
    echo D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m src.main --path "%TARGET_DIR%"
pause
