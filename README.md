# 🧹 TidyFile Central Organizer

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Dependencies](https://img.shields.io/badge/dependencies-watchdog-orange.svg)](https://github.com/gorakhargosh/watchdog)
[![Tests Status](https://img.shields.io/badge/tests-17%20passing-brightgreen.svg)](#-testing)

**TidyFile** adalah utilitas otomatisasi berbasis Python yang dirancang untuk merapikan direktori berantakan (seperti `Downloads`, `Desktop`, dll.) secara terpusat. Program ini memilah file ke dalam subfolder kategori terstruktur (seperti *Documents*, *Images*, *Code*, dsb.) berdasarkan ekstensi file secara cerdas dan aman.

---

## ✨ Fitur Utama

- 📦 **Arsitektur Modular & Bersih:** Pembagian tanggung jawab kode yang rapi (konfigurasi, logika inti, pemantauan, dan otomasi).
- 🛡️ **Anti-Collision & Proteksi Duplikat (SHA-256):** Menghitung sidik jari digital (Hash) untuk menghapus file unduhan duplikat secara aman dan mencegah penimpaan file secara tidak sengaja.
- 🔄 **Re-versioning Otomatis:** Mengubah nama file dengan indeks angka (misal: `laporan_1.pdf`) secara dinamis apabila namanya sama tetapi isinya berbeda.
- ⏱️ **Deteksi Cooldown Browser:** Menunda pemrosesan file sementara unduhan browser (seperti `.crdownload` atau `.part`) hingga unduhan selesai 100% untuk mencegah korupsi data.
- ⚙️ **Dua Mode Eksekusi:**
  - **One-off Mode:** Pemindaian sekali jalan yang cocok dipadukan dengan *Windows Task Scheduler*.
  - **Background Watchdog Mode:** Pemantauan real-time di latar belakang menggunakan Windows File System API dengan konsumsi resource yang sangat rendah.
- 🔕 **Silent Execution:** Didukung script VBScript agar pemantauan background berjalan tanpa memunculkan jendela hitam CMD yang mengganggu.

---

## 📂 Struktur Direktori Project

```text
TidyFile/
├── src/
│   ├── __init__.py          # Penanda paket python
│   ├── main.py              # Entrypoint CLI & inisialisasi logger
│   ├── config_manager.py    # Handler pemuatan file konfigurasi & fallback
│   ├── core.py              # Logika utama (pemindahan, hashing, anti-collision)
│   └── watcher.py           # Pemantau real-time (Watchdog daemon)
├── tests/
│   ├── __init__.py
│   ├── test_config.py       # Unit test untuk konfigurasi
│   ├── test_core.py         # Unit test untuk logika pemindahan & hash
│   ├── test_main.py         # Unit test untuk CLI argument parsing
│   └── test_watcher.py      # Unit test untuk event watcher
├── scripts/
│   ├── run_once.bat         # Batch file eksekusi sekali jalan (portable)
│   └── run_watcher.vbs      # VBScript eksekusi watchdog secara silent
├── config.json.example      # Template konfigurasi kategori & ekstensi
├── README.md                # Dokumentasi utama GitHub
└── gemini.md                # Konteks persistent memori kecerdasan AI
```

---

## 🚀 Memulai (Quick Start)

### 1. Prasyarat
Pastikan komputer kamu sudah terinstall **Python 3.x**.

### 2. Setup Virtual Environment & Install Dependensi
Buka Terminal/PowerShell di direktori project, lalu jalankan perintah berikut:
```powershell
# Buat virtual environment
python -m venv .venv

# Aktivasi virtual environment
.venv\Scripts\Activate.ps1

# Install pustaka watchdog
pip install -r requirements.txt
```

### 3. Setup Konfigurasi Kategori
Salin file `config.json.example` menjadi `config.json` pada root direktori project:
```json
{
  "target_folders": [
    "D:/Downloads"
  ],
  "categories": {
    "Documents": [".pdf", ".docx", ".xlsx", ".csv", ".md"],
    "Images": [".png", ".jpg", ".jpeg", ".webp", ".heic"]
  },
  "default_category": "Others"
}
```
*Catatan: Kamu bisa mendaftarkan beberapa folder sekaligus pada `"target_folders"`.*

---

## 💻 Cara Penggunaan

### Mode A: Eksekusi Sekali Jalan (One-Off)
Digunakan untuk merapikan folder target saat ini juga kemudian program langsung berhenti.
- **Melalui Python:**
  ```powershell
  python -m src.main
  ```
- **Melalui Shortcut Windows:**
  Double-click file `scripts/run_once.bat`. Kamu bisa memindahkan atau menduplikat file `.bat` ini ke Desktop untuk kemudahan akses.

### Mode B: Eksekusi Real-time (Background Watchdog)
Program akan standby di latar belakang dan merapikan file secara instan begitu ada file baru masuk ke folder target.
- **Melalui Python:**
  ```powershell
  python -m src.main --watch
  ```
- **Melalui Silent Execution (Tanpa Window CMD):**
  Double-click file `scripts/run_watcher.vbs`. Program akan langsung berjalan di background secara tersembunyi.

---

## 🕒 Windows Task Scheduler Setup (Set & Forget)

Agar folder kamu dirapikan secara otomatis (misal: setiap hari jam 4 sore):
1. Buka **Task Scheduler** di Windows.
2. Klik **Create Basic Task** pada panel kanan.
3. Beri nama tugas: `TidyFile Auto Organizer`.
4. Pilih Trigger: `Daily` (setiap hari) atau `When I log on` (setiap laptop dinyalakan).
5. Pada bagian Action, pilih `Start a program`.
6. Di kolom **Program/script**, arahkan ke file `.bat` absolut kamu:
   `D:\_CampusLife\ProjectCampus\6ProjectPribadi\TidyFile\scripts\run_once.bat`
7. Klik **Finish**.

---

## 🧪 Testing

Project ini dilengkapi dengan unit test menyeluruh menggunakan modul `unittest` bawaan Python. Semua pengujian menggunakan folder tiruan sementara (`tempfile`), sehingga aman dijalankan kapan saja tanpa merusak file asli kamu.

Untuk menjalankan seluruh test suite:
```powershell
python -m unittest discover tests
```
