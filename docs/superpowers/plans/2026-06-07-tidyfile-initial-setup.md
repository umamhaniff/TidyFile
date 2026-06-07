# TidyFile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modular, automated Python utility that cleans and organizes files from target directories into categorized subfolders based on extension, featuring hash-based duplicate deletion, version renaming, and silent real-time background watchdog monitoring.

**Architecture:** A modular Python package structured into core file-moving and duplicate-checking logic, a configuration manager reading from a JSON config file, and a watchdog-based real-time listener. Command execution is handled via a unified CLI entry point, and Windows automation is achieved via helper batch and VBScript files.

**Tech Stack:** Python 3.x, pathlib, shutil, hashlib, logging, watchdog, unittest.

---

### Task 1: Project Scaffolding, Gitignore & Requirements

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `config.json.example`

- [ ] **Step 1: Create the `.gitignore` file**
  Create the `.gitignore` file to ensure personal configuration, virtual environment, and log files are not checked into git.
  
  ```gitignore
  # Virtual environment
  .venv/
  __pycache__/
  *.py[cod]
  *$py.class

  # Project configurations and outputs
  config.json
  tidyfile.log

  # Local guides and documents (ignored as requested)
  LOCAL_GUIDE.md
  
  # VS Code and temporary files
  .vscode/
  .idea/
  *.tmp
  *.crdownload
  *.part
  ```

- [ ] **Step 2: Create `requirements.txt`**
  Add required dependencies. We only need `watchdog` for background file monitoring.
  
  ```text
  watchdog==4.0.0
  ```

- [ ] **Step 3: Create `config.json.example`**
  Provide a template configuration file for users.
  
  ```json
  {
    "target_folders": [
      "C:/Users/Public/Downloads"
    ],
    "categories": {
      "Documents": [
        ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", 
        ".txt", ".rtf", ".odt", ".ods", ".odp", ".csv", ".md", 
        ".pages", ".numbers", ".key", ".epub", ".mobi", ".gdoc", ".gsheet"
      ],
      "Data_and_Models": [
        ".json", ".parquet", ".pkl", ".sqlite", ".db", ".db3", 
        ".tsv", ".yaml", ".yml", ".xml", ".h5", ".feather", 
        ".pb", ".onnx", ".tflite", ".bin"
      ],
      "Code_and_Projects": [
        ".py", ".ipynb", ".sql", ".js", ".ts", ".html", ".css", 
        ".c", ".cpp", ".h", ".cs", ".java", ".kt", ".swift", 
        ".dart", ".sh", ".bat", ".ps1", ".go", ".rs", ".php", ".rb"
      ],
      "BI_and_Design_Links": [
        ".twbx", ".twb", ".pbix", ".pbit", ".fig", ".xd", ".sketch"
      ],
      "Images": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", 
        ".heic", ".heif", ".psd", ".ai", ".svg", ".raw", ".cr2", ".nef"
      ],
      "Audio_and_Video": [
        ".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".3gp", 
        ".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".wma", ".opus"
      ],
      "Compressed_and_Packages": [
        ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", 
        ".dmg", ".pkg", ".apk", ".aab", ".ipa", ".exe", ".msi"
      ]
    },
    "default_category": "Others"
  }
  ```

- [ ] **Step 4: Commit**
  Run:
  ```bash
  git add .gitignore requirements.txt config.json.example
  git commit -m "chore: setup scaffolding, requirements, and config template"
  ```

---

### Task 2: Config Manager

**Files:**
- Create: `src/__init__.py`
- Create: `src/config_manager.py`
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests for Config Manager**
  Create `tests/test_config.py` to test reading valid and invalid config JSON.
  
  ```python
  import unittest
  import json
  import tempfile
  from pathlib import Path
  from src.config_manager import ConfigManager

  class TestConfigManager(unittest.TestCase):
      def setUp(self):
          self.temp_dir = tempfile.TemporaryDirectory()
          self.config_path = Path(self.temp_dir.name) / "config.json"

      def tearDown(self):
          self.temp_dir.cleanup()

      def test_load_valid_config(self):
          config_data = {
              "target_folders": ["C:/TestDownloads"],
              "categories": {"Docs": [".pdf"]},
              "default_category": "Misc"
          }
          with open(self.config_path, "w") as f:
              json.dump(config_data, f)
          
          cm = ConfigManager(self.config_path)
          self.assertEqual(cm.target_folders, [Path("C:/TestDownloads")])
          self.assertEqual(cm.categories, {"Docs": [".pdf"]})
          self.assertEqual(cm.default_category, "Misc")

      def test_load_missing_or_invalid_config_fallback(self):
          # No file created, should fallback to defaults
          cm = ConfigManager(self.config_path)
          self.assertTrue(len(cm.target_folders) >= 0)
          self.assertEqual(cm.default_category, "Others")
  ```

- [ ] **Step 2: Run the test to verify it fails**
  Run: `python -m unittest tests/test_config.py`
  Expected: Failure due to `src.config_manager` not existing.

- [ ] **Step 3: Implement `src/config_manager.py`**
  Create `src/config_manager.py` with fallback defaults.
  
  ```python
  import json
  import logging
  from pathlib import Path

  logger = logging.getLogger("TidyFile")

  DEFAULT_CONFIG = {
      "target_folders": [str(Path.home() / "Downloads")],
      "categories": {
          "Documents": [
              ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", 
              ".txt", ".rtf", ".odt", ".ods", ".odp", ".csv", ".md"
          ],
          "Images": [
              ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"
          ]
      },
      "default_category": "Others"
  }

  class ConfigManager:
      def __init__(self, config_path: Path):
          self.config_path = Path(config_path)
          self.target_folders = []
          self.categories = {}
          self.default_category = "Others"
          self.load_config()

      def load_config(self):
          if not self.config_path.exists():
              logger.warning(f"Config file {self.config_path} not found. Using defaults.")
              self._apply_dict(DEFAULT_CONFIG)
              return

          try:
              with open(self.config_path, "r") as f:
                  data = json.load(f)
              self._apply_dict(data)
          except json.JSONDecodeError as e:
              logger.error(f"Failed to read config.json: Format JSON rusak. Menggunakan konfigurasi default. Detail: {e}")
              self._apply_dict(DEFAULT_CONFIG)

      def _apply_dict(self, data: dict):
          self.target_folders = [Path(p) for p in data.get("target_folders", [])]
          self.categories = data.get("categories", {})
          self.default_category = data.get("default_category", "Others")
  ```

- [ ] **Step 4: Create empty `src/__init__.py` and `tests/__init__.py`**
  Ensure the directories are treated as python packages.

- [ ] **Step 5: Run tests to verify they pass**
  Run: `python -m unittest tests/test_config.py`
  Expected: PASS

- [ ] **Step 6: Commit**
  Run:
  ```bash
  git add src/__init__.py src/config_manager.py tests/__init__.py tests/test_config.py
  git commit -m "feat: implement config manager with fallback mechanisms"
  ```

---

### Task 3: Core Logic (Moving, Hashing, & Collision Handling)

**Files:**
- Create: `src/core.py`
- Create: `tests/test_core.py`

- [ ] **Step 1: Write failing tests for Core logic**
  Create `tests/test_core.py` to test file hashing, category resolution, version renaming, and duplicate deletion.
  
  ```python
  import unittest
  import tempfile
  import shutil
  from pathlib import Path
  from src.core import FileOrganizer
  from src.config_manager import ConfigManager

  class TestFileOrganizer(unittest.TestCase):
      def setUp(self):
          self.temp_dir = tempfile.TemporaryDirectory()
          self.root = Path(self.temp_dir.name)
          
          # Target directories setup
          self.src_dir = self.root / "Downloads"
          self.src_dir.mkdir()
          
          # Mock ConfigManager properties
          class MockConfig:
              target_folders = [self.src_dir]
              categories = {
                  "Documents": [".pdf"],
                  "Images": [".jpg"]
              }
              default_category = "Others"
              
          self.config = MockConfig()
          self.organizer = FileOrganizer(self.config)

      def tearDown(self):
          self.temp_dir.cleanup()

      def test_get_category(self):
          self.assertEqual(self.organizer.get_category(Path("test.pdf")), "Documents")
          self.assertEqual(self.organizer.get_category(Path("test.txt")), "Others")

      def test_hash_calculation(self):
          file1 = self.src_dir / "f1.txt"
          file1.write_text("Hello World")
          h1 = self.organizer.calculate_hash(file1)
          self.assertEqual(len(h1), 64)  # SHA-256 length

      def test_organize_simple_move(self):
          file = self.src_dir / "tugas.pdf"
          file.write_text("content")
          
          self.organizer.organize_folder(self.src_dir)
          
          dest = self.src_dir / "Documents" / "tugas.pdf"
          self.assertTrue(dest.exists())
          self.assertFalse(file.exists())

      def test_organize_duplicate_deletion(self):
          # Target file exists
          dest_dir = self.src_dir / "Documents"
          dest_dir.mkdir()
          dest_file = dest_dir / "tugas.pdf"
          dest_file.write_text("same content")
          
          # Source file (duplicate)
          src_file = self.src_dir / "tugas.pdf"
          src_file.write_text("same content")
          
          self.organizer.organize_folder(self.src_dir)
          
          self.assertTrue(dest_file.exists())
          self.assertFalse(src_file.exists())  # Duplicate deleted

      def test_organize_version_renaming(self):
          dest_dir = self.src_dir / "Documents"
          dest_dir.mkdir()
          dest_file = dest_dir / "tugas.pdf"
          dest_file.write_text("version 1")
          
          src_file = self.src_dir / "tugas.pdf"
          src_file.write_text("version 2")
          
          self.organizer.organize_folder(self.src_dir)
          
          self.assertTrue(dest_file.exists())
          self.assertFalse(src_file.exists())
          
          renamed_file = dest_dir / "tugas_1.pdf"
          self.assertTrue(renamed_file.exists())
          self.assertEqual(renamed_file.read_text(), "version 2")
  ```

- [ ] **Step 2: Run tests to verify they fail**
  Run: `python -m unittest tests/test_core.py`
  Expected: Failures due to missing `src/core.py`.

- [ ] **Step 3: Implement `src/core.py`**
  Implement the file hash calculations, file categorization, duplicate detection, version renaming, and directory movement.
  
  ```python
  import hashlib
  import shutil
  import logging
  from pathlib import Path

  logger = logging.getLogger("TidyFile")

  class FileOrganizer:
      def __init__(self, config):
          self.config = config

      def calculate_hash(self, file_path: Path) -> str:
          sha256 = hashlib.sha256()
          try:
              with open(file_path, "rb") as f:
                  while chunk := f.read(8192):
                      sha256.update(chunk)
              return sha256.hexdigest()
          except Exception as e:
              logger.error(f"Gagal menghitung hash file {file_path.name}: {e}")
              return ""

      def get_category(self, file_path: Path) -> str:
          suffix = file_path.suffix.lower()
          for category, extensions in self.config.categories.items():
              if suffix in extensions:
                  return category
          return self.config.default_category

      def get_unique_path(self, dest_folder: Path, file_name: Path) -> Path:
          base_name = file_name.stem
          ext = file_name.suffix
          counter = 1
          target_path = dest_folder / file_name.name
          while target_path.exists():
              target_path = dest_folder / f"{base_name}_{counter}{ext}"
              counter += 1
          return target_path

      def process_file(self, file_path: Path):
          # Ignore folders and temp files
          if file_path.is_dir():
              return
          
          # Ignore browser downloading files
          if file_path.suffix.lower() in [".crdownload", ".part", ".tmp"]:
              return

          category = self.get_category(file_path)
          dest_folder = file_path.parent / category
          dest_folder.mkdir(exist_ok=True)
          
          target_path = dest_folder / file_path.name

          # Collision Handling
          if target_path.exists():
              src_hash = self.calculate_hash(file_path)
              target_hash = self.calculate_hash(target_path)
              
              if src_hash and src_hash == target_hash:
                  try:
                      file_path.unlink()
                      logger.warning(f"Duplikat Terdeteksi (Isi Identik): \"{file_path.name}\" sama dengan \"{target_path}\". Menghapus duplikat di root.")
                      return
                  except PermissionError:
                      logger.warning(f"Gagal menghapus duplikat \"{file_path.name}\": File sedang dibuka oleh program lain.")
                      return

              # Hash differs -> rename
              target_path = self.get_unique_path(dest_folder, file_path)
              logger.info(f"Konflik Nama Terdeteksi (Isi Berbeda): \"{file_path.name}\" memiliki versi berbeda di tujuan. Memindahkan sebagai \"{target_path.name}\".")

          # Move file
          try:
              shutil.move(str(file_path), str(target_path))
              logger.info(f"Dipindahkan: \"{file_path.name}\" -> \"{target_path}\"")
          except PermissionError:
              logger.warning(f"Gagal memindahkan \"{file_path.name}\": File sedang dibuka oleh program lain atau sedang di-download.")
          except Exception as e:
              logger.error(f"Gagal memproses file \"{file_path.name}\": {e}")

      def organize_folder(self, folder_path: Path):
          if not folder_path.exists():
              logger.error(f"Folder target \"{folder_path}\" tidak ditemukan.")
              return

          logger.info(f"Memulai pemindaian folder target: {folder_path}...")
          
          # Only scan files at root level (do not recurse into category subfolders)
          files = [p for p in folder_path.iterdir() if p.is_file()]
          if not files:
              logger.info(f"Folder \"{folder_path.name}\" sudah bersih. Tidak ada file untuk dirapikan.")
              return

          for file_path in files:
              self.process_file(file_path)
          logger.info(f"Pemindaian folder \"{folder_path.name}\" selesai.")
  ```

- [ ] **Step 4: Run tests to verify they pass**
  Run: `python -m unittest tests/test_core.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run:
  ```bash
  git add src/core.py tests/test_core.py
  git commit -m "feat: implement core file moving and collision logic"
  ```

---

### Task 4: Main CLI & Logging Setup

**Files:**
- Create: `src/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write tests for Main CLI**
  Create `tests/test_main.py` to test argument parsing options.
  
  ```python
  import unittest
  import sys
  from unittest.mock import patch
  from src.main import parse_args

  class TestMainCLI(unittest.TestCase):
      def test_parse_args_default(self):
          with patch.object(sys, 'argv', ['main.py']):
              args = parse_args()
              self.assertFalse(args.watch)

      def test_parse_args_watch(self):
          with patch.object(sys, 'argv', ['main.py', '--watch']):
              args = parse_args()
              self.assertTrue(args.watch)
  ```

- [ ] **Step 2: Run tests to verify they fail**
  Run: `python -m unittest tests/test_main.py`
  Expected: Failures due to missing `src/main.py`.

- [ ] **Step 3: Implement `src/main.py`**
  Build argument parser, setup double logging outputs (stdout and `tidyfile.log`), and tie core processes together.
  
  ```python
  import argparse
  import logging
  import sys
  from pathlib import Path
  from src.config_manager import ConfigManager
  from src.core import FileOrganizer

  def setup_logging():
      logger = logging.getLogger("TidyFile")
      logger.setLevel(logging.INFO)
      
      # Clear existing handlers
      logger.handlers = []

      # Formatter
      formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

      # File Handler (logs to project root directory)
      file_handler = logging.FileHandler("tidyfile.log", encoding="utf-8")
      file_handler.setFormatter(formatter)
      file_handler.setLevel(logging.INFO)

      # Stream Handler
      stream_handler = logging.StreamHandler(sys.stdout)
      stream_handler.setFormatter(formatter)
      stream_handler.setLevel(logging.INFO)

      logger.addHandler(file_handler)
      logger.addHandler(stream_handler)
      return logger

  def parse_args():
      parser = argparse.ArgumentParser(description="TidyFile: Central file organization utility.")
      parser.add_argument("--watch", action="store_true", help="Menjalankan monitoring real-time di background.")
      return parser.parse_args()

  def main():
      logger = setup_logging()
      args = parse_args()

      config_path = Path("config.json")
      config = ConfigManager(config_path)
      organizer = FileOrganizer(config)

      if args.watch:
          logger.info("Memulai TidyFile dalam mode Watchdog (Real-time monitoring)...")
          from src.watcher import start_watcher
          start_watcher(config, organizer)
      else:
          logger.info("Memulai TidyFile dalam mode Sekali Jalan (One-off)...")
          for folder in config.target_folders:
              organizer.organize_folder(folder)
          logger.info("TidyFile selesai merapikan file.")

  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 4: Run tests to verify they pass**
  Run: `python -m unittest tests/test_main.py`
  Expected: PASS

- [ ] **Step 5: Run all tests**
  Run: `python -m unittest discover tests`
  Expected: All tests pass.

- [ ] **Step 6: Commit**
  Run:
  ```bash
  git add src/main.py tests/test_main.py
  git commit -m "feat: implement CLI entry point and double logger"
  ```

---

### Task 5: Watchdog Background Monitor

**Files:**
- Create: `src/watcher.py`

- [ ] **Step 1: Implement `src/watcher.py`**
  Uses the `watchdog` library to monitor folder creation and modifications, and handles Chrome/Firefox download events.
  
  ```python
  import time
  import logging
  from pathlib import Path
  from watchdog.observers import Observer
  from watchdog.events import FileSystemEventHandler

  logger = logging.getLogger("TidyFile")

  class FolderHandler(FileSystemEventHandler):
      def __init__(self, organizer):
          self.organizer = organizer

      def on_created(self, event):
          if not event.is_directory:
              self.process_with_cooldown(Path(event.src_path))

      def on_moved(self, event):
          # Browser downloads rename the file when complete
          if not event.is_directory:
              self.process_with_cooldown(Path(event.dest_path))

      def process_with_cooldown(self, file_path: Path):
          # Ignore browser temp extensions
          if file_path.suffix.lower() in [".crdownload", ".part", ".tmp"]:
              return

          # Short cooldown to allow browser to release the file lock
          time.sleep(1.5)
          logger.info(f"Mendeteksi file baru: {file_path.name}. Memproses...")
          self.organizer.process_file(file_path)

  def start_watcher(config, organizer):
      observer = Observer()
      handler = FolderHandler(organizer)

      watched_folders = 0
      for folder in config.target_folders:
          if folder.exists():
              observer.schedule(handler, path=str(folder), recursive=False)
              logger.info(f"Memantau folder: {folder}")
              watched_folders += 1
          else:
              logger.error(f"Gagal memantau folder: {folder} (Folder tidak ditemukan)")

      if watched_folders == 0:
          logger.error("Tidak ada folder valid yang dapat dipantau. Watchdog dimatikan.")
          return

      observer.start()
      try:
          while True:
              time.sleep(1)
      except KeyboardInterrupt:
          logger.info("Menghentikan pemantauan watchdog...")
          observer.stop()
      observer.join()
  ```

- [ ] **Step 2: Commit**
  Run:
  ```bash
  git add src/watcher.py
  git commit -m "feat: implement background watcher using watchdog library"
  ```

---

### Task 6: Helper Scripts for Automation

**Files:**
- Create: `scripts/run_once.bat`
- Create: `scripts/run_watcher.vbs`

- [ ] **Step 1: Create `scripts/run_once.bat`**
  Build the batch file that can be run from anywhere, shifting context to the project directory and running Python.
  
  ```bat
  @echo off
  cd /d "D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile"
  ".venv\Scripts\python.exe" -m src.main
  pause
  ```

- [ ] **Step 2: Create `scripts/run_watcher.vbs`**
  Build a VBScript file that runs the watchdog silently in the background (no visible command prompt).
  
  ```vbs
  Set WshShell = CreateObject("WScript.Shell")
  WshShell.Run "cmd.exe /c cd /d D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile && .venv\Scripts\python.exe -m src.main --watch", 0, False
  Set WshShell = Nothing
  ```

- [ ] **Step 3: Commit**
  Run:
  ```bash
  git add scripts/run_once.bat scripts/run_watcher.vbs
  git commit -m "chore: add windows helper batch and silent VBS scripts"
  ```

---

### Task 7: Guide Files, Readme & Local Setup

**Files:**
- Create: `LOCAL_GUIDE.md`
- Create: `README.md`

- [ ] **Step 1: Create local `LOCAL_GUIDE.md`**
  Create local guides containing activation steps, package installations, and task scheduler configs. Since this is ignored in `.gitignore`, it stays strictly local.
  
  ```markdown
  # Panduan Lokal TidyFile

  Panduan ini membantu kamu mengatur dan menjalankan TidyFile di komputermu sendiri.

  ## 1. Setup Virtual Environment (venv)
  
  Buka PowerShell di folder project:
  ```powershell
  # Buat virtual environment
  python -m venv .venv

  # Aktivasi venv
  .venv\Scripts\Activate.ps1

  # Install dependencies
  pip install -r requirements.txt
  ```

  ## 2. Setup Konfigurasi
  Salin file `config.json.example` menjadi `config.json`, lalu sesuaikan folder target yang ingin kamu bersihkan:
  ```json
  {
    "target_folders": [
      "C:/Users/HP/Downloads",
      "C:/Users/HP/Desktop"
    ]
  }
  ```

  ## 3. Eksekusi
  * **Sekali Jalan (One-off):** Double-click file `scripts/run_once.bat` atau jalankan:
    ```powershell
    python -m src.main
    ```
  * **Real-time Monitoring (Background):** Double-click file `scripts/run_watcher.vbs` untuk menjalankannya diam-diam di background, atau jalankan:
    ```powershell
    python -m src.main --watch
    ```

  ## 4. Setup Otomatisasi Windows Task Scheduler (Set & Forget)
  1. Buka **Task Scheduler** di Windows.
  2. Klik **Create Basic Task**.
  3. Beri nama: `TidyFile Cleanup`.
  4. Atur Trigger: `Daily` (misal jam 16:00) atau `When I log on`.
  5. Action: `Start a program`.
  6. Program/script: `D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile\scripts\run_once.bat`.
  7. Klik **Finish**.
  ```

- [ ] **Step 2: Create public `README.md`**
  Provide professional README documentation for GitHub.
  
  ```markdown
  # TidyFile Central Organizer

  TidyFile is a modular, automated Python utility designed to automatically organize messy directories (such as `Downloads` or `Desktop`) into categorized subfolders based on file extensions.

  ## Features
  - **Modular Architecture:** Structured package for configuration management, file routing, and background services.
  - **Hash-based Collision Handling:** Computes file hashes (SHA-256) to safely delete duplicate downloads and prevent data loss.
  - **Version Renaming:** Auto-renames files with incremental counter suffixes if versions differ but names match.
  - **Dual Modes:** 
    - *One-off cleaning:* Perfect for Windows Task Scheduler.
    - *Real-time monitoring:* Watchdog-based daemon that reacts to file creations and finished browser downloads.
  - **Robust Error Handling:** Cooldown timers for unfinished browser downloads and locks for open application files.

  ## Setup Template
  Rename `config.json.example` to `config.json` to define your target folders and category-extension mapping.
  
  ## License
  MIT
  ```

- [ ] **Step 3: Commit**
  Run:
  ```bash
  git add README.md
  git commit -m "docs: add README.md for github repository"
  ```
  *(Note: LOCAL_GUIDE.md is ignored by git, so we do not add it).*
