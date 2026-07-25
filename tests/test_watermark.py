"""
Darleine Abellard
craft-watermark

Automated tests for the core watermarking logic (embed/extract).
"""

import unittest
import os
from src.watermark import embed_watermark, extract_watermark, WATERMARK_BITS


TEST_IMAGE = "examples/test.png"
TEST_OUTPUT = "examples/_test_output.png"


class TestWatermark(unittest.TestCase):
    """Tests for embed_watermark and extract_watermark."""

    def tearDown(self):
        """
        Runs automatically after every individual test method.
        Deletes any output file a test created, so tests don't leave
        junk behind or interfere with each other by reusing a stale
        file from a previous test.
        """
        if os.path.exists(TEST_OUTPUT):
            os.remove(TEST_OUTPUT)

    def test_embed_and_extract_round_trip(self):
        """A watermark embedded into an image should be recoverable
        exactly, unchanged, from the untouched output file."""
        test_id = 0b10101010101010101010101010101010 & 0xFFFFFFFF

        embed_watermark(TEST_IMAGE, TEST_OUTPUT, test_id)
        recovered = extract_watermark(TEST_OUTPUT)

        self.assertEqual(recovered, test_id)

    def test_round_trip_with_id_zero(self):
        """id 0 (all-zero bits) is an edge case worth testing on its
        own, since an all-zero pattern behaves differently from a
        mixed pattern during embedding."""
        embed_watermark(TEST_IMAGE, TEST_OUTPUT, 0)
        recovered = extract_watermark(TEST_OUTPUT)

        self.assertEqual(recovered, 0)

    def test_round_trip_with_max_id(self):
        """The largest id that fits in WATERMARK_BITS (all 1 bits)
        should also round-trip correctly -- the other edge case."""
        max_id = (2 ** WATERMARK_BITS) - 1

        embed_watermark(TEST_IMAGE, TEST_OUTPUT, max_id)
        recovered = extract_watermark(TEST_OUTPUT)

        self.assertEqual(recovered, max_id)

    def test_rejects_id_too_large(self):
        """Embedding an id that doesn't fit in WATERMARK_BITS should
        raise a clear error, not silently corrupt or truncate it."""
        too_large = 2 ** WATERMARK_BITS

        with self.assertRaises(ValueError):
            embed_watermark(TEST_IMAGE, TEST_OUTPUT, too_large)

    def test_embedding_returns_a_valid_sha256_hash(self):
        """embed_watermark should return a real SHA256 hash (64 hex
        characters) of the file it just wrote."""
        test_id = 12345

        image_hash = embed_watermark(TEST_IMAGE, TEST_OUTPUT, test_id)

        self.assertEqual(len(image_hash), 64)
        # every character should be a valid hex digit
        self.assertTrue(all(c in "0123456789abcdef" for c in image_hash))

    def test_original_file_is_never_modified(self):
        """embed_watermark must never alter the source file -- only
        write to output_path."""
        original_size_before = os.path.getsize(TEST_IMAGE)

        embed_watermark(TEST_IMAGE, TEST_OUTPUT, 42)

        original_size_after = os.path.getsize(TEST_IMAGE)
        self.assertEqual(original_size_before, original_size_after)


if __name__ == "__main__":
    unittest.main()