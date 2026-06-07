@echo off
:: TidyFile - Script untuk merapikan folder tempat file .bat ini diletakkan.
:: Salin file ini ke folder mana saja, lalu klik dua kali untuk merapikannya!

set "TARGET_DIR=%~dp0"
cd /d "D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile"
".venv\Scripts\python.exe" -m src.main --path "%TARGET_DIR%"
pause
