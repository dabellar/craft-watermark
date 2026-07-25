"""
Darleine Abellard
craft-watermark

Automated tests for the creator database logic. Uses a separate,
temporary test database file so these tests never touch or corrupt
your real watermark.db.
"""

import unittest
import os
import src.database as database


TEST_DB_PATH = "test_watermark.db"


class TestDatabase(unittest.TestCase):
    """Tests for register_creator, record_watermarked_image, and
    get_creator_by_id."""

    def setUp(self):
        """
        Runs automatically BEFORE every individual test method.
        Points the database module at a separate test file, so these
        tests never read or write your real watermark.db.
        """
        database.DB_PATH = TEST_DB_PATH

    def tearDown(self):
        """Deletes the test database file after every test, so each
        test starts from a genuinely clean, empty database."""
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def test_register_creator_returns_an_id(self):
        """Registering a new creator should return a real, usable id."""
        creator_id = database.register_creator("Test Creator", "test@example.com")

        self.assertIsInstance(creator_id, int)
        self.assertGreater(creator_id, 0)

    def test_get_creator_by_id_returns_correct_info(self):
        """Looking up a creator by their id should return exactly the
        info they were registered with."""
        creator_id = database.register_creator("Jane Doe", "jane@example.com")

        creator = database.get_creator_by_id(creator_id)

        self.assertEqual(creator["name"], "Jane Doe")
        self.assertEqual(creator["contact_info"], "jane@example.com")

    def test_get_creator_by_id_returns_none_for_unknown_id(self):
        """Looking up an id that was never registered should return
        None, not raise an error or return incorrect data."""
        creator = database.get_creator_by_id(999999)

        self.assertIsNone(creator)

    def test_record_watermarked_image_succeeds_for_real_creator(self):
        """Recording an image for a real, existing creator should
        succeed without error."""
        creator_id = database.register_creator("Real Creator")

        try:
            database.record_watermarked_image(creator_id, "fake_hash_value")
        except Exception:
            self.fail("record_watermarked_image raised an error for a valid creator_id")

    def test_record_watermarked_image_rejects_unknown_creator(self):
        """The foreign key constraint should prevent recording an
        image for a creator_id that doesn't actually exist."""
        with self.assertRaises(Exception):
            database.record_watermarked_image(999999, "fake_hash_value")


if __name__ == "__main__":
    unittest.main()