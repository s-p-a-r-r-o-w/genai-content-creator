import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from image_generator import generate_and_save_image

class TestImageGenerator(unittest.TestCase):
    
    def test_image_generation_structure(self):
        """Test image generation returns proper structure"""
        prompt = "A simple test image"
        result = generate_and_save_image(prompt)
        
        self.assertIn("prompt", result)
        self.assertIn("image_path", result)
        self.assertIn("error", result)
        self.assertEqual(result["prompt"], prompt)

if __name__ == '__main__':
    unittest.main()