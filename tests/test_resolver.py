import unittest

from georesolve.models import Coordinates, GeocodedAddress, GeographyMatch
from georesolve.services import Resolver


class FakeProvider:
    name = "fake"

    def __init__(self, geographies):
        self._geographies = geographies
        self.reverse_calls = 0
        self.geocode_calls = 0

    def geocode(self, address: str) -> GeocodedAddress:
        self.geocode_calls += 1
        return GeocodedAddress(
            provider=self.name,
            matched_address=address.upper(),
            coordinates=Coordinates(latitude=38.0, longitude=-77.0),
            geographies=self._geographies,
            benchmark="bench",
            vintage="vint",
        )

    def reverse_geographies(self, latitude: float, longitude: float):
        self.reverse_calls += 1
        return {
            "state": GeographyMatch(
                kind="state",
                name="District of Columbia",
                geoid="11",
                summary_level="040",
                source_layer="States",
            ),
            "county": None,
            "place": None,
            "zcta": None,
            "tract": None,
        }


class ResolverTests(unittest.TestCase):
    def test_resolve_uses_embedded_geographies_when_available(self):
        provider = FakeProvider(
            geographies={
                "state": GeographyMatch(
                    kind="state",
                    name="District of Columbia",
                    geoid="11",
                    summary_level="040",
                    source_layer="States",
                ),
                "county": None,
                "place": None,
                "zcta": None,
                "tract": None,
            }
        )

        result = Resolver(provider).resolve("1600 Pennsylvania Ave NW")

        self.assertEqual(result.matched_address, "1600 PENNSYLVANIA AVE NW")
        self.assertEqual(result.geoids()["state"], "11")
        self.assertEqual(provider.reverse_calls, 0)

    def test_resolve_falls_back_to_reverse_lookup(self):
        provider = FakeProvider(
            geographies={
                "state": None,
                "county": None,
                "place": None,
                "zcta": None,
                "tract": None,
            }
        )

        result = Resolver(provider).resolve("1600 Pennsylvania Ave NW")

        self.assertEqual(result.geographies["state"].name, "District of Columbia")
        self.assertEqual(provider.reverse_calls, 1)

    def test_resolve_current_location_uses_reverse_lookup(self):
        provider = FakeProvider(
            geographies={
                "state": None,
                "county": None,
                "place": None,
                "zcta": None,
                "tract": None,
            }
        )

        result = Resolver(provider).resolve_current_location(38.8899, -77.0091)

        self.assertIsNone(result.input_address)
        self.assertEqual(result.input_coordinates.latitude, 38.8899)
        self.assertEqual(result.input_coordinates.longitude, -77.0091)
        self.assertEqual(result.coordinates.latitude, 38.8899)
        self.assertEqual(result.coordinates.longitude, -77.0091)
        self.assertEqual(result.geographies["state"].geoid, "11")
        self.assertEqual(provider.reverse_calls, 1)

    def test_resolve_parses_plain_coordinate_pair(self):
        provider = FakeProvider(
            geographies={
                "state": None,
                "county": None,
                "place": None,
                "zcta": None,
                "tract": None,
            }
        )

        result = Resolver(provider).resolve("38.8899, -77.0091")

        self.assertIsNone(result.input_address)
        self.assertEqual(result.input_coordinates.latitude, 38.8899)
        self.assertEqual(result.input_coordinates.longitude, -77.0091)
        self.assertEqual(provider.geocode_calls, 0)
        self.assertEqual(provider.reverse_calls, 1)

    def test_resolve_parses_google_maps_url(self):
        provider = FakeProvider(
            geographies={
                "state": None,
                "county": None,
                "place": None,
                "zcta": None,
                "tract": None,
            }
        )

        result = Resolver(provider).resolve("https://www.google.com/maps/@38.8899,-77.0091,15z")

        self.assertIsNone(result.input_address)
        self.assertEqual(result.input_coordinates.latitude, 38.8899)
        self.assertEqual(result.input_coordinates.longitude, -77.0091)
        self.assertEqual(provider.geocode_calls, 0)
        self.assertEqual(provider.reverse_calls, 1)

    def test_resolve_still_geocodes_address_input(self):
        provider = FakeProvider(
            geographies={
                "state": GeographyMatch(
                    kind="state",
                    name="District of Columbia",
                    geoid="11",
                    summary_level="040",
                    source_layer="States",
                ),
                "county": None,
                "place": None,
                "zcta": None,
                "tract": None,
            }
        )

        result = Resolver(provider).resolve("1600 Pennsylvania Ave NW")

        self.assertEqual(result.input_address, "1600 Pennsylvania Ave NW")
        self.assertEqual(provider.geocode_calls, 1)
        self.assertEqual(provider.reverse_calls, 0)


if __name__ == "__main__":
    unittest.main()
