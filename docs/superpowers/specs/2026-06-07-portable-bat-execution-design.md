# Spec: Portable Batch Script Execution

## Flow & Concept
The user wants a portable `.bat` file (let's name it `tidy_here.bat`) that can be copied to any directory. When double-clicked, it will run the TidyFile organizer on that specific directory.

To achieve this:
1. We will add a `--path` option to the Python CLI parser in `src/main.py`.
2. When `--path` is supplied, it overrides the `target_folders` in `config.json` and runs the organizer exclusively on that directory.
3. We will create `tidy_here.bat` at the project root. This script captures its own directory path (`%~dp0`), changes working directory to the TidyFile project directory, and runs the virtualenv python passing `--path "%TARGET_DIR%"`.
4. We will modify `src/core.py` to ensure that `tidy_here.bat` is ignored during organization so it doesn't get moved into a category folder.
5. We will update `README.md` and `LOCAL_GUIDE.md` to document the `.bat` file and how to use it.

---

## Technical Details

### 1. CLI Arguments in [src/main.py](file:///D:/_CampusLife/ProjectCampus/6ProjectPribadi/TidyFile/src/main.py)
* Add parser argument `--path`:
  ```python
  parser.add_argument("--path", type=str, help="Path folder spesifik yang ingin dirapikan (mengabaikan target_folders di config.json).")
  ```
* In `main()`, check if `args.path` is provided:
  ```python
  if args.path:
      specific_path = Path(args.path).resolve()
      logger.info(f"Target spesifik dari argumen --path: {specific_path}")
      organizer.organize_folder(specific_path)
  else:
      for folder in config.target_folders:
          organizer.organize_folder(folder)
  ```

### 2. File Exclusion in [src/core.py](file:///D:/_CampusLife/ProjectCampus/6ProjectPribadi/TidyFile/src/core.py)
* Update the ignore list to include `"tidy_here.bat"`:
  ```python
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

### 3. Portable Script [tidy_here.bat](file:///D:/_CampusLife/ProjectCampus/6ProjectPribadi/TidyFile/tidy_here.bat)
* Create this file at the project root:
  ```bat
  @echo off
  :: TidyFile - Script untuk merapikan folder tempat file .bat ini diletakkan.
  :: Salin file ini ke folder mana saja, lalu klik dua kali untuk merapikannya!
  
  set "TARGET_DIR=%~dp0"
  cd /d "D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile"
  ".venv\Scripts\python.exe" -m src.main --path "%TARGET_DIR%"
  pause
  ```

---

## Verification Plan

### Manual Verification
1. Run `python -m src.main --path <temp_test_dir>` on a temp folder and verify that only that folder is cleaned.
2. Copy `tidy_here.bat` into a temp folder containing dummy files (e.g. `test.pdf`, `test.jpg`).
3. Run `tidy_here.bat` by double-clicking (or calling from CMD).
4. Verify:
   - Dummy files are moved into `Documents/` and `Images/` inside that folder.
   - `tidy_here.bat` remains untouched in the root of that folder.
