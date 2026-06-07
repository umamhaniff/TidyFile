# Portable Batch Script Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a portable batch script (`tidy_here.bat`) that can be placed in any directory to organize that directory, and add a `--path` CLI option to override config settings.

**Architecture:** Extend the Python parser with `--path`, pass it to `FileOrganizer.organize_folder()`, add `tidy_here.bat` to the file exclusion rules, create the `tidy_here.bat` script using `%~dp0` to capture the current directory, and update documentation.

**Tech Stack:** Python 3.x (`pathlib`, `argparse`), Windows Batch Script.

---

### Task 1: CLI Argument Parsing and Main Flow
Update the CLI parser and main runner to accept and handle a `--path` argument.

**Files:**
- Modify: `src/main.py`
- Test: `tests/test_main.py`

- [ ] **Step 1: Write test for the new argument**
  Modify `tests/test_main.py` to assert that `--path` argument is parsed correctly.
  
  ```python
  def test_parse_args_path(self):
      with patch.object(sys, 'argv', ['main.py', '--path', 'C:\\some\\dir']):
          args = parse_args()
          self.assertEqual(args.path, 'C:\\some\\dir')
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `python -m unittest tests/test_main.py`
  Expected: FAIL (AttributeError: 'Namespace' object has no attribute 'path' or similar)

- [ ] **Step 3: Update `src/main.py` to parse `--path`**
  Modify `parse_args` to include `--path` argument:
  ```python
  def parse_args():
      parser = argparse.ArgumentParser(description="TidyFile: Central file organization utility.")
      parser.add_argument("--watch", action="store_true", help="Menjalankan monitoring real-time di background.")
      parser.add_argument("--path", type=str, help="Path folder spesifik yang ingin dirapikan (mengabaikan target_folders di config.json).")
      return parser.parse_args()
  ```

- [ ] **Step 4: Run test to verify it passes**
  Run: `python -m unittest tests/test_main.py`
  Expected: PASS

- [ ] **Step 5: Modify main execution flow to use `--path`**
  Modify `main()` in `src/main.py` so that if `args.path` is provided, it organizes only that folder:
  ```python
      if args.watch:
          logger.info("Memulai TidyFile dalam mode Watchdog (Real-time monitoring)...")
          from src.watcher import start_watcher
          start_watcher(config, organizer)
      else:
          logger.info("Memulai TidyFile dalam mode Sekali Jalan (One-off)...")
          if args.path:
              specific_path = Path(args.path).resolve()
              logger.info(f"Target spesifik dari argumen --path: {specific_path}")
              organizer.organize_folder(specific_path)
          else:
              for folder in config.target_folders:
                  organizer.organize_folder(folder)
          logger.info("TidyFile selesai merapikan file.")
  ```

- [ ] **Step 6: Commit**
  ```bash
  git add src/main.py tests/test_main.py
  git commit -m "feat: add --path option to CLI and main runner"
  ```

---

### Task 2: File Exclusion and Unit Test
Add `tidy_here.bat` to the organizer ignore list and update tests to verify it is ignored.

**Files:**
- Modify: `src/core.py`
- Modify: `tests/test_core.py`

- [ ] **Step 1: Write test for ignoring `tidy_here.bat`**
  Modify `tests/test_core.py` inside `test_organize_ignores_tidyfile_scripts` to check that `tidy_here.bat` is ignored.
  
  ```python
      def test_organize_ignores_tidyfile_scripts(self):
          # Create TidyFile scripts in source dir
          script_file = self.src_dir / "run_once.bat"
          script_file.write_text("echo run once")
          
          tidy_here_file = self.src_dir / "tidy_here.bat"
          tidy_here_file.write_text("echo tidy here")
          
          config_file = self.src_dir / "config.json"
          config_file.write_text("{}")
          
          self.organizer.organize_folder(self.src_dir)
          
          # They should NOT be moved
          self.assertTrue(script_file.exists())
          self.assertTrue(tidy_here_file.exists())
          self.assertTrue(config_file.exists())
          
          # Verify no "Code_and_Projects" or "Others" subdirectories were created
          self.assertFalse((self.src_dir / "Code_and_Projects").exists())
          self.assertFalse((self.src_dir / "Others").exists())
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `python -m unittest tests/test_core.py`
  Expected: FAIL (as `tidy_here.bat` gets moved because it is not in the ignore list yet)

- [ ] **Step 3: Modify `src/core.py` to add `tidy_here.bat` to the ignore list**
  Modify `src/core.py` ignore check:
  ```python
          # Ignore TidyFile project files if they are located in the target directory
          if file_path.name.lower() in [
              "run_once.bat", 
              "run_watcher.vbs", 
              "tidy_here.bat",
              "config.json", 
              "config.json.example", 
              "tidyfile.log",
              "local_guide.md", 
              "readme.md", 
              "gemini.md"
          ]:
              return
  ```

- [ ] **Step 4: Run tests to verify they pass**
  Run: `python -m unittest tests/test_core.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add src/core.py tests/test_core.py
  git commit -m "feat: ignore tidy_here.bat in organizer and update tests"
  ```

---

### Task 3: Create `tidy_here.bat` script
Create the new portable batch script at the project root.

**Files:**
- Create: `tidy_here.bat`

- [ ] **Step 1: Create `tidy_here.bat`**
  Create `tidy_here.bat` at the project root directory with the following content:
  ```bat
  @echo off
  :: TidyFile - Script untuk merapikan folder tempat file .bat ini diletakkan.
  :: Salin file ini ke folder mana saja, lalu klik dua kali untuk merapikannya!
  
  set "TARGET_DIR=%~dp0"
  cd /d "<TidyFile_Directory>"
  ".venv\Scripts\python.exe" -m src.main --path "%TARGET_DIR%"
  pause
  ```

- [ ] **Step 2: Commit**
  ```bash
  git add tidy_here.bat
  git commit -m "feat: create portable tidy_here.bat script"
  ```

---

### Task 4: Documentation Updates
Update documentation files to instruct the user on how to use `tidy_here.bat`.

**Files:**
- Modify: `README.md`
- Modify: `LOCAL_GUIDE.md`

- [ ] **Step 1: Update `README.md`**
  Modify the section under "Mode A: Eksekusi Sekali Jalan (One-Off)" to detail both `run_once.bat` (central organization) and `tidy_here.bat` (portable folder organization).
  
- [ ] **Step 2: Update `LOCAL_GUIDE.md`**
  Add details explaining that `tidy_here.bat` is portable and can be copied anywhere.

- [ ] **Step 3: Run all project unit tests**
  Run: `python -m unittest discover tests`
  Expected: All tests pass.

- [ ] **Step 4: Commit**
  ```bash
  git add README.md LOCAL_GUIDE.md
  git commit -m "docs: document tidy_here.bat in README and LOCAL_GUIDE"
  ```
