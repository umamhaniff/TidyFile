import unittest
import tempfile
from pathlib import Path
from src.core import WorkstationOrganizer, MomentOrganizer

class TestOrganizersModes(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_workstation_organizer(self):
        organizer = WorkstationOrganizer()
        
        doc = self.root / "2024-05-12_Laporan_Keuangan.xlsx"
        doc.write_text("dummy excel")

        organizer.organize_folder(self.root)

        expected_dest = self.root / "Workstation-2024-05-12" / "2024-05-12_Laporan_Keuangan.xlsx"
        self.assertTrue(expected_dest.exists())
        self.assertFalse(doc.exists())

    def test_moment_organizer(self):
        organizer = MomentOrganizer()
        
        photo = self.root / "IMG_20231225_201530.jpg"
        photo.write_text("dummy photo")

        organizer.organize_folder(self.root)

        expected_dest = self.root / "Moment-2023-12-25" / "IMG_20231225_201530.jpg"
        self.assertTrue(expected_dest.exists())
        self.assertFalse(photo.exists())

if __name__ == "__main__":
    unittest.main()
