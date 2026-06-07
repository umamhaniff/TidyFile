import argparse
import logging
import sys
from pathlib import Path
from src import __version__
from src.config_manager import ConfigManager
from src.core import FileOrganizer

def setup_logging():
    logger = logging.getLogger("TidyFile")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers = []

    # Formatter
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # File Handler (logs to project root directory)
    file_handler = logging.FileHandler("tidyfile.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

def parse_args():
    parser = argparse.ArgumentParser(description="TidyFile: Central file organization utility.")
    parser.add_argument("--watch", action="store_true", help="Menjalankan monitoring real-time di background.")
    parser.add_argument("--path", type=str, help="Path folder spesifik yang ingin dirapikan (mengabaikan target_folders di config.json).")
    parser.add_argument("-v", "--version", action="version", version=f"TidyFile v{__version__}")
    return parser.parse_args()


def main():
    logger = setup_logging()
    args = parse_args()

    config_path = Path("config.json")
    config = ConfigManager(config_path)
    organizer = FileOrganizer(config)

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

    return 0

if __name__ == "__main__":
    main()
