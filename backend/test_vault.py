import unittest
import os
import shutil
import tempfile
from io import BytesIO
from vault import VaultManager

class TestVaultManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault = VaultManager(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_get_asset(self):
        # Create a dummy file
        content = b"test image data"
        file_obj = BytesIO(content)
        filename = "test_image.png"
        
        # Save
        saved_path = self.vault.save_asset(file_obj, filename)
        self.assertIsNotNone(saved_path)
        self.assertTrue(os.path.exists(saved_path))
        
        # Get assets
        assets = self.vault.get_assets()
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0]['filename'], filename)
        self.assertEqual(assets[0]['type'], 'image')

    def test_delete_asset(self):
        # Create a dummy file
        content = b"test video data"
        file_obj = BytesIO(content)
        filename = "test_video.mp4"
        
        self.vault.save_asset(file_obj, filename)
        
        # Delete
        result = self.vault.delete_asset(filename)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, filename)))
        
        # Verify list is empty
        assets = self.vault.get_assets()
        self.assertEqual(len(assets), 0)

if __name__ == '__main__':
    unittest.main()
