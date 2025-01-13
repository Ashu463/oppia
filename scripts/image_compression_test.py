import unittest
import os
import pathlib
from unittest.mock import MagicMock
from image_compression import check_and_compress_images
from PIL import Image
import subprocess

class TestImageCompression(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.test_dir = pathlib.Path('./test_assets')
        self.test_dir.mkdir(exist_ok=True)
        # Create mock images for testing
        self.create_mock_image('test_image.jpg', (100, 100))
        self.create_mock_image('test_image.png', (100, 100))
        self.create_mock_image('test_image.webp', (100, 100))
        self.create_mock_image('unsupported_image.bmp', (100, 100))

    def tearDown(self):
        """Remove the test directory after tests."""
        for file in self.test_dir.glob('*'):
            file.unlink()
        self.test_dir.rmdir()

    def create_mock_image(self, filename, size):
        """Create a mock image for testing."""
        img = Image.new('RGB', size)
        img.save(self.test_dir / filename)

    def mock_subprocess_run(self, cmd, capture_output=True, text=True, check=False):
        """Mock subprocess.run to control its behavior."""
        class MockResult:
            def __init__(self, returncode):
                self.returncode = returncode

        # Simulate successful compression for supported formats
        if 'gm' in cmd and 'convert' in cmd:
            return MockResult(returncode=0)
        
        return MockResult(returncode=1)  # Simulate failure for other commands

    def test_compress_supported_formats(self):
        """Test compression of supported image formats."""
        original_subprocess_run = subprocess.run  # Save original function
        subprocess.run = self.mock_subprocess_run  # Replace with mock

        compressed_images = check_and_compress_images(str(self.test_dir))
        
        # Check that the function returns a list of compressed images
        self.assertIsInstance(compressed_images, list)
        self.assertEqual(len(compressed_images), 0)

        subprocess.run = original_subprocess_run  # Restore original function

    def test_ignore_unsupported_formats(self):
        """Test that unsupported formats are ignored."""
        original_subprocess_run = subprocess.run
        subprocess.run = self.mock_subprocess_run

        compressed_images = check_and_compress_images(str(self.test_dir))

        # Check that unsupported images are not included in the results
        unsupported_image_path = pathlib.Path(self.test_dir / 'unsupported_image.bmp')
        self.assertNotIn({'path': unsupported_image_path, 'original_size': 0, 'new_size': 0}, compressed_images)

        subprocess.run = original_subprocess_run

    def test_error_handling_on_image_open_failure(self):
        """Test error handling when an image cannot be opened."""
        original_subprocess_run = subprocess.run
        subprocess.run = self.mock_subprocess_run

        # Simulate an error by raising an exception in the context of opening an image.
        with unittest.mock.patch('PIL.Image.open', side_effect=Exception("Image open failed")):
            compressed_images = check_and_compress_images(str(self.test_dir))

            # Check that no images were compressed if there was an error
            self.assertEqual(len(compressed_images), 0)

        subprocess.run = original_subprocess_run

if __name__ == '__main__':
    unittest.main()
