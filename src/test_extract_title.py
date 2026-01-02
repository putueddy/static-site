import unittest
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import extract_title


class TestExtractTitle(unittest.TestCase):
    
    def test_basic_h1(self):
        """Test basic h1 extraction"""
        markdown = "# Hello World"
        result = extract_title(markdown)
        self.assertEqual(result, "Hello World")
    
    def test_h1_with_extra_whitespace(self):
        """Test h1 with extra whitespace"""
        markdown = "#    Hello World    "
        result = extract_title(markdown)
        self.assertEqual(result, "Hello World")
    
    def test_h1_with_inline_markdown(self):
        """Test h1 with inline markdown formatting"""
        markdown = "# Hello **World**"
        result = extract_title(markdown)
        self.assertEqual(result, "Hello **World**")
    
    def test_h1_not_at_start(self):
        """Test h1 not at the start of file"""
        markdown = "Some text\n# Real Title\nMore text"
        result = extract_title(markdown)
        self.assertEqual(result, "Real Title")
    
    def test_multiple_h1_returns_first(self):
        """Test that first h1 is returned when multiple exist"""
        markdown = "# First Title\nSome content\n# Second Title"
        result = extract_title(markdown)
        self.assertEqual(result, "First Title")
    
    def test_h2_not_extracted(self):
        """Test that h2 headers are not extracted"""
        markdown = "## Not H1\n# Real H1"
        result = extract_title(markdown)
        self.assertEqual(result, "Real H1")
    
    def test_no_h1_raises_exception(self):
        """Test that exception is raised when no h1 is found"""
        markdown = "## H2\n### H3\nJust text"
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertIn("No h1 header found", str(context.exception))
    
    def test_empty_h1_raises_exception(self):
        """Test that empty h1 raises exception"""
        markdown = "#   "
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertIn("No h1 header found", str(context.exception))
    
    def test_hash_in_text_not_h1(self):
        """Test that # in text that's not at start doesn't count"""
        markdown = "This is # not a header\n# Real Header"
        result = extract_title(markdown)
        self.assertEqual(result, "Real Header")
    
    def test_h1_with_newlines(self):
        """Test h1 extraction with newlines around"""
        markdown = "\n\n# Title with newlines\n\n"
        result = extract_title(markdown)
        self.assertEqual(result, "Title with newlines")


if __name__ == "__main__":
    unittest.main()
