"""
Basic tests for the AI Content Creator application.
"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests."""
    
    def test_imports(self):
        """Test that main modules can be imported."""
        try:
            import app
            import content_pipeline
            import scraper
            import groq_processor
            import email_sender
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")
    
    def test_config_exists(self):
        """Test that configuration files exist."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sources.py')
        self.assertTrue(os.path.exists(config_path), "Config sources.py should exist")
    
    def test_requirements_exist(self):
        """Test that requirements.txt exists."""
        req_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        self.assertTrue(os.path.exists(req_path), "requirements.txt should exist")

if __name__ == '__main__':
    unittest.main()
