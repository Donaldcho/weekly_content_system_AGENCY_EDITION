import unittest
from unittest.mock import MagicMock, patch
from backend.brand_analyzer import BrandAnalyzer
import json

class TestBrandAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = BrandAnalyzer()

    @patch('backend.brand_analyzer.genai.GenerativeModel')
    def test_analyze_style(self, mock_model_cls):
        # Mock the response from Gemini
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"tone": "Professional", "style_guide": "Use clear headers"}'
        mock_model.generate_content.return_value = mock_response
        
        # Assign mock to the instance
        self.analyzer.text_model = mock_model
        
        result = self.analyzer.analyze_style("Sample text")
        self.assertEqual(result['tone'], "Professional")
        self.assertEqual(result['style_guide'], "Use clear headers")

    @patch('backend.brand_analyzer.requests.get')
    def test_analyze_website(self, mock_get):
        # Mock website fetch
        mock_resp = MagicMock()
        mock_resp.content = b"<html><body>Brand Mission</body></html>"
        mock_get.return_value = mock_resp
        
        # Mock Gemini
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"name": "TestBrand", "mission": "Testing"}'
        
        # Assign mock FIRST
        self.analyzer.text_model = mock_model
        mock_model.generate_content.return_value = mock_response

        result = self.analyzer.analyze_website("http://test.com")
        self.assertEqual(result['name'], "TestBrand")

    def test_clean_json(self):
        raw = "```json\n{\"test\": 1}\n```"
        clean = self.analyzer._clean_json(raw)
        self.assertEqual(clean['test'], 1)

if __name__ == '__main__':
    unittest.main()
