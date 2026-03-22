from __future__ import annotations

from georesolve.providers.census import CensusConfig, CensusGeocoderProvider

SUPPORTED_PROVIDERS = ("census",)


def create_provider(
    provider_name: str = "census",
    *,
    benchmark: str = "Public_AR_Current",
    vintage: str = "Current_Current",
    timeout_seconds: float = 15.0,
):
    normalized = provider_name.strip().lower()
    if normalized != "census":
        supported = ", ".join(SUPPORTED_PROVIDERS)
        raise ValueError(f"Unsupported provider: {provider_name}. Supported providers: {supported}")

    return CensusGeocoderProvider(
        CensusConfig(
            benchmark=benchmark,
            vintage=vintage,
            timeout_seconds=timeout_seconds,
        )
    )
