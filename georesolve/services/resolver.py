from __future__ import annotations

from georesolve.models import Coordinates, ResolveResult
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
            input_coordinates=None,
            matched_address=geocoded.matched_address,
            coordinates=geocoded.coordinates,
            geographies=geographies,
            geocoder=geocoded.provider,
            geography_source=self.geography_provider.name,
            benchmark=geocoded.benchmark,
            vintage=geocoded.vintage,
        )

    def resolve_coordinates(self, latitude: float, longitude: float) -> ResolveResult:
        coordinates = Coordinates(latitude=latitude, longitude=longitude)
        geographies = self.geography_provider.reverse_geographies(
            latitude=latitude,
            longitude=longitude,
        )
        provider_name = self.geography_provider.name
        provider_config = getattr(self.geography_provider, "config", None)

        return ResolveResult(
            input_address=None,
            input_coordinates=coordinates,
            matched_address=None,
            coordinates=coordinates,
            geographies=geographies,
            geocoder=provider_name,
            geography_source=provider_name,
            benchmark=getattr(provider_config, "benchmark", None),
            vintage=getattr(provider_config, "vintage", None),
        )

    def resolve_current_location(self, latitude: float, longitude: float) -> ResolveResult:
        return self.resolve_coordinates(latitude=latitude, longitude=longitude)
