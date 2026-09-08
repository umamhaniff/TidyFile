@echo off
setlocal enabledelayedexpansion
:: ============================================================================
:: TIDYFILE SUITE - Interactive Quick Menu (Tidy File, Workstation, Moment)
:: Salin file ini ke folder mana saja, lalu klik dua kali untuk merapikannya!
:: ============================================================================

set "TARGET_DIR=%~dp0"
set "TARGET_DIR=%TARGET_DIR:\=/%"

:: Cek apakah TIDYFILE_DIR terdefinisi
if "%TIDYFILE_DIR%"=="" (
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

:MENU
cls
echo ============================================================================
echo                            TIDYFILE SUITE
echo ============================================================================
echo  Target Folder: %TARGET_DIR%
echo ============================================================================
echo  [1] Tidy File        - Rapikan Kategori & Ekstensi (Documents, Images, dll.)
echo  [2] Tidy Workstation - Rapikan Dokumen Kerja ^(Workstation/YYYY/MM/DD^)
echo  [3] Tidy Moment      - Rapikan Foto & Video ^(Moment/YYYY/MM/DD^)
echo  [4] Keluar
echo ============================================================================
set /p CHOICE="Pilih mode [1-4]: "

if "%CHOICE%"=="1" (
    echo.
    echo [INFO] Menjalankan Tidy File...
    ".venv\Scripts\python.exe" -m src.main tidy --path "%TARGET_DIR%"
    goto END
)
if "%CHOICE%"=="2" (
    echo.
    echo [INFO] Menjalankan Tidy Workstation...
    ".venv\Scripts\python.exe" -m src.main workstation --path "%TARGET_DIR%"
    goto END
)
if "%CHOICE%"=="3" (
    echo.
    echo [INFO] Menjalankan Tidy Moment...
    ".venv\Scripts\python.exe" -m src.main moment --path "%TARGET_DIR%"
    goto END
)
if "%CHOICE%"=="4" (
    echo Membatalkan operasi.
    exit /b 0
)

echo Pilihan tidak valid. Silakan masukkan angka 1-4.
timeout /t 2 >nul
goto MENU

:END
echo.
echo ============================================================================
echo Pembersihan selesai!
echo ============================================================================
pause
