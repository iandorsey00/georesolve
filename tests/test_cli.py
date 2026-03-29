import unittest

from georesolve.interfaces.cli import build_parser


class CliTests(unittest.TestCase):
    def test_resolve_parser_accepts_provider_options(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "resolve",
                "1600 Pennsylvania Ave NW, Washington, DC 20500",
                "--provider",
                "census",
                "--benchmark",
                "Public_AR_ACS2025",
                "--vintage",
                "ACS2025_Current",
                "--timeout-seconds",
                "7.5",
            ]
        )

        self.assertEqual(args.command, "resolve")
        self.assertEqual(args.provider, "census")
        self.assertEqual(args.query, "1600 Pennsylvania Ave NW, Washington, DC 20500")
        self.assertEqual(args.benchmark, "Public_AR_ACS2025")
        self.assertEqual(args.vintage, "ACS2025_Current")
        self.assertEqual(args.timeout_seconds, 7.5)

    def test_resolve_coordinates_parser_accepts_coordinates(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "resolve-coordinates",
                "38.8899",
                "-77.0091",
                "--provider",
                "census",
            ]
        )

        self.assertEqual(args.command, "resolve-coordinates")
        self.assertEqual(args.latitude, 38.8899)
        self.assertEqual(args.longitude, -77.0091)
        self.assertEqual(args.provider, "census")

    def test_resolve_parser_accepts_url_like_query(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "resolve",
                "https://www.google.com/maps/@38.8899,-77.0091,15z",
            ]
        )

        self.assertEqual(args.command, "resolve")
        self.assertEqual(args.query, "https://www.google.com/maps/@38.8899,-77.0091,15z")

    def test_resolve_current_location_alias_still_works(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "resolve-current-location",
                "38.8899",
                "-77.0091",
            ]
        )

        self.assertEqual(args.command, "resolve-current-location")
        self.assertEqual(args.latitude, 38.8899)
        self.assertEqual(args.longitude, -77.0091)


if __name__ == "__main__":
    unittest.main()
