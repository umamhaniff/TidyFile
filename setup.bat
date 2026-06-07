@echo off
:: TidyFile - Setup Script untuk Mendaftarkan Path dan Menyiapkan Virtual Environment
:: Jalankan script ini sekali di root direktori project setelah melakukan clone.

echo Menyiapkan TidyFile...

:: Set environment variable TIDYFILE_DIR secara permanen untuk user saat ini
setx TIDYFILE_DIR "%cd%" >nul
if %errorlevel% neq 0 (
    echo [ERROR] Gagal mendaftarkan TIDYFILE_DIR. Silakan jalankan script ini sebagai Administrator jika diperlukan.
    pause
    exit /b 1
)
echo [OK] TIDYFILE_DIR berhasil didaftarkan ke: %cd%

:: Membuat virtual environment jika belum ada
if not exist ".venv" (
    echo [INFO] Membuat Python virtual environment (.venv)...
    python -m venv .venv
)

:: Menginstall requirements
echo [INFO] Menginstall dependencies...
.venv\Scripts\pip install -r requirements.txt

echo.
echo === SETUP BERHASIL ===
echo Silakan buka terminal baru agar environment variable TIDYFILE_DIR aktif.
pause
