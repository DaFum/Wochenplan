import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pollinations.text import Text
from pollinations.image import Image


class PollinationsTestCase(unittest.TestCase):
    """Test cases for Pollinations clients."""

    def test_text_client(self):
        """Test the Text client functionality."""
        with patch('httpx.Client') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = [{'message': {'content': 'Test response'}}]
            mock_client.return_value.__enter__.return_value.post.return_value = mock_response
            
            with Text() as text_client:
                result = text_client('Test prompt')
                self.assertEqual(result, 'Test response')
            
            # Verify the request was made correctly
            mock_client.return_value.__enter__.return_value.post.assert_called_once()
            call_args = mock_client.return_value.__enter__.return_value.post.call_args
            self.assertEqual(call_args[0][0], 'https://text.pollinations.ai/')
            
            # Check that the payload has the correct structure
            payload = call_args[1]['json']
            self.assertIn('messages', payload)
            self.assertEqual(payload['messages'][-1]['content'], 'Test prompt')

    def test_image_client(self):
        """Test the Image client functionality."""
        # Create a fake 1x1 PNG image in memory
        from PIL import Image as PILImage
        fake_image = PILImage.new('RGB', (1, 1), color='red')
        img_bytes = BytesIO()
        fake_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        with patch('httpx.Client') as mock_client:
            mock_response = MagicMock()
            mock_response.content = img_bytes.getvalue()
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            with Image() as image_client:
                result = image_client('test prompt')
                self.assertIsInstance(result, PILImage.Image)
                self.assertEqual(result.size, (1, 1))
            
            # Verify the request was made correctly  
            mock_client.return_value.__enter__.return_value.get.assert_called_once()
            call_args = mock_client.return_value.__enter__.return_value.get.call_args
            self.assertIn('image.pollinations.ai/prompt/', call_args[0][0])


if __name__ == '__main__':
    unittest.main()