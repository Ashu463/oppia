# coding: utf-8
#
# Copyright 2023 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for scripts/image_compression.py."""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import unittest
from unittest import mock

from scripts import image_compression

from PIL import Image
from typing import List, Tuple, Union, Optional


class MockCompletedProcess:
    """Mock for subprocess.CompletedProcess."""
    def __init__(self, returncode: int, stderr: bytes = b''):
        self.returncode = returncode
        self.stderr = stderr

class TestImageCompression(unittest.TestCase):
    """Unit tests for image compression script."""

    def setUp(self) -> None:
        """Set up test environment with actual test images."""
        self.test_dir = pathlib.Path('./test_assets')
        self.test_dir.mkdir(exist_ok=True)
        
        # Create test images with actual content
        self.test_files = {
            'test_image.jpg': self.create_noisy_image('test_image.jpg', (100, 100)),
            'test_image.png': self.create_noisy_image('test_image.png', (100, 100)),
            'test_image.webp': self.create_noisy_image('test_image.webp', (100, 100)),
            'test_small.png': self.create_optimized_image('test_small.png', (50, 50)),
            'unsupported.bmp': self.create_noisy_image('unsupported.bmp', (100, 100))
        }
        
        # Store original file sizes
        self.original_sizes = {
            file_path: file_path.stat().st_size 
            for file_path in self.test_dir.glob('*')
        }

        img = Image.new('RGB', (100, 100), color='white')
        self.test_image = self.test_dir / 'test_compression.jpg'
        img.save(self.test_image, optimize=True, quality=95)

    def tearDown(self) -> None:
        """Clean up test directory and files."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def create_noisy_image(self, filename: str, size: Tuple[int, int]) -> pathlib.Path:
        """Create a test image with noise to ensure it's compressible."""
        img = Image.new('RGB', size)
        pixels = img.load()
        
        # Add random noise to make image more compressible
        import random
        for x in range(size[0]):
            for y in range(size[1]):
                pixels[x, y] = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
        
        file_path = self.test_dir / filename
        img.save(file_path, quality=95)  # Save with high quality to allow room for compression
        return file_path

    def create_optimized_image(self, filename: str, size: Tuple[int, int]) -> pathlib.Path:
        """Create an already optimized image that shouldn't compress further."""
        img = Image.new('RGB', size, color='white')  # Solid color = highly compressed
        file_path = self.test_dir / filename
        img.save(file_path, optimize=True, quality=60)  # Save with optimization
        return file_path

    def test_real_compression(self) -> None:
        """Test actual image compression with real files."""
        if not shutil.which('gm'):
            self.skipTest("GraphicsMagick not installed")
            
        compressed_images = image_compression.check_and_compress_images(str(self.test_dir))
        
        # Verify compression results
        self.assertGreater(len(compressed_images), 0, "No images were compressed")
        
        for image_info in compressed_images:
            path = image_info['path']
            original_size = image_info['original_size']
            new_size = image_info['new_size']
            
            # Verify size reduction
            self.assertLess(new_size, original_size, 
                          f"Failed to compress {path.name}")
            
            # Verify image is still valid
            try:
                with Image.open(path) as img:
                    img.verify()
            except Exception as e:
                self.fail(f"Compressed image {path.name} is corrupt: {e}")
    
    def test_already_optimized_image(self) -> None:
        """Test handling of already optimized images."""
        if not shutil.which('gm'):
            self.skipTest("GraphicsMagick not installed")
            
        test_image = self.test_dir / 'test_small.png'
        original_size = test_image.stat().st_size
        
        compressed_images = image_compression.check_and_compress_images(str(self.test_dir))
        
        # Check if the optimized image wasn't compressed
        optimized_results = [img for img in compressed_images if img['path'] == test_image]
        self.assertEqual(len(optimized_results), 0, 
                        "Already optimized image shouldn't be compressed further")

    def test_unsupported_format(self) -> None:
        """Test handling of unsupported image formats."""
        if not shutil.which('gm'):
            self.skipTest("GraphicsMagick not installed")
            
        bmp_path = self.test_dir / 'unsupported.bmp'
        original_size = bmp_path.stat().st_size
        
        compressed_images = image_compression.check_and_compress_images(str(self.test_dir))
        
        # Verify BMP wasn't processed
        bmp_results = [img for img in compressed_images if img['path'] == bmp_path]
        self.assertEqual(len(bmp_results), 0, 
                        "Unsupported format shouldn't be processed")
        
        # Verify BMP wasn't modified
        self.assertEqual(bmp_path.stat().st_size, original_size,
                        "Unsupported format file was modified")

    def test_failed_compression(self) -> None:
        """Test when compression process fails."""
        original_size = self.test_image.stat().st_size
        
        # Mock subprocess to return failure
        mock_result = MockCompletedProcess(returncode=1, stderr=b'Mock error')
        
        with mock.patch('subprocess.run', return_value=mock_result), \
             mock.patch('builtins.print') as mock_print:
            
            compressed_images = image_compression.check_and_compress_images(str(self.test_dir))
            
            # Verify results
            self.assertEqual(len(compressed_images), 0)
            mock_print.assert_called_with('Compressed image > original image')
            self.assertEqual(
                self.test_image.stat().st_size, 
                original_size, 
                "Original file was modified"
            )

    def test_error_handling(self) -> None:
        """Test error handling for corrupt or inaccessible images."""
        # Create a corrupt image file
        corrupt_path = self.test_dir / 'corrupt.jpg'
        with open(corrupt_path, 'wb') as f:
            f.write(b'Not an image file')
            
        try:
            compressed_images = image_compression.check_and_compress_images(str(self.test_dir))
            
            # Verify corrupt file wasn't processed
            corrupt_results = [img for img in compressed_images if img['path'] == corrupt_path]
            self.assertEqual(len(corrupt_results), 0,
                           "Corrupt image shouldn't be processed")
        finally:
            corrupt_path.unlink(missing_ok=True)

    def test_multiple_iterations(self) -> None:
        """Test multiple compression iterations."""
        if not shutil.which('gm'):
            self.skipTest("GraphicsMagick not installed")
            
        # Run compression multiple times
        first_run = image_compression.check_and_compress_images(str(self.test_dir))
        second_run = image_compression.check_and_compress_images(str(self.test_dir))
        
        # Second run should compress fewer images or none at all
        self.assertGreaterEqual(len(first_run), len(second_run),
                              "Subsequent compression shouldn't find more images to compress")


if __name__ == '__main__':
    unittest.main()