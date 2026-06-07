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
