import unittest
import os
import sys

# Add parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.content_generator import ContentGenerator

class TestMASPipeline(unittest.TestCase):
    def setUp(self):
        self.gen = ContentGenerator()
        
    def test_weekly_plan_mas(self):
        print("\n[TEST] Testing MAS Weekly Plan...")
        
        # Test with a dummy topic
        topic = "AI Agents in 2025"
        plan = self.gen.generate_weekly_plan(
            topic=topic,
            trends="Automation is key",
            model_name="gemini-2.0-flash-exp",
            use_rag=False # Skip RAG for speed in test
        )
        
        self.assertTrue(len(plan) > 0, "Plan should not be empty")
        
        first_day = plan[0]
        print(f"Result keys: {first_day.keys()}")
        
        self.assertIn("day", first_day)
        self.assertIn("linkedin_draft", first_day)
        self.assertIn("quality_score", first_day, "Reviewer should have added a score")
        
        print(f"Sample Draft: {first_day['linkedin_draft'][:50]}...")
        print(f"Critique: {first_day.get('critique', 'None')}")

if __name__ == "__main__":
    unittest.main()
