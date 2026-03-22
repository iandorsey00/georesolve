from __future__ import annotations

from georesolve.models import ResolveResult
from georesolve.providers.base import GeocodeProvider, GeographyProvider


class Resolver:
    def __init__(
        self,
        geocoder: GeocodeProvider,
        geography_provider: GeographyProvider | None = None,
    ):
        self.geocoder = geocoder
        self.geography_provider = geography_provider or geocoder

    def resolve(self, address: str) -> ResolveResult:
        geocoded = self.geocoder.geocode(address)
        geographies = geocoded.geographies

        if not any(match is not None for match in geographies.values()):
            geographies = self.geography_provider.reverse_geographies(
                latitude=geocoded.coordinates.latitude,
                longitude=geocoded.coordinates.longitude,
            )

        return ResolveResult(
            input_address=address,
            matched_address=geocoded.matched_address,
            coordinates=geocoded.coordinates,
            geographies=geographies,
            geocoder=geocoded.provider,
            geography_source=self.geography_provider.name,
            benchmark=geocoded.benchmark,
            vintage=geocoded.vintage,
        )
