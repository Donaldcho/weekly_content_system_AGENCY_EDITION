import unittest
import os
import shutil
import tempfile
import json
from datetime import datetime
from backend.database import Database
from project_config import Config

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Override DB path for testing
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        Config.DB_PATH = self.db_path
        self.db = Database()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_brand_settings(self):
        original = self.db.get_brand_settings()
        self.assertTrue("Deviceterra" in original)
        
        new_settings = "Brand: TestBrand\nTone: Fun"
        self.db.save_brand_settings(new_settings)
        
        retrieved = self.db.get_brand_settings()
        self.assertEqual(retrieved, new_settings)

    def test_scheduled_posts(self):
        post = {
            "id": "123",
            "platform": "LinkedIn",
            "content": "Test Post",
            "scheduled_time": "2025-01-01 10:00:00",
            "status": "scheduled"
        }
        
        self.db.add_scheduled_post(post)
        
        scheduled = self.db.get_scheduled_posts()
        self.assertEqual(len(scheduled), 1)
        self.assertEqual(scheduled[0]['id'], "123")
        self.assertEqual(scheduled[0]['status'], "scheduled")
        
        # Test mark as posted
        self.db.mark_as_posted("123")
        scheduled = self.db.get_scheduled_posts()
        self.assertEqual(len(scheduled), 0)
        
        history = self.db.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['status'], "posted")

if __name__ == '__main__':
    unittest.main()
