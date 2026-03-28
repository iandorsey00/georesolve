import unittest

from georesolve.interfaces.api import _resolve_query_target


class ApiTests(unittest.TestCase):
    def test_resolve_query_target_accepts_query(self):
        self.assertEqual(_resolve_query_target("38.8899,-77.0091", None), "38.8899,-77.0091")

    def test_resolve_query_target_accepts_address(self):
        self.assertEqual(_resolve_query_target(None, "1600 Pennsylvania Ave NW"), "1600 Pennsylvania Ave NW")

    def test_resolve_query_target_rejects_both(self):
        with self.assertRaisesRegex(ValueError, "not both"):
            _resolve_query_target("38.8899,-77.0091", "1600 Pennsylvania Ave NW")

    def test_resolve_query_target_requires_one(self):
        with self.assertRaisesRegex(ValueError, "Provide either"):
            _resolve_query_target(None, None)


if __name__ == "__main__":
    unittest.main()
