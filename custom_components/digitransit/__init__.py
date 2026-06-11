"""The Digitransit integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_STOPS,
    CONF_NUM_DEPARTURES,
    DEFAULT_NUM_DEPARTURES,
    DEFAULT_SCAN_INTERVAL,
    API_ROUTERS,
    DEFAULT_ROUTER,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Digitransit from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = DigitransitCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: DigitransitCoordinator | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        if coordinator is not None:
            await coordinator.async_shutdown()
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


class DigitransitCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Digitransit data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.api_key = entry.data[CONF_API_KEY]
        self.stops = entry.data[CONF_STOPS]
        self.default_num_departures = entry.options.get(
            CONF_NUM_DEPARTURES,
            DEFAULT_NUM_DEPARTURES,
        )
        self.session = async_get_clientsession(hass)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from API."""
        try:
            data = {}
            
            for stop in self.stops:
                stop_id = stop["stop_id"]
                num_departures = stop.get("num_departures", self.default_num_departures)
                router = stop.get("router", DEFAULT_ROUTER)
                
                stop_data = await self._fetch_stop_data(stop_id, num_departures, router)
                data[stop_id] = stop_data
            
            return data
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _fetch_stop_data(self, stop_id: str, num_departures: int, router: str = DEFAULT_ROUTER) -> dict:
        """Fetch data for a single stop."""
        headers = {
            "Content-Type": "application/json",
            "digitransit-subscription-key": self.api_key,
        }
        
        # Determine the API URL based on router
        api_url = API_ROUTERS.get(router, API_ROUTERS[DEFAULT_ROUTER])
        
        query = f'{{"query": "{{ stop(id: \\"{stop_id}\\") {{ name code gtfsId stoptimesWithoutPatterns(numberOfDepartures: {num_departures}) {{ scheduledDeparture realtimeDeparture realtime serviceDay headsign trip {{ route {{ shortName longName }} }} }} }} }}"}}'
        
        try:
            async with self.session.post(
                api_url,
                data=query,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", {}).get("stop", {})
                else:
                    _LOGGER.error(
                        "API returned status %s for stop %s",
                        response.status,
                        stop_id,
                    )
                    return {}
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.error("Error fetching data for stop %s: %s", stop_id, err)
            return {}

    async def async_shutdown(self) -> None:
        """Release coordinator resources."""
        if not self.session.closed:
            await self.session.close()