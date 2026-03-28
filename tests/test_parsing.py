import unittest

from georesolve.parsing import parse_coordinates, parse_coordinates_from_url, parse_query_coordinates


class ParsingTests(unittest.TestCase):
    def test_parse_plain_coordinate_pair(self):
        coordinates = parse_coordinates("38.8899, -77.0091")

        self.assertIsNotNone(coordinates)
        self.assertEqual(coordinates.latitude, 38.8899)
        self.assertEqual(coordinates.longitude, -77.0091)

    def test_parse_google_maps_at_url(self):
        coordinates = parse_coordinates_from_url(
            "https://www.google.com/maps/@38.8899,-77.0091,15z"
        )

        self.assertIsNotNone(coordinates)
        self.assertEqual(coordinates.latitude, 38.8899)
        self.assertEqual(coordinates.longitude, -77.0091)

    def test_parse_google_maps_query_url(self):
        coordinates = parse_coordinates_from_url(
            "https://www.google.com/maps/search/?api=1&query=38.8899,-77.0091"
        )

        self.assertIsNotNone(coordinates)
        self.assertEqual(coordinates.latitude, 38.8899)
        self.assertEqual(coordinates.longitude, -77.0091)

    def test_parse_query_coordinates_prefers_supported_patterns(self):
        coordinates = parse_query_coordinates(
            "https://maps.google.com/?q=38.8899,-77.0091"
        )

        self.assertIsNotNone(coordinates)
        self.assertEqual(coordinates.latitude, 38.8899)
        self.assertEqual(coordinates.longitude, -77.0091)

    def test_parse_coordinates_from_url_rejects_non_http_scheme(self):
        coordinates = parse_coordinates_from_url(
            "javascript://maps.google.com/@38.8899,-77.0091"
        )

        self.assertIsNone(coordinates)


if __name__ == "__main__":
    unittest.main()
