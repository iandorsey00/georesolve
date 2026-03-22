import os
import unittest

from georesolve.providers.factory import create_provider
from georesolve.services import Resolver


@unittest.skipUnless(
    os.getenv("GEORESOLVE_RUN_LIVE_TESTS") == "1",
    "Set GEORESOLVE_RUN_LIVE_TESTS=1 to run live Census smoke tests",
)
class LiveCensusSmokeTests(unittest.TestCase):
    def test_census_resolves_known_address(self):
        provider = create_provider("census")
        result = Resolver(provider).resolve("4600 Silver Hill Rd, Washington, DC 20233")

        self.assertAlmostEqual(result.coordinates.latitude, 38.8460, places=2)
        self.assertAlmostEqual(result.coordinates.longitude, -76.9275, places=2)
        self.assertEqual(result.geographies["state"].geoid, "24")
        self.assertEqual(result.geographies["county"].geoid, "24033")
        self.assertIsNotNone(result.geographies["tract"])


if __name__ == "__main__":
    unittest.main()
