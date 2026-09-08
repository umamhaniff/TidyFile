@echo off
cd /d "%~dp0"
:: ============================================================================
:: TidyFile - Build Script (Portable Single EXE Generator)
:: ============================================================================

echo ====================================================
echo        TidyFile Portable Executable Builder
echo ====================================================
echo.

:: 1. Cek ketersediaan UV atau Python
where uv >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Menggunakan UV untuk build super cepat...
    echo [INFO] Memastikan dependencies dev dan pyinstaller terpasang...
    uv sync --all-extras
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal sinkronisasi environment dengan UV.
        goto :failed
    )
    echo.
    echo [INFO] Mengompilasi TidyFile ke single-file portable .exe...
    uv run pyinstaller --noconfirm --clean --onefile --name tidyfile src/main.py
) else (
    echo [INFO] UV tidak terdeteksi, menggunakan virtual environment Python...
    if not exist ".venv\Scripts\python.exe" (
        echo [ERROR] Virtual environment .venv belum siap. Jalankan setup.bat terlebih dahulu.
        goto :failed
    )
    .venv\Scripts\pip install pyinstaller
    .venv\Scripts\pyinstaller --noconfirm --clean --onefile --name tidyfile src/main.py
)

if %errorlevel% neq 0 (
    echo [ERROR] Terjadi kesalahan saat proses kompilasi PyInstaller.
    goto :failed
)

echo.
echo ====================================================
echo [SUKSES] Binary Portable siap digunakan!
echo Lokasi File: %cd%\dist\tidyfile.exe
echo ====================================================
echo File dist\tidyfile.exe bersifat 100%% portable (zero dependency).
echo Kamu bisa membagikan file tersebut ke komputer manapun tanpa instalasi.
echo.
pause
exit /b 0

:failed
echo.
echo ====================================================
echo [GAGAL] Proses build tidak berhasil diselesaikan.
echo ====================================================
pause
exit /b 1
