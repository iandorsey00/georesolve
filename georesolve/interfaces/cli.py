from __future__ import annotations

import argparse
import json
from typing import Any

from georesolve.providers import NoMatchError, ProviderError
from georesolve.providers.factory import SUPPORTED_PROVIDERS, create_provider
from georesolve.services import Resolver

EXIT_SUCCESS = 0
EXIT_PROVIDER_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_NO_MATCH = 3


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be 0 or greater")
    return parsed


def _add_provider_options(parser: argparse.ArgumentParser, provider_help: str):
    parser.add_argument(
        "--provider",
        default="census",
        choices=SUPPORTED_PROVIDERS,
        help=provider_help,
    )
    parser.add_argument(
        "--benchmark",
        default="Public_AR_Current",
        help="Census benchmark to use when the provider supports it",
    )
    parser.add_argument(
        "--vintage",
        default="Current_Current",
        help="Census vintage to use when the provider supports it",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=_positive_float,
        default=15.0,
        help="HTTP timeout for provider requests in seconds",
    )
    parser.add_argument(
        "--indent",
        type=_non_negative_int,
        default=2,
        help="JSON indentation level; use 0 for compact single-line output",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="georesolve",
        description="Resolve U.S. addresses, coordinates, and coordinate-bearing map URLs into geographies.",
        epilog=(
            "Examples:\n"
            '  georesolve resolve "4600 Silver Hill Rd, Washington, DC 20233"\n'
            '  georesolve resolve "38.8899, -77.0091"\n'
            '  georesolve resolve "https://www.google.com/maps/@38.8899,-77.0091,15z"\n'
            "  georesolve resolve-coordinates 38.8899 -77.0091"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True, title="commands")

    resolve_parser = subparsers.add_parser(
        "resolve",
        help="Resolve an address, lat/lon pair, or supported map URL into geographies",
        description="Resolve an address, a direct lat/lon pair, or a supported map URL with embedded coordinates.",
    )
    resolve_parser.add_argument(
        "query",
        help="Address, coordinate pair, or supported map URL to resolve",
    )
    _add_provider_options(resolve_parser, provider_help="Geocoding and geography provider")

    coordinates_parser = subparsers.add_parser(
        "resolve-coordinates",
        aliases=["resolve-current-location"],
        help="Resolve caller-supplied coordinates into geographies",
        description="Resolve explicit latitude and longitude values into geographies.",
    )
    coordinates_parser.add_argument("latitude", type=float, help="Latitude from the caller or device")
    coordinates_parser.add_argument("longitude", type=float, help="Longitude from the caller or device")
    _add_provider_options(coordinates_parser, provider_help="Geography provider")

    return parser


def _build_resolver(args: Any) -> Resolver:
    provider = create_provider(
        args.provider,
        benchmark=args.benchmark,
        vintage=args.vintage,
        timeout_seconds=args.timeout_seconds,
    )
    return Resolver(provider)


def _print_result(result: dict[str, Any], indent: int):
    print(json.dumps(result, indent=None if indent == 0 else indent, sort_keys=True))


def _exit_for_error(parser: argparse.ArgumentParser, exc: Exception):
    if isinstance(exc, NoMatchError):
        parser.exit(EXIT_NO_MATCH, f"No match: {exc}\n")
    if isinstance(exc, ProviderError):
        parser.exit(
            EXIT_PROVIDER_ERROR,
            f"Provider error: {exc}\n"
            "Try again later, or check --provider, --benchmark, and network access.\n",
        )
    parser.exit(EXIT_USAGE_ERROR, f"{exc}\n")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "resolve":
        resolver = _build_resolver(args)
        try:
            result = resolver.resolve(args.query)
        except (NoMatchError, ProviderError) as exc:
            _exit_for_error(parser, exc)

        _print_result(result.to_dict(), indent=args.indent)
        return EXIT_SUCCESS
    if args.command in {"resolve-coordinates", "resolve-current-location"}:
        resolver = _build_resolver(args)
        try:
            result = resolver.resolve_current_location(args.latitude, args.longitude)
        except (NoMatchError, ProviderError) as exc:
            _exit_for_error(parser, exc)

        _print_result(result.to_dict(), indent=args.indent)
        return EXIT_SUCCESS

    parser.exit(EXIT_USAGE_ERROR, "Unknown command\n")
    return EXIT_USAGE_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
