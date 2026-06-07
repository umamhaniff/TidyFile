@echo off
:: TidyFile - Script untuk merapikan folder tempat file .bat ini diletakkan.
:: Salin file ini ke folder mana saja, lalu klik dua kali untuk merapikannya!

set "TARGET_DIR=%~dp0"
:: Replace backslashes with forward slashes to prevent escaping issues while preserving drive roots (e.g. D:/)
set "TARGET_DIR=%TARGET_DIR:\=/%"

cd /d "D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile" || (
    echo Error: Folder project tidak ditemukan di:
    echo D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Error: Folder project atau Python virtual environment tidak ditemukan di:
    echo D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m src.main --path "%TARGET_DIR%"
pause
