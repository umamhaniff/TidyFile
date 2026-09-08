import unittest
import tempfile
import os
import io
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from PIL import Image
from src.metadata_parser import MetadataParser

class TestMetadataParser(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_date_string_formats(self):
        self.assertEqual(MetadataParser.parse_date_string("2026:03:08 10:30:00"), datetime(2026, 3, 8, 10, 30))
        self.assertEqual(MetadataParser.parse_date_string("2026-03-08 10:30:00"), datetime(2026, 3, 8, 10, 30))
        self.assertEqual(MetadataParser.parse_date_string("2026-03-08T10:30:00"), datetime(2026, 3, 8, 10, 30))
        self.assertEqual(MetadataParser.parse_date_string("2026-03-08"), datetime(2026, 3, 8))
        self.assertEqual(MetadataParser.parse_date_string("20260308_120000"), datetime(2026, 3, 8, 12, 0))
        self.assertIsNone(MetadataParser.parse_date_string("invalid_date_string"))
        self.assertIsNone(MetadataParser.parse_date_string(""))

    def test_filename_date_whatsapp(self):
        f1 = self.root / "IMG-20260308-WA0001.jpg"
        f1.write_text("dummy")
        dt = MetadataParser.get_filename_date(f1)
        self.assertEqual(dt, datetime(2026, 3, 8))

        f2 = self.root / "VID-20251225-WA0010.mp4"
        f2.write_text("dummy")
        dt2 = MetadataParser.get_filename_date(f2)
        self.assertEqual(dt2, datetime(2025, 12, 25))

    def test_filename_date_camera_and_screenshots(self):
        f1 = self.root / "IMG_20260115_143022.jpg"
        f1.write_text("dummy")
        self.assertEqual(MetadataParser.get_filename_date(f1), datetime(2026, 1, 15))

        f2 = self.root / "Screenshot_2026-02-20-09-15-00.png"
        f2.write_text("dummy")
        self.assertEqual(MetadataParser.get_filename_date(f2), datetime(2026, 2, 20))

        f3 = self.root / "2024-11-05_Laporan_Akhir.pdf"
        f3.write_text("dummy")
        self.assertEqual(MetadataParser.get_filename_date(f3), datetime(2024, 11, 5))

    def test_filename_date_dd_mm_yyyy(self):
        f = self.root / "Invoice_25-12-2023.pdf"
        f.write_text("dummy")
        self.assertEqual(MetadataParser.get_filename_date(f), datetime(2023, 12, 25))

    def test_embedded_exif_image(self):
        img_path = self.root / "photo.jpg"
        img = Image.new("RGB", (10, 10), color="red")
        exif = img.getexif()
        exif[306] = "2023:08:17 10:00:00"
        img.save(img_path, exif=exif)

        dt = MetadataParser.get_embedded_date(img_path)
        self.assertEqual(dt, datetime(2023, 8, 17, 10, 0, 0))

    @patch('src.metadata_parser.TinyTag.get')
    def test_embedded_tinytag_video(self, mock_tinytag_get):
        video_file = self.root / "clip.mp4"
        video_file.write_text("dummy video")
        
        mock_tag = MagicMock()
        mock_tag.year = "2024-06-15 08:30:00"
        mock_tinytag_get.return_value = mock_tag

        dt = MetadataParser.get_embedded_date(video_file)
        self.assertEqual(dt, datetime(2024, 6, 15, 8, 30, 0))

    @patch('src.metadata_parser.createParser')
    @patch('src.metadata_parser.extractMetadata')
    def test_embedded_hachoir_fallback(self, mock_extract, mock_create):
        doc_file = self.root / "document.xyz"
        doc_file.write_text("dummy")

        mock_parser = MagicMock()
        mock_create.return_value = mock_parser
        
        mock_meta = MagicMock()
        mock_meta.has.side_effect = lambda k: k == "creation_date"
        mock_meta.get.return_value = datetime(2021, 10, 5, 12, 0, 0)
        mock_extract.return_value = mock_meta

        dt = MetadataParser.get_embedded_date(doc_file)
        self.assertEqual(dt, datetime(2021, 10, 5, 12, 0, 0))

    def test_extract_date_fallback_hierarchy(self):
        # 1. Embedded takes precedence over filename
        img_path = self.root / "IMG_20260101_000000.jpg"
        img = Image.new("RGB", (10, 10), color="blue")
        exif = img.getexif()
        exif[306] = "2022:05:20 12:00:00"
        img.save(img_path, exif=exif)

        y, m, d = MetadataParser.extract_date(img_path)
        self.assertEqual((y, m, d), ("2022", "05", "20"))

        # 2. Filename takes precedence over filesystem
        f_no_meta = self.root / "IMG_20250704_120000.txt"
        f_no_meta.write_text("test")
        y, m, d = MetadataParser.extract_date(f_no_meta)
        self.assertEqual((y, m, d), ("2025", "07", "04"))

        # 3. Filesystem fallback when no embedded and no regex
        f_random = self.root / "random_document.docx"
        f_random.write_text("test")
        y, m, d = MetadataParser.extract_date(f_random)
        now = datetime.now()
        self.assertEqual(y, f"{now.year:04d}")
        self.assertEqual(m, f"{now.month:02d}")
        self.assertEqual(d, f"{now.day:02d}")

if __name__ == "__main__":
    unittest.main()
