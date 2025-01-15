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

import pathlib
import subprocess
import unittest
from unittest import mock
from typing import List, Tuple, Union
from PIL import Image
from scripts import image_compression


class TestImageCompression(unittest.TestCase):
    """Unit tests for image compression script."""

    def setUp(self) -> None:
        """Set up a temporary directory for testing."""
        self.test_dir = pathlib.Path('./test_assets')
        self.test_dir.mkdir(exist_ok=True)
        self.create_mock_image('test_image.jpg', (100, 100))
        self.create_mock_image('test_image.png', (100, 100))
        self.create_mock_image('test_image.webp', (100, 100))
        self.create_mock_image('unsupported_image.bmp', (100, 100))

    def tearDown(self) -> None:
        """Remove the test directory after tests."""
        for file in self.test_dir.glob('*'):
            file.unlink()
        self.test_dir.rmdir()

    def create_mock_image(self, filename: str, size: Tuple[int, int]) -> None:
        """Create a mock image for testing."""
        img = Image.new('RGB', size)
        img.save(self.test_dir / filename)

    def mock_subprocess_run(
        self,
        cmd: Union[str, List[str]]
    ) -> subprocess.CompletedProcess[bytes]:
        """Mock subprocess.run to control its behavior."""
        class MockResult(subprocess.CompletedProcess[bytes]):
            def __init__(self, returncode: int) -> None:
                super().__init__(args=cmd, returncode=returncode, stdout=b'', stderr=b'')

        if isinstance(cmd, list) and 'gm' in cmd and 'convert' in cmd:
            return MockResult(returncode=0)
        return MockResult(returncode=1)

    def test_compress_supported_formats(self) -> None:
        """Test compression of supported image formats."""
        with mock.patch('subprocess.run', side_effect=self.mock_subprocess_run):
            compressed_images = image_compression.check_and_compress_images(
                str(self.test_dir)
            )
            self.assertIsInstance(compressed_images, list)
            self.assertEqual(len(compressed_images), 0)

    def test_ignore_unsupported_formats(self) -> None:
        """Test that unsupported formats are ignored."""
        with mock.patch('subprocess.run', side_effect=self.mock_subprocess_run):
            compressed_images = image_compression.check_and_compress_images(
                str(self.test_dir)
            )

            unsupported_image_path = pathlib.Path(
                self.test_dir / 'unsupported_image.bmp'
            )
            self.assertNotIn(
                {'path': unsupported_image_path,
                'original_size': 0,
                'new_size': 0},
                compressed_images
            )

    def test_error_handling_on_image_open_failure(self) -> None:
        """Test error handling when an image cannot be opened."""
        mock_image = mock.MagicMock()
        mock_image.__enter__ = mock.MagicMock(return_value=mock_image)
        mock_image.__exit__ = mock.MagicMock(return_value=None)
        with mock.patch('PIL.Image.open', return_value=mock_image) as mock_open:
            mock_open.side_effect = [
                mock_image,
                Exception('Image open failed')
            ]
            with mock.patch('subprocess.run', side_effect=self.mock_subprocess_run):
                compressed_images = image_compression.check_and_compress_images(
                    str(self.test_dir)
                )
                self.assertEqual(len(compressed_images), 0)


if __name__ == '__main__':
    unittest.main()
