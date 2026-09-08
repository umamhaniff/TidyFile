@echo off
cd /d "%~dp0"
:: ============================================================================
:: TidyFile - Setup Script untuk Mendaftarkan Path dan Menyiapkan Virtual Environment
:: Mendukung UV (Fast Package Manager) dengan fallback ke Python standard venv/pip.
:: ============================================================================

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

:: 2. Cek apakah UV tersedia
where uv >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] UV terdeteksi di sistem! Menggunakan UV untuk setup kilat...
    uv --version
    echo.
    echo [INFO] Menyiapkan environment dan sinkronisasi dependencies via UV...
    uv sync --all-extras
    if %errorlevel% neq 0 (
        echo [ERROR] Gagal sinkronisasi environment dengan UV.
        goto :failed
    )
    echo [OK] Environment dan dependencies berhasil disiapkan via UV.
    goto :success
)

:: 3. Fallback: Deteksi Python Standard & pip
echo [INFO] UV tidak ditemukan. Mendeteksi instalasi Python standard...
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
    echo [ERROR] Python / UV tidak ditemukan di sistem ini.
    echo Silakan unduh dan install Python 3.x dari https://www.python.org/
    echo Atau install UV dari https://docs.astral.sh/uv/
    echo Pastikan mencentang "Add to PATH" saat instalasi.
    goto :failed
)

echo [OK] Python ditemukan:
%PYTHON_CMD% --version
echo.

:: 4. Membuat virtual environment jika belum ada (Fallback mode)
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

:: 5. Install dependencies via pip fallback
if exist "requirements.txt" (
    echo [INFO] Menginstall dependencies dari requirements.txt...
    .venv\Scripts\pip install -r requirements.txt
) else if exist "pyproject.toml" (
    echo [INFO] Menginstall dependencies dari pyproject.toml...
    .venv\Scripts\pip install .
) else (
    echo [ERROR] File konfigurasi dependencies (pyproject.toml / requirements.txt) tidak ditemukan!
    goto :failed
)

if %errorlevel% neq 0 (
    echo [ERROR] Gagal menginstall dependencies. 
    echo Harap periksa koneksi internet Anda.
    goto :failed
)
echo [OK] Dependencies berhasil diinstall.


:success
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
