from __future__ import annotations

import importlib.util
import os

from georesolve.providers import NoMatchError, ProviderError
from georesolve.providers.factory import create_provider
from georesolve.services import Resolver


def _optional_dependency_error(package_name: str):
    raise RuntimeError(
        f"Missing optional dependency: {package_name}. "
        f'Install the web extras with: python3 -m pip install -e ".[web]"'
    )


def _resolve_query_target(query: str | None, address: str | None) -> str:
    if query and address:
        raise ValueError("Provide either 'query' or 'address', not both.")
    target = query or address
    if target is None:
        raise ValueError("Provide either 'query' or 'address'.")
    return target


def create_app():
    if importlib.util.find_spec("fastapi") is None:
        _optional_dependency_error("fastapi")

    from fastapi import FastAPI, HTTPException, Query

    provider = create_provider(
        os.getenv("GEORESOLVE_PROVIDER", "census"),
        benchmark=os.getenv("GEORESOLVE_BENCHMARK", "Public_AR_Current"),
        vintage=os.getenv("GEORESOLVE_VINTAGE", "Current_Current"),
        timeout_seconds=float(os.getenv("GEORESOLVE_TIMEOUT_SECONDS", "15.0")),
    )
    resolver = Resolver(provider)
    app = FastAPI(title="georesolve API", version="0.3.0")

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "provider": provider.name,
            "benchmark": provider.config.benchmark,
            "vintage": provider.config.vintage,
        }

    @app.get("/resolve")
    def resolve(
        query: str | None = Query(None, min_length=1),
        address: str | None = Query(None, min_length=1),
    ):
        try:
            target = _resolve_query_target(query, address)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        try:
            return resolver.resolve(target).to_dict()
        except NoMatchError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except ProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc))

    @app.get("/resolve-current-location")
    def resolve_current_location(
        latitude: float = Query(..., ge=-90.0, le=90.0),
        longitude: float = Query(..., ge=-180.0, le=180.0),
    ):
        try:
            return resolver.resolve_current_location(latitude=latitude, longitude=longitude).to_dict()
        except NoMatchError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except ProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc))

    return app


def main():
    if importlib.util.find_spec("uvicorn") is None:
        _optional_dependency_error("uvicorn")

    import uvicorn

    uvicorn.run("georesolve.interfaces.api:create_app", factory=True, host="127.0.0.1", port=8080)


if __name__ == "__main__":  # pragma: no cover
    main()
