# Portable Paths and Versioning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove hardcoded personal paths from all batch, VBS, and documentation files, automate the setup workflow via a new `setup.bat` file, introduce semantic versioning CLI options, and clean up the git configuration/tags.

**Architecture:** Use Windows batch relative directory resolution (`%~dp0`), VBS script directory parsing via `Scripting.FileSystemObject`, user-level environment variables (`TIDYFILE_DIR`), and standard Python package versioning attributes (`__version__`).

**Tech Stack:** Batch (CMD/BAT), VBScript, Python 3.x, Git

---

### Task 1: Package Initialization & CLI Version Option
Add the `__version__` property to the Python package and support `-v`/`--version` in CLI.

**Files:**
- Modify: [src/__init__.py](../../../src/__init__.py)
- Modify: [src/main.py](../../../src/main.py)
- Modify: [tests/test_main.py](../../../tests/test_main.py)

- [ ] **Step 1: Define version in __init__.py**
  Add `__version__ = "1.0.0"` to [src/__init__.py](../../../src/__init__.py).

- [ ] **Step 2: Add version argument in main.py**
  Import `__version__` and add `-v`/`--version` argument to `parse_args()` in [src/main.py](../../../src/main.py).

- [ ] **Step 3: Add test case for version in test_main.py**
  Add `test_parse_args_version` in [tests/test_main.py](../../../tests/test_main.py) to check that `--version` triggers a clean SystemExit with code 0.

- [ ] **Step 4: Run tests**
  Run: `python -m unittest tests/test_main.py`
  Expected: All tests pass.

---

### Task 2: Create setup.bat and Update Core File Ignore List
Create a root-level script to set up virtual environments, install dependencies, and register the local project path dynamically.

**Files:**
- Create: [setup.bat](../../../setup.bat)
- Modify: [src/core.py](../../../src/core.py)

- [ ] **Step 1: Write setup.bat**
  Write the automated environment setup and path registration script to [setup.bat](../../../setup.bat).

- [ ] **Step 2: Add setup.bat to organizer ignore list**
  Modify [src/core.py](../../../src/core.py) to ignore `setup.bat` so it isn't categorized when run.

---

### Task 3: Make Scripts Portable
Modify batch and VBS scripts to resolve paths relative to their locations or environment variables.

**Files:**
- Modify: [scripts/run_once.bat](../../../scripts/run_once.bat)
- Modify: [scripts/run_watcher.vbs](../../../scripts/run_watcher.vbs)
- Modify: [tidy_here.bat](../../../tidy_here.bat)

- [ ] **Step 1: Update scripts/run_once.bat**
  Replace absolute path with `%~dp0..`.

- [ ] **Step 2: Update scripts/run_watcher.vbs**
  Use `Scripting.FileSystemObject` to compute the root folder relative to the script location.

- [ ] **Step 3: Update tidy_here.bat**
  Check `%TIDYFILE_DIR%` with local fallback to `%~dp0` if running from project root.

---

### Task 4: Clean Up Absolute Paths in Documentation and Memory Files
Replace absolute personal path strings with relative links or generic placeholders.

**Files:**
- Modify: [README.md](../../../README.md)
- Modify: [LOCAL_GUIDE.md](../../../LOCAL_GUIDE.md)
- Modify: [gemini.md](../../../gemini.md)
- Modify: [docs/superpowers/plans/2026-06-07-portable-bat-execution.md](../../../docs/superpowers/plans/2026-06-07-portable-bat-execution.md)
- Modify: [docs/superpowers/plans/2026-06-07-tidyfile-initial-setup.md](../../../docs/superpowers/plans/2026-06-07-tidyfile-initial-setup.md)
- Modify: [docs/superpowers/specs/2026-06-07-portable-bat-execution-design.md](../../../docs/superpowers/specs/2026-06-07-portable-bat-execution-design.md)

- [ ] **Step 1: Replace path references in README.md & LOCAL_GUIDE.md**
  Update documented examples to use `<PATH_TO_PROJECT>` or relative guidelines. Also, add the `v1.0.0` versioning/badge info.

- [ ] **Step 2: Remove absolute path references in gemini.md & design docs**
  Convert links to relative paths or standard markdown format.

---

### Task 5: Git Tagging & Verification
Verify all tests pass, run the organizer manually to ensure portability works, and create a Git tag for `v1.0.0`.

- [ ] **Step 1: Run all tests**
  Run: `python -m unittest discover tests`
  Expected: All tests pass.

- [ ] **Step 2: Create Git Tag**
  Run: `git tag -a v1.0.0 -m "Release version 1.0.0"`
