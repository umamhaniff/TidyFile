# 🧹 TidyFile Suite: Central Organizer & Moment Manager

[![Latest Tag](https://img.shields.io/github/v/tag/umamhaniff/TidyFile?color=brightgreen&label=version)](https://github.com/umamhaniff/TidyFile/tags)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Dependencies](https://img.shields.io/badge/dependencies-pillow%20%7C%20tinytag%20%7C%20hachoir%20%7C%20watchdog-orange.svg)](#)
[![Tests Status](https://img.shields.io/badge/tests-53%20passing-brightgreen.svg)](#-testing)

**TidyFile Suite** adalah utilitas otomatisasi modular berbasis Python yang dirancang untuk merapikan direktori berantakan (seperti `Downloads`, `Desktop`, folder foto/video, dokumen kerja, dll.) secara cerdas, aman, dan berkinerja tinggi.

---

## 🌟 3 Mode Pengorganisasian Spesifik

1. **📁 Tidy File (Core):**
   * Merapikan file ke subfolder kategori (`Documents`, `Images`, `Code_and_Projects`, `Audio_and_Video`, `Data_and_Models`, dll.) berdasarkan ekstensi.
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
- ⏱️ **Deteksi Cooldown Browser:** Mengabaikan file sementara unduhan (`.crdownload`, `.part`, `.tmp`) hingga proses download selesai sempurna.
- 🔕 **Silent Execution:** Didukung script VBScript (`scripts/run_watcher.vbs`) agar pemantauan background berjalan tanpa pop-up window CMD.
- ⚡ **Lightweight (8GB RAM Safe):** Menggunakan lazy header parsing tanpa memuat dekompresi file penuh ke dalam memori RAM.

---

## 📂 Struktur Direktori Project

```text
TidyFile/
├── src/
│   ├── __init__.py          # Penanda paket python & versi
│   ├── main.py              # Entrypoint CLI, subcommand & interactive menu
│   ├── metadata_parser.py   # 3-Tier Date Extractor (EXIF, Video, Regex, mtime)
│   ├── config_manager.py    # Handler konfigurasi & fallback
│   ├── core.py              # Logika BaseOrganizer, FileOrganizer, WorkstationOrganizer, MomentOrganizer
│   └── watcher.py           # Pemantau real-time (Watchdog daemon)
├── tests/
│   ├── __init__.py
│   ├── test_config.py       # Unit test konfigurasi
│   ├── test_core.py         # Unit test logika perpindahan & hash
│   ├── test_metadata_parser.py # Unit test ekstraksi metadata & regex
│   ├── test_modes.py        # Unit test Workstation & Moment organizers
│   ├── test_main.py         # Unit test CLI arguments & menu
│   └── test_watcher.py      # Unit test event watcher
├── scripts/
│   ├── run_once.bat         # Batch eksekusi sekali jalan
│   └── run_watcher.vbs      # VBScript background watcher (silent)
├── tidy_here.bat            # Quick batch menu interaktif portabel (1-4)
├── setup.bat                # Installer environment otomatis
├── requirements.txt         # Daftar dependency
├── config.json.example      # Template konfigurasi
├── README.md                # Dokumentasi utama GitHub
└── gemini.md                # Konteks persistent memori
```

---

## 🚀 Memulai (Quick Start)

### 1. Setup Project
Cukup jalankan setup otomatis sekali:
1. Double-click file `setup.bat` di root direktori project.
2. Script akan membuat virtual environment `.venv`, menginstal semua library (`requirements.txt`), dan mendaftarkan `TIDYFILE_DIR`.

### 2. Konfigurasi Folder
Salin `config.json.example` menjadi `config.json`:
```json
{
  "target_folders": [
    "D:/Downloads"
  ]
}
```

---

## 💻 Cara Penggunaan

### A. Quick Menu Interaktif Portabel (`tidy_here.bat`) ⭐ *Paling Praktis*
Salin `tidy_here.bat` ke folder mana saja yang ingin kamu rapikan, lalu double-click:
```text
============================================================================
                           TIDYFILE SUITE
============================================================================
 Target Folder: D:/FotoLiburan
============================================================================
 [1] Tidy File        - Rapikan Kategori & Ekstensi (Documents, Images, dll.)
 [2] Tidy Workstation - Rapikan Dokumen Kerja (Workstation/YYYY/MM/DD)
 [3] Tidy Moment      - Rapikan Foto & Video (Moment/YYYY/MM/DD)
 [4] Keluar
============================================================================
Pilih mode [1-4]: 
```

### B. Python CLI (Subcommands)
```powershell
# 1. Mode Tidy File
python -m src.main tidy --path "D:/Target"

# 2. Mode Tidy Workstation
python -m src.main workstation --path "D:/Target"

# 3. Mode Tidy Moment
python -m src.main moment --path "D:/Target"

# Mode Watchdog (Real-time Background)
python -m src.main tidy --watch
```

---

## 🧪 Testing

Semua unit test menggunakan folder tiruan sementara (`tempfile`) yang aman:
```powershell
# Jalankan seluruh test suite
python -m unittest discover -s tests

# Jalankan dengan coverage
.venv\Scripts\python -m coverage run -m unittest discover -s tests
.venv\Scripts\python -m coverage report -m
```
