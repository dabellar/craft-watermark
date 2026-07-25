"""
Darleine Abellard
craft-watermark

Automated tests for upload validation logic.
"""

import unittest
from src.validation import (
    validate_file_size,
    validate_file_extension,
    validate_is_real_img,
    validation,
    ValidationError,
    MAX_FILE_SIZE_BYTES,
)


class TestValidation(unittest.TestCase):
    """Tests for the individual and combined validation checks."""

    def test_file_size_within_limit_passes(self):
        """A file smaller than the max size should pass silently."""
        small_file = b"x" * 100  # 100 bytes of dummy content
        try:
            validate_file_size(small_file)
        except ValidationError:
            self.fail("validate_file_size raised an error for a valid-size file")

    def test_file_size_over_limit_raises(self):
        """A file larger than MAX_FILE_SIZE_BYTES should be rejected."""
        oversized_file = b"x" * (MAX_FILE_SIZE_BYTES + 1)

        with self.assertRaises(ValidationError):
            validate_file_size(oversized_file)

    def test_allowed_extension_passes(self):
        """A filename with an allowed extension should pass silently."""
        try:
            validate_file_extension("photo.png")
            validate_file_extension("photo.JPG")  # case-insensitive check
        except ValidationError:
            self.fail("validate_file_extension raised an error for an allowed extension")

    def test_disallowed_extension_raises(self):
        """A filename with a disallowed extension should be rejected."""
        with self.assertRaises(ValidationError):
            validate_file_extension("document.pdf")

    def test_real_image_passes(self):
        """A genuine image's real byte contents should pass."""
        with open("examples/test.png", "rb") as f:
            real_image_bytes = f.read()

        try:
            validate_is_real_img(real_image_bytes)
        except ValidationError:
            self.fail("validate_is_real_image rejected a genuine image")

    def test_fake_image_disguised_as_png_is_rejected(self):
        """A file that is NOT actually image data, even if it were
        named to look like one, must be rejected based on its real
        contents -- this is the core security check of the module."""
        fake_file_bytes = b"this is definitely not a real image file"

        with self.assertRaises(ValidationError):
            validate_is_real_img(fake_file_bytes)

    def test_validate_upload_runs_all_checks(self):
        """validate_upload should catch a failure from ANY individual
        check -- here, a fake image with a technically-allowed
        extension should still be rejected."""
        fake_file_bytes = b"not a real image"

        with self.assertRaises(ValidationError):
            validation("fake.png", fake_file_bytes)


if __name__ == "__main__":
    unittest.main()