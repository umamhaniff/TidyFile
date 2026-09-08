import argparse
import logging
import sys
from pathlib import Path
from src import __version__
from src.config_manager import ConfigManager
from src.core import FileOrganizer, WorkstationOrganizer, MomentOrganizer

def setup_logging():
    logger = logging.getLogger("TidyFile")
    logger.setLevel(logging.INFO)
    
    # Close and clear existing handlers to avoid ResourceWarning
    for h in list(logger.handlers):
        h.close()
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

def get_organizer_by_mode(mode: str, config: ConfigManager):
    mode = mode.lower()
    if mode in ("2", "workstation"):
        return "workstation", WorkstationOrganizer(config)
    elif mode in ("3", "moment"):
        return "moment", MomentOrganizer(config)
    else:
        return "tidy", FileOrganizer(config)

def show_interactive_menu():
    print("\n" + "=" * 52)
    print("                  TIDYFILE SUITE")
    print("=" * 52)
    print(" [1] Tidy File        (Organize by Category & Extension)")
    print(" [2] Tidy Workstation (Work Files -> Workstation/YYYY/MM/DD)")
    print(" [3] Tidy Moment      (Photos & Videos -> Moment/YYYY/MM/DD)")
    print(" [4] Keluar")
    print("=" * 52)
    
    choice = input("Pilih mode [1-4]: ").strip()
    if choice == "1":
        return "tidy"
    elif choice == "2":
        return "workstation"
    elif choice == "3":
        return "moment"
    elif choice == "4":
        print("Membatalkan operasi. Sampai jumpa!")
        sys.exit(0)
    else:
        print("Pilihan tidak valid. Default ke Tidy File.")
        return "tidy"

def parse_args():
    parser = argparse.ArgumentParser(
        description="TidyFile: Central file organization utility (Tidy File, Workstation, & Moment)."
    )
    parser.add_argument(
        "mode", 
        nargs="?", 
        choices=["tidy", "workstation", "moment", "1", "2", "3", "menu"],
        default=None,
        help="Mode operasi: tidy (1), workstation (2), moment (3), atau menu."
    )
    parser.add_argument("--watch", action="store_true", help="Menjalankan monitoring real-time di background.")
    parser.add_argument("--path", type=str, help="Path folder spesifik yang ingin dirapikan.")
    parser.add_argument("-v", "--version", action="version", version=f"TidyFile v{__version__}")
    return parser.parse_args()


def main():
    logger = setup_logging()
    args = parse_args()

    config_path = Path("config.json")
    config = ConfigManager(config_path)

    # Tentukan mode
    selected_mode = args.mode
    if selected_mode == "menu":
        selected_mode = show_interactive_menu()
    elif selected_mode is None:
        if not args.watch and not args.path:
            # Jika dijalankan tanpa argumen apapun di terminal interaktif
            if sys.stdin.isatty():
                selected_mode = show_interactive_menu()
            else:
                selected_mode = "tidy"
        else:
            selected_mode = "tidy"

    mode_name, organizer = get_organizer_by_mode(selected_mode, config)
    logger.info(f"Mode aktif: {mode_name.upper()} ({organizer.__class__.__name__})")

    if args.watch:
        logger.info(f"Memulai TidyFile [{mode_name}] dalam mode Watchdog (Real-time monitoring)...")
        from src.watcher import start_watcher
        start_watcher(config, organizer)
    else:
        logger.info(f"Memulai TidyFile [{mode_name}] dalam mode Sekali Jalan (One-off)...")
        if args.path:
            specific_path = Path(args.path).resolve()
            logger.info(f"Target spesifik dari argumen --path: {specific_path}")
            organizer.organize_folder(specific_path)
        else:
            for folder in config.target_folders:
                organizer.organize_folder(folder)
        logger.info(f"TidyFile [{mode_name}] selesai merapikan file.")

    return 0

if __name__ == "__main__":
    main()
