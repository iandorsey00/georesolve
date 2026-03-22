import unittest

from georesolve.providers.census import CensusGeocoderProvider


class CensusProviderNormalizationTests(unittest.TestCase):
    def test_normalize_geographies_prefers_incorporated_place(self):
        raw = {
            "States": [{"GEOID": "06", "NAME": "California"}],
            "Counties": [{"STATE": "06", "COUNTY": "075", "NAME": "San Francisco County"}],
            "Incorporated Places": [{"STATE": "06", "PLACE": "67000", "NAME": "San Francisco"}],
            "Census Designated Places": [{"STATE": "06", "PLACE": "12345", "NAME": "Fallback CDP"}],
            "2020 Census ZIP Code Tabulation Areas": [{"BASENAME": "94107"}],
            "Census Tracts": [{"STATE": "06", "COUNTY": "075", "TRACT": "010100", "NAME": "Census Tract 101"}],
        }

        normalized = CensusGeocoderProvider._normalize_geographies(raw)

        self.assertEqual(normalized["state"].geoid, "06")
        self.assertEqual(normalized["county"].geoid, "06075")
        self.assertEqual(normalized["place"].name, "San Francisco")
        self.assertEqual(normalized["place"].geoid, "0667000")
        self.assertEqual(normalized["place"].source_layer, "Incorporated Places")
        self.assertEqual(normalized["zcta"].geoid, "94107")
        self.assertEqual(normalized["tract"].geoid, "06075010100")

    def test_normalize_geographies_falls_back_to_cdp(self):
        raw = {
            "Census Designated Places": [{"STATE": "48", "PLACE": "35000", "NAME": "Example CDP"}],
        }

        normalized = CensusGeocoderProvider._normalize_geographies(raw)

        self.assertIsNone(normalized["state"])
        self.assertEqual(normalized["place"].name, "Example CDP")
        self.assertEqual(normalized["place"].geoid, "4835000")
        self.assertEqual(normalized["place"].source_layer, "Census Designated Places")


if __name__ == "__main__":
    unittest.main()
