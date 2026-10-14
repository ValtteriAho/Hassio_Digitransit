"""The Digitransit integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ROUTERS,
    CONF_API_KEY,
    CONF_NUM_DEPARTURES,
    CONF_ROUTER,
    CONF_SCAN_INTERVAL,
    CONF_STOPS,
    DEFAULT_NUM_DEPARTURES,
    DEFAULT_ROUTER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.DIAGNOSTICS]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Digitransit from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = DigitransitCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry on options update."""
    await hass.config_entries.async_reload(entry.entry_id)


class DigitransitCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Digitransit data with batched GraphQL queries."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.api_key: str = entry.data[CONF_API_KEY]
        self.stops: list[dict[str, Any]] = entry.data.get(CONF_STOPS, [])
        self.default_num_departures: int = entry.options.get(
            CONF_NUM_DEPARTURES,
            DEFAULT_NUM_DEPARTURES,
        )
        scan_interval: int = entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API batching stops by router."""
        if not self.stops:
            return {}

        # Group stops by router for GraphQL batching
        stops_by_router: dict[str, list[dict[str, Any]]] = {}
        for stop in self.stops:
            router = stop.get(CONF_ROUTER, DEFAULT_ROUTER)
            stops_by_router.setdefault(router, []).append(stop)

        tasks = [
            self._fetch_router_batch(router, router_stops)
            for router, router_stops in stops_by_router.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        data: dict[str, Any] = dict(self.data) if self.data else {}
        success_count = 0

        for result in results:
            if isinstance(result, Exception):
                _LOGGER.warning("Error fetching router batch: %s", result)
            elif isinstance(result, dict):
                for stop_id, stop_data in result.items():
                    if stop_data:
                        data[stop_id] = stop_data
                        success_count += 1

        # If every stop failed and we have no prior cached data, raise UpdateFailed
        if success_count == 0 and not self.data:
            raise UpdateFailed("Failed to fetch data for any configured stop")

        return data

    async def _fetch_router_batch(
        self,
        router: str,
        stops: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Fetch multiple stops on the same router in a single batched GraphQL query."""
        api_url = API_ROUTERS.get(router, API_ROUTERS[DEFAULT_ROUTER])
        headers = {
            "Content-Type": "application/json",
            "digitransit-subscription-key": self.api_key,
        }

        query, variables = self._build_batch_query(stops)
        payload = {"query": query, "variables": variables}

        try:
            async with self.session.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    errors = result.get("errors")
                    if errors:
                        _LOGGER.warning(
                            "GraphQL errors for router %s: %s", router, errors
                        )
                    res_data = result.get("data") or {}
                    batch_result: dict[str, Any] = {}
                    for idx, stop in enumerate(stops):
                        alias = f"stop_{idx}"
                        batch_result[stop["stop_id"]] = res_data.get(alias) or {}
                    return batch_result

                _LOGGER.error(
                    "API returned HTTP %s for router %s",
                    response.status,
                    router,
                )
                return {}
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.error("Network error fetching router %s: %s", router, err)
            return {}

    def _build_batch_query(
        self,
        stops: list[dict[str, Any]],
    ) -> tuple[str, dict[str, Any]]:
        """Construct batched GraphQL query with aliases and variables."""
        parts: list[str] = []
        variables: dict[str, Any] = {}

        for idx, stop in enumerate(stops):
            stop_id = stop["stop_id"]
            num_departures = stop.get("num_departures", self.default_num_departures)
            alias = f"stop_{idx}"
            var_id = f"id_{idx}"
            var_num = f"num_{idx}"

            variables[var_id] = stop_id
            variables[var_num] = num_departures

            parts.append(
                f"""  {alias}: stop(id: ${var_id}) {{
    name
    code
    gtfsId
    vehicleMode
    alerts {{
      alertSeverityLevel
      alertHeaderText
      alertDescriptionText
    }}
    stoptimesWithoutPatterns(numberOfDepartures: ${var_num}) {{
      scheduledDeparture
      realtimeDeparture
      realtime
      serviceDay
      headsign
      trip {{
        route {{
          shortName
          longName
          mode
        }}
      }}
    }}
  }}"""
            )

        var_defs = ", ".join(
            f"${k}: String!" if k.startswith("id_") else f"${k}: Int!"
            for k in variables
        )
        query = f"query GetBatchStops({var_defs}) {{\n" + "\n".join(parts) + "\n}"
        return query, variables
