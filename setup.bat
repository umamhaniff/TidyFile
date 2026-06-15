@echo off
cd /d "%~dp0"
:: TidyFile - Setup Script untuk Mendaftarkan Path dan Menyiapkan Virtual Environment
:: Jalankan script ini sekali di root direktori project setelah melakukan clone.

echo ==========================================
echo Menyiapkan TidyFile...
echo ==========================================
echo.

:: 1. Set environment variable TIDYFILE_DIR secara permanen untuk user saat ini
setx TIDYFILE_DIR "%cd%" >nul
if %errorlevel% neq 0 (
    echo [ERROR] Gagal mendaftarkan TIDYFILE_DIR ke System Environment.
    echo Silakan jalankan script ini sebagai Administrator jika diperlukan.
    goto :failed
)
echo [OK] TIDYFILE_DIR berhasil didaftarkan ke: %cd%
echo.

:: 2. Deteksi Python & Dukungan Banyak Versi
echo [INFO] Mendeteksi instalasi Python...
set "PYTHON_CMD="
where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python tidak ditemukan di sistem ini.
    echo Silakan unduh dan install Python 3.x dari https://www.python.org/
    echo Pastikan mencentang "Add Python to PATH" saat instalasi.
    goto :failed
)

echo [OK] Python ditemukan:
%PYTHON_CMD% --version
echo.

:: 3. Membuat virtual environment jika belum ada
if not exist ".venv" (
    echo [INFO] Membuat Python virtual environment .venv...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal membuat virtual environment .venv.
        goto :failed
    )
    echo [OK] Virtual environment .venv berhasil dibuat.
) else (
    echo [INFO] Virtual environment .venv sudah ada. Melewati pembuatan...
)
echo.

:: 4. Memperbarui pip (menghindari warning update)
if exist ".venv\Scripts\python.exe" (
    echo [INFO] Memperbarui pip di dalam virtual environment...
    .venv\Scripts\python.exe -m pip install --upgrade pip
    if %errorlevel% neq 0 (
        echo [WARNING] Gagal memperbarui pip. Melanjutkan instalasi dependencies...
    )
)
echo.

:: 5. Menginstall requirements
if not exist "requirements.txt" (
    echo [ERROR] File requirements.txt tidak ditemukan di root project!
    goto :failed
)

echo [INFO] Menginstall dependencies dari requirements.txt...
.venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Gagal menginstall dependencies. 
    echo Harap periksa koneksi internet Anda atau file requirements.txt.
    goto :failed
)
echo [OK] Dependencies berhasil diinstall.

echo.
echo ==========================================
echo === SETUP BERHASIL ===
echo ==========================================
echo Silakan buka terminal/PowerShell baru agar
echo environment variable TIDYFILE_DIR aktif.
echo ==========================================
pause
exit /b 0

:failed
echo.
echo ==========================================
echo === SETUP GAGAL ===
echo ==========================================
pause
exit /b 1
