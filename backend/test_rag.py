import unittest
import os
import shutil
import tempfile
import sqlite3
import json
from unittest.mock import MagicMock, patch
from backend.rag import RAGEngine
from project_config import Config

class TestRAG(unittest.TestCase):
    def setUp(self):
        # Setup mock DB and Vault
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        Config.DB_PATH = self.db_path
        Config.ASSETS_DIR = self.test_dir
        
        # Create vault dir
        os.makedirs(os.path.join(self.test_dir, "vault"))
        
        self.rag = RAGEngine()
        # Mocking genai.embed_content to avoid API calls and costs during unit testing
        # We patch it at the class level or method level
        
    def tearDown(self):
        try:
             shutil.rmtree(self.test_dir)
        except:
            pass

    @patch('backend.rag.genai.embed_content')
    def test_ingest_and_retrieve(self, mock_embed):
        # 1. Setup Dummy File
        vault_file = os.path.join(self.test_dir, "vault", "secret.txt")
        with open(vault_file, "w") as f:
            f.write("The secret code is BANANA_BLUE.")

        # 2. Mock Embedding Response
        # Ingest calls it once per chunk. Retrieve calls it once for query.
        # Simple mock: return random vector
        mock_embed.return_value = {'embedding': [0.1, 0.2, 0.3]}
        
        # 3. Ingest
        report = self.rag.ingest_vault()
        self.assertIn("Ingested 1 files", report)
        
        # Verify DB content
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM embeddings")
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertIn("BANANA_BLUE", rows[0][0])

        # 4. Retrieve
        # Mock retrieval embedding to ensure dot product works (same vector = high score)
        mock_embed.return_value = {'embedding': [0.1, 0.2, 0.3]} 
        
        results = self.rag.retrieve("What is the secret code?")
        self.assertEqual(len(results), 1)
        self.assertIn("BANANA_BLUE", results[0]['content'])

if __name__ == '__main__':
    unittest.main()
