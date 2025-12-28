import unittest
import os
import shutil
import tempfile
import sys
# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag import RAGEngine
from project_config import Config

class TestAdvancedRAG(unittest.TestCase):
    def setUp(self):
        # Setup temporary vault and db
        self.test_dir = tempfile.mkdtemp()
        self.vault_dir = os.path.join(self.test_dir, "vault")
        os.makedirs(self.vault_dir)
        
        # Override Config paths purely for this test instance
        # Note: In a real app we'd mock Config, but here we construct RAG with overrides if possible
        # Since RAG uses Config globally, we might need to rely on the test_dir being isolated if we could inject it
        # For now, we will test the chunking logic directly as it is pure function
        self.rag = RAGEngine()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_recursive_chunking(self):
        print("\n[TEST] Testing Recursive Chunking...")
        text = "Hello world. This is a test sentence. " * 50 # Long text
        
        # Test 1: Chunk size smaller than text
        chunks = self.rag._recursive_chunk(text, chunk_size=100, overlap=10)
        
        self.assertTrue(len(chunks) > 1, "Should split into multiple chunks")
        
        # Check if it split reasonably (near sentence end)
        first_chunk = chunks[0]
        print(f"First chunk ({len(first_chunk)} chars): {first_chunk}")
        
        # It should end with a period or space usually
        self.assertTrue(first_chunk.endswith(" ") or first_chunk.endswith("."), "Should end on delimiter")

    def test_chunking_small_text(self):
        text = "Small text."
        chunks = self.rag._recursive_chunk(text, chunk_size=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

if __name__ == "__main__":
    unittest.main()
