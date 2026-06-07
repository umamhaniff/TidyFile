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
