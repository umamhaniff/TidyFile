import hashlib
import shutil
import logging
from pathlib import Path
from src.metadata_parser import MetadataParser

logger = logging.getLogger("TidyFile")

IGNORED_FILENAMES = {
    "run_once.bat", 
    "run_watcher.vbs", 
    "tidy_here.bat",
    "setup.bat",
    "build.bat",
    "tidyfile.exe",
    "config.json", 
    "config.json.example", 
    "tidyfile.log",
    "local_guide.md", 
    "readme.md", 
    "gemini.md",
    "requirements.txt",
    "pyproject.toml",
    "uv.lock",
    "tidyfile.spec",
    ".gitignore",
    "typing.md"
}

IGNORED_EXTENSIONS = {".crdownload", ".part", ".tmp"}


class BaseOrganizer:
    """Base class untuk pengorganisasian file dengan collision & duplicate handling."""

    def __init__(self, config=None):
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

    def get_unique_path(self, dest_folder: Path, file_name: Path) -> Path:
        base_name = file_name.stem
        ext = file_name.suffix
        counter = 1
        target_path = dest_folder / file_name.name
        while target_path.exists():
            target_path = dest_folder / f"{base_name}_{counter}{ext}"
            counter += 1
        return target_path

    def should_ignore(self, file_path: Path) -> bool:
        if file_path.is_dir():
            return True
        if file_path.suffix.lower() in IGNORED_EXTENSIONS:
            return True
        if file_path.name.lower() in IGNORED_FILENAMES:
            return True
        return False

    def get_destination_folder(self, file_path: Path) -> Path:
        """Override di kelas turunan untuk menentukan folder tujuan."""
        raise NotImplementedError

    def process_file(self, file_path: Path):
        if self.should_ignore(file_path):
            return

        dest_folder = self.get_destination_folder(file_path)
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        target_path = dest_folder / file_path.name

        # Cek jika file sudah berada di folder tujuannya sendiri
        if file_path.resolve() == target_path.resolve():
            return

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
        if not folder_path.is_dir():
            logger.error(f"Folder target \"{folder_path}\" bukan merupakan direktori.")
            return

        logger.info(f"Memulai pemindaian folder target [{self.__class__.__name__}]: {folder_path}...")
        
        # Only scan files at root level (do not recurse into subfolders automatically)
        files = [p for p in folder_path.iterdir() if p.is_file()]
        if not files:
            logger.info(f"Folder \"{folder_path.name}\" sudah bersih. Tidak ada file untuk dirapikan.")
            return

        for file_path in files:
            self.process_file(file_path)
        logger.info(f"Pemindaian folder \"{folder_path.name}\" selesai.")


class FileOrganizer(BaseOrganizer):
    """Mode 1: Tidy File - Merapikan berdasarkan Kategori & Ekstensi."""

    def get_category(self, file_path: Path) -> str:
        if not self.config:
            return "Others"
        suffix = file_path.suffix.lower()
        for category, extensions in self.config.categories.items():
            if suffix in extensions:
                return category
        return self.config.default_category

    def get_destination_folder(self, file_path: Path) -> Path:
        category = self.get_category(file_path)
        return file_path.parent / category


class WorkstationOrganizer(BaseOrganizer):
    """Mode 2: Tidy Workstation - Merapikan dokumen kerja ke Workstation/YYYY/MM/DD/."""

    def get_destination_folder(self, file_path: Path) -> Path:
        year, month, day = MetadataParser.extract_date(file_path)
        return file_path.parent / "Workstation" / year / month / day


class MomentOrganizer(BaseOrganizer):
    """Mode 3: Tidy Moment - Merapikan foto & video ke Moment/YYYY/MM/DD/."""

    def get_destination_folder(self, file_path: Path) -> Path:
        year, month, day = MetadataParser.extract_date(file_path)
        return file_path.parent / "Moment" / year / month / day
