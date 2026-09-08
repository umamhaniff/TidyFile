import os
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("TidyFile")

# Try importing Pillow & pillow_heif
try:
    from PIL import Image, ExifTags
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except Exception:
        pass
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Try importing tinytag
try:
    from tinytag import TinyTag
    HAS_TINYTAG = True
except ImportError:
    HAS_TINYTAG = False

# Try importing hachoir
try:
    from hachoir.parser import createParser
    from hachoir.metadata import extractMetadata
    HAS_HACHOIR = True
except ImportError:
    HAS_HACHOIR = False


class MetadataParser:
    """
    Parser metadata tanggal dengan 3-Tier Fallback:
    1. Embedded Metadata (EXIF Image, Video/Audio Container Atoms, Document Header)
    2. Filename Regex Pattern (WhatsApp, Camera, ISO dates, Screenshots)
    3. Filesystem Timestamps (Modified time / Created time)
    """

    @staticmethod
    def parse_date_string(date_str: str) -> Optional[datetime]:
        """Helper untuk parse berbagai format string tanggal."""
        if not date_str:
            return None
        date_str = str(date_str).strip()
        
        # Standard EXIF: "YYYY:MM:DD HH:MM:SS"
        # Standard ISO: "YYYY-MM-DD HH:MM:SS" / "YYYY-MM-DDTHH:MM:SS"
        formats = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y:%m:%d",
            "%Y-%m-%d",
            "%Y%m%d_%H%M%S",
            "%Y%m%d-%H%M%S",
            "%Y%m%d",
        ]
        for fmt in formats:
            try:
                # Truncate timezone/milliseconds if present
                clean_str = date_str[:19].replace("T", " ")
                return datetime.strptime(clean_str, fmt)
            except Exception:
                continue
        return None

    @classmethod
    def get_embedded_date(cls, file_path: Path) -> Optional[datetime]:
        """Tier 1: Ekstraksi tanggal dari metadata file internal."""
        ext = file_path.suffix.lower()

        # 1. Image EXIF via Pillow
        if HAS_PILLOW and ext in [
            ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", 
            ".heic", ".heif", ".dng", ".cr2", ".nef", ".arw"
        ]:
            try:
                with Image.open(file_path) as img:
                    exif_data = img.getexif()
                    if exif_data:
                        # Check EXIF sub-IFDs (34665 is ExifOffset)
                        sub_ifd = exif_data.get_ifd(0x8769) if hasattr(exif_data, "get_ifd") else {}
                        
                        # Tags: 36867 (DateTimeOriginal), 36868 (DateTimeDigitized), 306 (DateTime)
                        for tag_id in (36867, 36868, 306):
                            val = sub_ifd.get(tag_id) or exif_data.get(tag_id)
                            if val:
                                dt = cls.parse_date_string(val)
                                if dt:
                                    return dt
            except Exception as e:
                logger.debug(f"Pillow gagal membaca EXIF {file_path.name}: {e}")

        # 2. Audio/Video metadata via TinyTag
        if HAS_TINYTAG and ext in [
            ".mp4", ".mov", ".m4v", ".mkv", ".avi", ".3gp", ".webm",
            ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma", ".opus"
        ]:
            try:
                tag = TinyTag.get(str(file_path))
                # Check year / other tag info
                if tag.year:
                    # Year might be full date string or just year
                    dt = cls.parse_date_string(str(tag.year))
                    if dt:
                        return dt
            except Exception as e:
                logger.debug(f"TinyTag gagal membaca metadata {file_path.name}: {e}")

        # 3. Universal format fallback via Hachoir
        if HAS_HACHOIR:
            try:
                parser = createParser(str(file_path))
                if parser:
                    with parser:
                        metadata = extractMetadata(parser)
                        if metadata:
                            for key in ("creation_date", "last_modification"):
                                if metadata.has(key):
                                    val = metadata.get(key)
                                    if isinstance(val, datetime):
                                        return val
                                    dt = cls.parse_date_string(str(val))
                                    if dt:
                                        return dt
            except Exception as e:
                logger.debug(f"Hachoir gagal membaca metadata {file_path.name}: {e}")

        return None

    @classmethod
    def get_filename_date(cls, file_path: Path) -> Optional[datetime]:
        """Tier 2: Ekstraksi tanggal dari nama file menggunakan pola Regex."""
        name = file_path.stem

        # Pola umum:
        # 1. WhatsApp: IMG-20260308-WA0001, VID-20260308-WA0001, AUD-20260308-WA0001
        # 2. Camera: IMG_20260308_123456, VID_20260308_123456, PXL_20260308_...
        # 3. Screenshot: Screenshot_2026-03-08-12-34-56, Screenshot_20260308_123456, Screen Shot 2026-03-08
        # 4. Standard ISO: 2026-03-08, 2026_03_08, 2026.03.08
        patterns = [
            # YYYY-MM-DD or YYYY_MM_DD or YYYY.MM.DD
            r"(?<!\d)(20\d{2}|19\d{2})[-_.](0[1-9]|1[0-2])[-_.](0[1-9]|[12]\d|3[01])(?!\d)",
            # YYYYMMDD (misal IMG_20260308_... atau 20260308...)
            r"(?<!\d)(20\d{2}|19\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?!\d)",
            # DD-MM-YYYY or DD_MM_YYYY
            r"(?<!\d)(0[1-9]|[12]\d|3[01])[-_.](0[1-9]|1[0-2])[-_.](20\d{2}|19\d{2})(?!\d)",
        ]

        # Coba pola YYYY-MM-DD / YYYY_MM_DD
        m = re.search(patterns[0], name)
        if m:
            try:
                y, month, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                return datetime(y, month, d)
            except ValueError:
                pass

        # Coba pola YYYYMMDD
        m = re.search(patterns[1], name)
        if m:
            try:
                y, month, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                return datetime(y, month, d)
            except ValueError:
                pass

        # Coba pola DD-MM-YYYY
        m = re.search(patterns[2], name)
        if m:
            try:
                d, month, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                return datetime(y, month, d)
            except ValueError:
                pass

        return None

    @classmethod
    def get_filesystem_date(cls, file_path: Path) -> datetime:
        """Tier 3: Fallback ke filesystem metadata (mtime / ctime)."""
        stat = file_path.stat()
        mtime = stat.st_mtime
        # On Windows, st_ctime is creation time; use earlier of mtime and ctime if valid
        ctime = getattr(stat, "st_ctime", mtime)
        timestamp = min(mtime, ctime) if ctime > 0 else mtime
        return datetime.fromtimestamp(timestamp)

    @classmethod
    def extract_date(cls, file_path: Path) -> Tuple[str, str, str]:
        """
        Mengekstrak tanggal dengan alur 3-Tier:
        1. Embedded Metadata
        2. Filename Regex
        3. Filesystem Timestamps
        
        Returns:
            Tuple[str, str, str]: (YYYY, MM, DD) format string 2-digit untuk MM & DD.
        """
        # Tier 1: Embedded Metadata
        dt = cls.get_embedded_date(file_path)
        if dt:
            logger.debug(f"[Tier 1: Embedded] {file_path.name} -> {dt.strftime('%Y-%m-%d')}")
            return f"{dt.year:04d}", f"{dt.month:02d}", f"{dt.day:02d}"

        # Tier 2: Filename Regex
        dt = cls.get_filename_date(file_path)
        if dt:
            logger.debug(f"[Tier 2: Filename] {file_path.name} -> {dt.strftime('%Y-%m-%d')}")
            return f"{dt.year:04d}", f"{dt.month:02d}", f"{dt.day:02d}"

        # Tier 3: Filesystem Fallback
        dt = cls.get_filesystem_date(file_path)
        logger.debug(f"[Tier 3: Filesystem] {file_path.name} -> {dt.strftime('%Y-%m-%d')}")
        return f"{dt.year:04d}", f"{dt.month:02d}", f"{dt.day:02d}"
