# Gemini Context Memory: TidyFile Project

## Flow & Concept
TidyFile Suite is a modular Python command-line utility and background service providing 3 specialized organization modes:
1. **Tidy File (Core):** Cleans and categorizes files based on file extensions (Documents, Images, Code, etc.).
2. **Tidy Workstation:** Organizes work/document files by metadata date into flat folder `Workstation-YYYY-MM-DD/`.
3. **Tidy Moment:** Organizes photos and videos across formats and devices by EXIF/Video/Filename/Filesystem date into flat folder `Moment-YYYY-MM-DD/`.

### Date Parsing Hierarchy (MetadataParser)
1. **Tier 1 (Embedded Metadata):** Image EXIF (`Pillow`/`pillow-heif`), Video/Audio container atoms (`tinytag`), and universal fallback (`hachoir`).
2. **Tier 2 (Filename Regex):** WhatsApp patterns (`IMG-YYYYMMDD-WA...`), Camera/Screenshot patterns (`IMG_YYYYMMDD_...`, `Screenshot_YYYY-MM-DD...`), ISO patterns (`YYYY-MM-DD`, `YYYYMMDD`).
3. **Tier 3 (Filesystem Fallback):** Modified/Creation timestamps (`os.path.getmtime`).

### Tech Stack
* **Language:** Python 3.x
* **Core Libraries:** `pathlib`, `shutil`, `hashlib`, `logging`, `unittest`, `re`, `datetime`
* **Third-party Libraries:** `watchdog`, `pillow`, `pillow-heif`, `tinytag`, `hachoir`
* **Automation Tools:** Windows Task Scheduler, VBScript wrapper, Interactive Batch Menu (`tidy_here.bat`)

---

## Workspace Layout
* [docs/superpowers/specs/2026-06-07-tidyfile-design.md](docs/superpowers/specs/2026-06-07-tidyfile-design.md): Design Specification
* `src/`: Core Python modules (`metadata_parser.py`, `core.py`, `config_manager.py`, `watcher.py`, `main.py`)
* `tests/`: Testing suites (`test_config.py`, `test_core.py`, `test_metadata_parser.py`, `test_modes.py`, `test_main.py`, `test_watcher.py`)
* `scripts/`: Batch and VBS helper scripts
* `tidy_here.bat`: Interactive numbered menu (1-4) for portable one-click cleanup

---

## Git Rules & Ignore Files
* `.venv/`, `config.json`, `tidyfile.log`, and `LOCAL_GUIDE.md` must be ignored in `.gitignore`.
* `LOCAL_GUIDE.md` must remain strictly local and not be committed to Git.

---

## Specialized CLI & UV Commands
* **Install / Sync Dependencies with UV:**
  ```powershell
  uv sync --all-extras
  ```
* **Run Tests with Coverage (via UV):**
  ```powershell
  uv run coverage run -m unittest discover -s tests
  uv run coverage report -m
  ```
* **Run Tidy File (CLI):**
  ```powershell
  uv run python -m src.main tidy [--path "D:/Target"]
  ```
* **Run Tidy Workstation:**
  ```powershell
  uv run python -m src.main workstation [--path "D:/Target"]
  ```
* **Run Tidy Moment:**
  ```powershell
  uv run python -m src.main moment [--path "D:/Target"]
  ```
* **Run Interactive Menu:**
  ```powershell
  uv run python -m src.main menu
  ```
* **Build Portable Single .EXE:**
  ```powershell
  .\build.bat
  # atau
  uv run pyinstaller --noconfirm --clean --onefile --name tidyfile src/main.py
  ```

