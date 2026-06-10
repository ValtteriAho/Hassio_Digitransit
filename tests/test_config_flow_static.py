"""Static tests for Digitransit config-flow related behavior."""

import pytest

pytest.importorskip("homeassistant")

from custom_components.digitransit.const import API_ROUTERS, DEFAULT_ROUTER


def test_default_router_exists_in_mapping() -> None:
    """Ensure default router is always available."""
    assert DEFAULT_ROUTER in API_ROUTERS


def test_router_urls_use_expected_prefix() -> None:
    """Sanity-check configured API router URLs."""
    for url in API_ROUTERS.values():
        assert url.startswith("https://api.digitransit.fi/routing/v2/")
