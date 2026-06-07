@echo off
:: TidyFile - Script untuk merapikan folder tempat file .bat ini diletakkan.
:: Salin file ini ke folder mana saja, lalu klik dua kali untuk merapikannya!

set "TARGET_DIR=%~dp0"
:: Replace backslashes with forward slashes to prevent escaping issues while preserving drive roots (e.g. D:/)
set "TARGET_DIR=%TARGET_DIR:\=/%"

:: Cek apakah TIDYFILE_DIR terdefinisi
if "%TIDYFILE_DIR%"=="" (
    :: Fallback: jika dijalankan langsung di root project
    if exist "%~dp0.venv\Scripts\python.exe" (
        set "TIDYFILE_DIR=%~dp0"
    ) else (
        echo Error: Environment variable TIDYFILE_DIR belum terdaftar.
        echo Silakan jalankan setup.bat terlebih dahulu di root folder project TidyFile.
        pause
        exit /b 1
    )
)

cd /d "%TIDYFILE_DIR%" || (
    echo Error: Folder project tidak ditemukan di:
    echo "%TIDYFILE_DIR%"
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Error: Folder project atau Python virtual environment tidak ditemukan di:
    echo "%TIDYFILE_DIR%"
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m src.main --path "%TARGET_DIR%"
pause
