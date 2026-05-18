"""Config flow for Digitransit integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_STOPS,
    CONF_STOP_ID,
    CONF_NUM_DEPARTURES,
    CONF_ROUTER,
    DEFAULT_NUM_DEPARTURES,
    API_ROUTERS,
    DEFAULT_ROUTER,
)

_LOGGER = logging.getLogger(__name__)


async def validate_api_key(hass: HomeAssistant, api_key: str) -> bool:
    """Validate the API key by making a test request."""
    session = async_get_clientsession(hass)
    headers = {
        "Content-Type": "application/json",
        "digitransit-subscription-key": api_key,
    }
    query = '{"query": "{ agencies { gtfsId name } }"}'
    
    try:
        # Use default router for validation
        base_url = API_ROUTERS[DEFAULT_ROUTER]
        async with session.post(
            base_url, data=query, headers=headers, timeout=10
        ) as response:
            if response.status == 200:
                data = await response.json()
                return "data" in data and "agencies" in data.get("data", {})
            return False
    except (aiohttp.ClientError, TimeoutError):
        return False


async def validate_stop_id(hass: HomeAssistant, api_key: str, stop_id: str) -> dict[str, str] | None:
    """Validate stop ID and return stop info."""
    session = async_get_clientsession(hass)
    headers = {
        "Content-Type": "application/json",
        "digitransit-subscription-key": api_key,
    }
    query = f'{{"query": "{{ stop(id: \\"{stop_id}\\") {{ name code gtfsId }} }}"}}'
    
    try:
        # Try with default router first (waltti)
        base_url = API_ROUTERS[DEFAULT_ROUTER]
        async with session.post(
            base_url, data=query, headers=headers, timeout=10
        ) as response:
            if response.status == 200:
                data = await response.json()
                stop = data.get("data", {}).get("stop")
                if stop:
                    return {
                        "name": stop.get("name", "Unknown"),
                        "code": stop.get("code", ""),
                        "gtfs_id": stop.get("gtfsId", stop_id),
                    }
            else:
                # If default router fails, try other routers
                for router_name, base_url in API_ROUTERS.items():
                    async with session.post(
                        base_url, data=query, headers=headers, timeout=10
                    ) as response2:
                        if response2.status == 200:
                            data = await response2.json()
                            stop = data.get("data", {}).get("stop")
                            if stop:
                                return {
                                    "name": stop.get("name", "Unknown"),
                                    "code": stop.get("code", ""),
                                    "gtfs_id": stop.get("gtfsId", stop_id),
                                }
    except (aiohttp.ClientError, TimeoutError):
        pass
    return None


class DigitransitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Digitransit."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.api_key: str | None = None
        self.stops: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            
            # Validate API key
            if await validate_api_key(self.hass, api_key):
                self.api_key = api_key
                return await self.async_step_stop()
            else:
                errors["base"] = "invalid_api_key"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    async def async_step_stop(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding a bus stop."""
        errors: dict[str, str] = {}

        if user_input is not None:
            stop_id = user_input[CONF_STOP_ID]
            
            # Validate stop ID
            stop_info = await validate_stop_id(self.hass, self.api_key, stop_id)
            
            if stop_info:
                # Add stop to list
                self.stops.append(
                    {
                        CONF_STOP_ID: stop_info["gtfs_id"],
                        CONF_NAME: stop_info["name"],
                        CONF_NUM_DEPARTURES: user_input.get(
                            CONF_NUM_DEPARTURES, DEFAULT_NUM_DEPARTURES
                        ),
                        CONF_ROUTER: user_input.get(CONF_ROUTER, "waltti"),
                    }
                )
                
                # Ask if user wants to add more stops
                return await self.async_step_add_another()
            else:
                errors["base"] = "invalid_stop_id"

        return self.async_show_form(
            step_id="stop",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STOP_ID): str,
                    vol.Optional(
                        CONF_NUM_DEPARTURES, default=DEFAULT_NUM_DEPARTURES
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                    vol.Optional(CONF_ROUTER, default=DEFAULT_ROUTER): vol.In(list(API_ROUTERS.keys())),
                }
            ),
            errors=errors,
            description_placeholders={
                "example": "Vaasa:159712 or Vaasa:302812"
            },
        )

    async def async_step_add_another(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask if user wants to add another stop."""
        if user_input is not None:
            if user_input.get("add_another"):
                return await self.async_step_stop()
            else:
                # Create the entry
                return self.async_create_entry(
                    title="Digitransit",
                    data={
                        CONF_API_KEY: self.api_key,
                        CONF_STOPS: self.stops,
                    },
                )

        return self.async_show_form(
            step_id="add_another",
            data_schema=vol.Schema(
                {
                    vol.Required("add_another", default=False): bool,
                }
            ),
            description_placeholders={
                "stops_added": str(len(self.stops))
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DigitransitOptionsFlow:
        """Get the options flow for this handler."""
        return DigitransitOptionsFlow(config_entry)


class DigitransitOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Digitransit."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NUM_DEPARTURES,
                        default=self.config_entry.options.get(
                            CONF_NUM_DEPARTURES, DEFAULT_NUM_DEPARTURES
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                }
            ),
        )