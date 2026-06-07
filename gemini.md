# Gemini Context Memory: TidyFile Project

## Flow & Concept
TidyFile is a modular Python command-line utility and background service to clean and organize files from messy directories (Downloads, Desktop, etc.) into categorized folders (Documents, Images, Code, etc.) based on file extensions.

### Tech Stack
* **Language:** Python 3.x
* **Core Libraries:** `pathlib`, `shutil`, `hashlib`, `logging`, `unittest`
* **Third-party Libraries:** `watchdog` (for background real-time folder monitoring)
* **Automation Tools:** Windows Task Scheduler, VBScript wrapper for silent execution

---

## Workspace Layout
* [docs/superpowers/specs/2026-06-07-tidyfile-design.md](docs/superpowers/specs/2026-06-07-tidyfile-design.md): Design Specification
* `src/`: Core Python modules
* `tests/`: Testing suites
* `scripts/`: Batch and VBS helper scripts

---

## Git Rules & Ignore Files
* `.venv/`, `config.json`, `tidyfile.log`, and `LOCAL_GUIDE.md` must be ignored in `.gitignore`.
* `LOCAL_GUIDE.md` must remain strictly local and not be committed to Git.

---

## Specialized CLI Commands
Here are the commands defined for this project:

* **Activate Virtual Environment:**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
* **Run Once (Cleanup Mode):**
  ```powershell
  python -m src.main
  ```
* **Run Watcher (Background Mode):**
  ```powershell
  python -m src.main --watch
  ```
* **Run Tests:**
  ```powershell
  python -m unittest tests/test_core.py
  ```
