# 🧹 TidyFile Suite: Central Organizer & Moment Manager

[![Latest Tag](https://img.shields.io/github/v/tag/umamhaniff/TidyFile?color=brightgreen&label=version)](https://github.com/umamhaniff/TidyFile/tags)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Package Manager](https://img.shields.io/badge/managed%20by-uv-purple.svg)](https://docs.astral.sh/uv/)
[![Tests Status](https://img.shields.io/badge/tests-53%20passing-brightgreen.svg)](#-testing)

**TidyFile Suite v3.0.0** adalah utilitas otomatisasi modular berbasis Python dan standalone executable yang dirancang untuk merapikan direktori berantakan (seperti `Downloads`, `Desktop`, folder foto/video, dokumen kerja, dataset AI, dll.) secara cerdas, aman, dan berkinerja tinggi.

---

## 🌟 3 Mode Pengorganisasian Spesifik

1. **📁 Tidy File (Core):**
   * Merapikan file ke subfolder kategori (`Documents`, `Images`, `Code_and_Projects`, `Audio_and_Video`, `Data_and_Models`, `Compressed_and_Packages`, `Fonts`, `Others`) berdasarkan ekstensi.
2. **💼 Tidy Workstation:**
   * Merapikan dokumen kerja berdasarkan tanggal metadata ke dalam hirarki `Workstation/YYYY/MM/DD/`.
3. **📸 Tidy Moment:**
   * Merapikan foto, video, dan audio dari berbagai format dan perangkat ke dalam hirarki `Moment/YYYY/MM/DD/`.

---

## 🔍 Pipeline Ekstraksi Tanggal 3-Tier (MetadataParser)

Untuk mode **Tidy Workstation** dan **Tidy Moment**, sistem menggunakan alur cerdas 3-Tier:
1. **Tier 1 (Embedded Metadata):**
   * Foto: EXIF tag (`DateTimeOriginal` / `DateTimeDigitized` / `DateTime`) via Pillow & `pillow-heif` (dukungan format HEIC/Apple).
   * Video & Audio: Atom container timestamps via `tinytag` & `hachoir`.
2. **Tier 2 (Filename Pattern Matching):**
   * WhatsApp: `IMG-YYYYMMDD-WA...`, `VID-YYYYMMDD-WA...`
   * Kamera & Screenshot: `IMG_YYYYMMDD_...`, `Screenshot_YYYY-MM-DD...`, `PXL_YYYYMMDD_...`
   * Pola ISO & Format Standar: `YYYY-MM-DD`, `YYYYMMDD`, `DD-MM-YYYY`
3. **Tier 3 (Filesystem Timestamps):**
   * Fallback otomatis ke modified / creation time filesystem (`os.path.getmtime`).

---

## ✨ Fitur Keamanan & Performa

- 🛡️ **Anti-Collision & Proteksi Duplikat (SHA-256):** Menghapus file identik di root secara aman jika isi file 100% sama dengan file di tujuan.
- 🔄 **Re-versioning Otomatis:** Mengubah nama file dengan indeks angka (misal: `laporan_1.pdf`) secara dinamis apabila namanya sama tetapi isinya berbeda.
- 🚫 **Self-Protection:** File program (`tidyfile.exe`, `.bat`, `config.json`, project files) otomatis diabaikan sehingga tidak akan pernah terpindah atau terhapus sendiri.
- ⏱️ **Deteksi Cooldown Browser:** Mengabaikan file sementara unduhan (`.crdownload`, `.part`, `.tmp`) hingga proses download selesai sempurna.
- ⚡ **Lightweight & High-Performance:** Menggunakan `uv` untuk manajemen dependencies instan dan lazy header parsing yang aman untuk hardware 8GB RAM.

---

## 📂 Struktur Direktori Project

```text
TidyFile/
├── src/
│   ├── __init__.py          # Penanda paket python & versi (v3.0.0)
│   ├── main.py              # Entrypoint CLI, subcommand & interactive menu
│   ├── metadata_parser.py   # 3-Tier Date Extractor (EXIF, Video, Regex, mtime)
│   ├── config_manager.py    # Handler konfigurasi & fallback categories
│   ├── core.py              # Logika BaseOrganizer, FileOrganizer, WorkstationOrganizer, MomentOrganizer
│   └── watcher.py           # Pemantau real-time (Watchdog daemon)
├── tests/
│   ├── __init__.py
│   ├── test_config.py       # Unit test konfigurasi & path expansion
│   ├── test_core.py         # Unit test logika perpindahan & SHA-256 deduplikasi
│   ├── test_metadata_parser.py # Unit test ekstraksi metadata & regex
│   ├── test_modes.py        # Unit test Workstation & Moment organizers
│   ├── test_main.py         # Unit test CLI arguments & interactive menu
│   └── test_watcher.py      # Unit test event watcher
├── scripts/
│   ├── run_once.bat         # Batch eksekusi sekali jalan
│   └── run_watcher.vbs      # VBScript background watcher (silent)
├── tidy_here.bat            # Batch launcher interaktif
├── setup.bat                # Setup environment otomatis (UV + Python fallback)
├── build.bat                # 1-Click compiler ke standalone portable EXE
├── pyproject.toml           # Definisi dependencies standar modern PEP 621 (UV)
├── uv.lock                  # Universal lockfile UV
├── config.json.example      # Template konfigurasi kustom
└── README.md                # Dokumentasi utama GitHub
```

---

## 🚀 Cara Penggunaan

### A. 📦 Jalur Standalone Portable (`tidyfile.exe`) ⭐ *Paling Praktis untuk User*
1. Unduh **`tidyfile.exe`** dari rilis.
2. Letakkan file `tidyfile.exe` di folder mana saja yang ingin dirapikan.
3. **Double-click** `tidyfile.exe` dan pilih mode `[1-4]` pada menu interaktif:
```text
==========================================================
                      TIDYFILE SUITE
==========================================================
 Target Folder : D:/FotoLiburan
==========================================================
 [1] Tidy File        (Organize by Category & Extension)
 [2] Tidy Workstation (Work Files -> Workstation/YYYY/MM/DD)
 [3] Tidy Moment      (Photos & Videos -> Moment/YYYY/MM/DD)
 [4] Keluar
==========================================================
Pilih mode [1-4]: 
```

### B. 🛠️ Jalur Developer / CLI (via UV)

1. **Setup Awal:**
   ```powershell
   # Sinkronisasi environment kilat via UV
   uv sync --all-extras
   ```

2. **Eksekusi Subcommand:**
   ```powershell
   # 1. Mode Tidy File
   uv run python -m src.main tidy --path "D:/Target"

   # 2. Mode Tidy Workstation
   uv run python -m src.main workstation --path "D:/Target"

   # 3. Mode Tidy Moment
   uv run python -m src.main moment --path "D:/Target"

   # 4. Mode Watchdog (Real-time Background)
   uv run python -m src.main tidy --watch
   ```

3. **Build Binary Portable Baru:**
   ```powershell
   .\build.bat
   ```

---

## 🧪 Testing

Semua unit test terisolasi menggunakan folder tiruan sementara (`tempfile`) yang aman:
```powershell
# Menjalankan seluruh test suite dengan coverage via UV
uv run coverage run -m unittest discover -s tests
uv run coverage report -m
```
