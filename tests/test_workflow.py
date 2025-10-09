import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflow import ContentWorkflow

class TestContentWorkflow(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv('OPENROUTER_API_KEY', 'test-key')
        self.workflow = ContentWorkflow(self.api_key)
        self.test_topic = "AI in healthcare"
    
    def test_workflow_initialization(self):
        """Test workflow initializes correctly"""
        self.assertIsNotNone(self.workflow)
        self.assertEqual(self.workflow.openrouter_api_key, self.api_key)
    
    def test_blog_post_generation(self):
        """Test blog post generation structure"""
        state = {
            "topic": self.test_topic,
            "blog_post": "",
            "word_count": 0,
            "image_url": "",
            "image_path": "",
            "execution_time": 0.0
        }
        
        result = self.workflow.generate_blog_post(state)
        
        self.assertIsNotNone(result["blog_post"])
        self.assertGreater(len(result["blog_post"]), 0)
        self.assertGreater(result["word_count"], 0)

if __name__ == '__main__':
    unittest.main()