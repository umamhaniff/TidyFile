@echo off
setlocal enabledelayedexpansion
:: ============================================================================
:: TIDYFILE SUITE - Interactive Quick Menu (Tidy File, Workstation, Moment)
:: Salin file ini ke folder mana saja, lalu klik dua kali untuk merapikannya!
:: ============================================================================

set "TARGET_DIR=%~dp0"
set "TARGET_DIR=%TARGET_DIR:\=/%"

:: 1. Deteksi apakah ada standalone tidyfile.exe di folder yang sama
set "RUNNER="
if exist "%~dp0tidyfile.exe" (
    set "RUNNER=%~dp0tidyfile.exe"
    goto :MENU
)
if exist "%~dp0dist\tidyfile.exe" (
    set "RUNNER=%~dp0dist\tidyfile.exe"
    goto :MENU
)

:: 2. Cek apakah TIDYFILE_DIR terdefinisi
if "%TIDYFILE_DIR%"=="" (
    if exist "%~dp0.venv\Scripts\python.exe" (
        set "TIDYFILE_DIR=%~dp0"
    ) else (
        echo Error: Environment variable TIDYFILE_DIR belum terdaftar atau tidyfile.exe tidak ditemukan.
        echo Silakan jalankan setup.bat terlebih dahulu di root folder project TidyFile.
        pause
        exit /b 1
    )
)

:: 3. Cek di dalam TIDYFILE_DIR
if exist "%TIDYFILE_DIR%\dist\tidyfile.exe" (
    set "RUNNER=%TIDYFILE_DIR%\dist\tidyfile.exe"
    goto :MENU
)
if exist "%TIDYFILE_DIR%\tidyfile.exe" (
    set "RUNNER=%TIDYFILE_DIR%\tidyfile.exe"
    goto :MENU
)

if not exist "%TIDYFILE_DIR%\.venv\Scripts\python.exe" (
    echo Error: Runtime Python virtual environment atau tidyfile.exe tidak ditemukan di:
    echo "%TIDYFILE_DIR%"
    pause
    exit /b 1
)

:MENU
cls
echo ============================================================================
echo                            TIDYFILE SUITE
echo ============================================================================
echo  Target Folder : %TARGET_DIR%
echo ============================================================================
echo  [1] Tidy File        - Rapikan Kategori ^& Ekstensi (Documents, Images, dll.)
echo  [2] Tidy Workstation - Rapikan Dokumen Kerja ^(Workstation/YYYY/MM/DD^)
echo  [3] Tidy Moment      - Rapikan Foto ^& Video ^(Moment/YYYY/MM/DD^)
echo  [4] Keluar
echo ============================================================================
set /p CHOICE="Pilih mode [1-4]: "

if "%CHOICE%"=="1" set "MODE=tidy" & goto :EXECUTE
if "%CHOICE%"=="2" set "MODE=workstation" & goto :EXECUTE
if "%CHOICE%"=="3" set "MODE=moment" & goto :EXECUTE
if "%CHOICE%"=="4" (
    echo Membatalkan operasi.
    exit /b 0
)

echo Pilihan tidak valid. Silakan masukkan angka 1-4.
timeout /t 2 >nul
goto :MENU

:EXECUTE
echo.
echo [INFO] Menjalankan TidyFile mode: %MODE%...
if not "%RUNNER%"=="" (
    "%RUNNER%" %MODE% --path "%TARGET_DIR%"
) else (
    cd /d "%TIDYFILE_DIR%"
    ".venv\Scripts\python.exe" -m src.main %MODE% --path "%TARGET_DIR%"
)

echo.
echo ============================================================================
echo Pembersihan selesai!
echo ============================================================================
pause
exit /b 0
