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

        # Ignore TidyFile project files if they are located in the target directory
        if file_path.name.lower() in [
            "run_once.bat", 
            "run_watcher.vbs", 
            "config.json", 
            "config.json.example", 
            "tidyfile.log",
            "local_guide.md", 
            "readme.md", 
            "gemini.md"
        ]:
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
