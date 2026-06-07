# Design Specification: TidyFile Central Organizer

**Date:** 2026-06-07  
**Status:** Approved (Design Phase Complete)  
**Author:** Antigravity (AI Coding Assistant)  

---

## 1. Overview & Goal
TidyFile is a central file organizing application written in Python. It is designed to automatically clean and organize messy directories (such as `Downloads`, `Desktop`, `Documents`) by routing files into structured subfolders based on their extensions. It runs in two modes: one-off execution (triggered manually or via Windows Task Scheduler) and real-time monitoring (utilizing a background daemon with the `watchdog` library).

A critical requirement is robust file collision handling (handling files with the same name via content hash comparison) to prevent accidental data loss or overwriting.

---

## 2. Directory Structure
The project will follow a modular Python package layout to ensure clean separation of concerns and high testability.

```
TidyFile/
├── .gitignore                  # Ignores .venv, logs, local guides, and temporary files
├── README.md                   # Professional GitHub-friendly documentation
├── requirements.txt            # Package dependencies (e.g., watchdog)
├── config.json.example         # Template configuration for categories & targets
├── src/
│   ├── __init__.py             # Makes 'src' a Python package
│   ├── main.py                 # CLI entrypoint, argument parsing, & logging init
│   ├── config_manager.py       # Reads and validates config.json
│   ├── core.py                 # Core scanning, hash calculation, and move logic
│   └── watcher.py              # Watchdog event handler for real-time mode
├── tests/
│   ├── __init__.py
│   └── test_core.py            # Unit tests for core moving & renaming logic
└── scripts/
    ├── run_once.bat            # Script to run organizer once (called anywhere)
    └── run_watcher.vbs         # Runs watchdog script silently in the background
```

---

## 3. Configuration System
User settings are stored in `config.json` (ignored by Git, but documented via `config.json.example`).

### Configuration Schema Example
```json
{
  "target_folders": [
    "D:/Downloads"
  ],
  "categories": {
    "Documents": [
      ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", 
      ".txt", ".rtf", ".odt", ".ods", ".odp", ".csv", ".md", 
      ".pages", ".numbers", ".key", ".epub", ".mobi", ".azw", ".azw3", 
      ".gdoc", ".gsheet", ".gslides", ".wps", ".wpt", ".dps"
    ],
    "Data_and_Models": [
      ".json", ".parquet", ".pkl", ".sqlite", ".db", ".db3", 
      ".tsv", ".yaml", ".yml", ".xml", ".h5", ".feather", 
      ".pb", ".onnx", ".tflite", ".bin", ".hdf5", ".mat", ".csv"
    ],
    "Code_and_Projects": [
      ".py", ".ipynb", ".sql", ".js", ".ts", ".html", ".css", 
      ".c", ".cpp", ".h", ".cs", ".java", ".kt", ".swift", 
      ".dart", ".sh", ".bat", ".ps1", ".go", ".rs", ".php", ".rb",
      ".json", ".xml", ".yaml", ".yml"
    ],
    "BI_and_Design_Links": [
      ".twbx", ".twb", ".pbix", ".pbit", ".fig", ".xd", ".sketch", ".cdr"
    ],
    "Images": [
      ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", 
      ".heic", ".heif", ".psd", ".ai", ".svg", ".raw", ".cr2", ".nef"
    ],
    "Audio_and_Video": [
      ".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".3gp", 
      ".mpeg", ".mpg", ".m4v", ".mp3", ".wav", ".m4a", ".flac", ".aac", 
      ".ogg", ".wma", ".opus", ".mid", ".midi", ".amr"
    ],
    "Compressed_and_Packages": [
      ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".cab", ".img",
      ".dmg", ".pkg", ".apk", ".aab", ".ipa", ".exe", ".msi"
    ],
    "Fonts": [
      ".ttf", ".otf", ".woff", ".woff2", ".eot"
    ]
  },
  "default_category": "Others"
}
```

---

## 4. Core Logic & Collision Handling

The script processes files in the root level of target directories and ignores the categorized subdirectories to avoid recursive processing.

### Collision Handling Algorithm
When moving a file (e.g., `Downloads/tugas.pdf` to `Downloads/Documents/tugas.pdf`):
1. If the destination file **does not exist**, move it immediately.
2. If the destination file **already exists**:
   * Calculate the **SHA-256 hash** of both the source file and the destination file.
   * **If Hashes are Identical:** The files are duplicates. Delete the source file to free space and prevent mess. Log: `[WARNING] Duplicate file detected: <filename>. Deleting duplicate.`
   * **If Hashes are Different:** They are different versions of the file. Rename the source file using a counter (e.g., `tugas_1.pdf`) and move it. Ensure the counter itself is checked to prevent overwriting existing counter files. Log: `[INFO] Version conflict for <filename>. Renamed to <new_filename>.`

---

## 5. Execution Modes

### Mode 1: One-Off Cleaning
* Activated by: `python -m src.main` or via `run_once.bat`.
* Scans all root directories in `target_folders`, moves eligible files, and terminates.
* Ideal for Windows Task Scheduler setup (e.g., run every day at 4:00 PM).

### Mode 2: Watchdog Monitoring (Real-time)
* Activated by: `python -m src.main --watch`.
* Uses the `watchdog` library to listen to filesystem events in target folders.
* **Chrome/Firefox Download Cooldown:**
  * Temporary files (`.crdownload`, `.part`, `.tmp`) are ignored.
  * When a `.crdownload` file is renamed to its final extension (triggering a rename/move event) or a new file is created, the watcher triggers the cleanup logic.
  * Before moving, the file lock is checked. If locked (currently being written), the script waits and retries using exponential backoff (e.g., wait 1s, 2s, 4s).

---

## 6. Logging Specifications
All logs are written to `tidyfile.log` (ignored by Git) and printed to stdout. Messages must be clear, actionable, and human-friendly:

* **Success:** `[INFO] Dipindahkan: "Downloads/laporan.xlsx" -> "Downloads/Documents/laporan.xlsx"`
* **Duplicate:** `[WARNING] Duplikat Terdeteksi (Isi Identik): "Downloads/invoice.pdf" sama dengan "Downloads/Documents/invoice.pdf". Menghapus duplikat di root.`
* **Version Renaming:** `[INFO] Konflik Nama Terdeteksi (Isi Berbeda): "Downloads/tugas.docx" memiliki versi berbeda di tujuan. Memindahkan sebagai "Downloads/Documents/tugas_1.docx".`
* **Locked Files:** `[WARNING] Gagal memindahkan "Downloads/tugas.docx": File sedang dibuka oleh program lain. Silakan tutup program tersebut.`
* **JSON Syntax Errors:** `[ERROR] Gagal membaca config.json: Format JSON rusak pada baris X. Menggunakan konfigurasi default.`

---

## 7. Testing Strategy
* Tests are located in `tests/test_core.py`.
* Uses `unittest` and `tempfile.TemporaryDirectory` to isolate testing from real user files.
* Test cases cover:
  1. Successful move to proper category.
  2. Fallback to `Others` folder for untracked extensions.
  3. Duplicate deletion (hash check match).
  4. File auto-renaming (hash check mismatch).

---

## 8. Git and Local Files Management
To respect privacy and protect local environments:
* **`.gitignore`** will ignore `.venv/`, `config.json`, `tidyfile.log`, and `LOCAL_GUIDE.md`.
* **`LOCAL_GUIDE.md`** contains setup instructions (activating venv, installing dependencies, configuring task scheduler) and remains local (untracked by Git).
