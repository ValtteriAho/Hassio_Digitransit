"""Sensor platform for Digitransit integration."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_STOPS,
    ATTR_STOP_CODE,
    ATTR_DEPARTURES,
    ATTR_NEXT_DEPARTURE,
    ATTR_ROUTE,
    ATTR_DESTINATION,
    ATTR_SCHEDULED_TIME,
    ATTR_REALTIME,
    ATTR_DELAY,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Digitransit sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for stop in entry.data[CONF_STOPS]:
        entities.append(DigitransitSensor(coordinator, stop))
    
    async_add_entities(entities)


class DigitransitSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Digitransit bus stop sensor."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:bus"

    def __init__(self, coordinator, stop_config: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._stop_id = stop_config["stop_id"]
        self._stop_name = stop_config["name"]
        self._num_departures = stop_config.get("num_departures", 5)
        self._router = stop_config.get("router", "waltti")
        
        self._attr_unique_id = f"{DOMAIN}_{self._stop_id}"
        self._attr_name = self._stop_name

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or self._stop_id not in self.coordinator.data:
            return None
        
        stop_data = self.coordinator.data[self._stop_id]
        departures = stop_data.get("stoptimesWithoutPatterns", [])
        
        if not departures:
            return None
        
        # Get next departure
        next_departure = self._get_next_departure(departures)
        if next_departure:
            minutes = next_departure["minutes"]
            if minutes == 0:
                return "Now"
            elif minutes == 1:
                return "1 min"
            else:
                return f"{minutes} min"
        
        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device metadata so entities group in Home Assistant UI."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._stop_id)},
            manufacturer="Digitransit",
            model="Public Transit Stop",
            name=self._stop_name,
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        if not self.coordinator.data or self._stop_id not in self.coordinator.data:
            return {}
        
        stop_data = self.coordinator.data[self._stop_id]
        departures = stop_data.get("stoptimesWithoutPatterns", [])
        
        attributes = {
            ATTR_STOP_CODE: stop_data.get("code", ""),
            "stop_id": self._stop_id,
            "stop_name": stop_data.get("name", self._stop_name),
            "router": self._router,
        }
        
        # Process departures
        departure_list = []
        for idx, departure_data in enumerate(departures[:self._num_departures]):
            departure = self._process_departure(departure_data)
            if departure:
                departure_list.append(departure)
                # Add individual departure attributes (lahto_1, lahto_2, etc.)
                attributes[f"lahto_{idx + 1}"] = self._format_departure(departure)
        
        attributes[ATTR_DEPARTURES] = departure_list
        
        # Next departure info
        if departure_list:
            attributes[ATTR_NEXT_DEPARTURE] = departure_list[0]
        
        return attributes

    def _get_next_departure(self, departures: list) -> dict | None:
        """Get the next departure."""
        for departure_data in departures:
            departure = self._process_departure(departure_data)
            if departure and departure["minutes"] >= 0:
                return departure
        return None

    def _process_departure(self, departure_data: dict) -> dict | None:
        """Process a single departure."""
        try:
            service_day = departure_data.get("serviceDay", 0)
            scheduled = departure_data.get("scheduledDeparture", 0)
            realtime = departure_data.get("realtimeDeparture", scheduled)
            is_realtime = departure_data.get("realtime", False)
            
            # Calculate departure time
            departure_timestamp = service_day + realtime
            departure_time = datetime.fromtimestamp(departure_timestamp, tz=dt_util.DEFAULT_TIME_ZONE)
            now = dt_util.now()
            
            # Calculate minutes until departure
            time_diff = departure_time - now
            minutes = int(time_diff.total_seconds() / 60)
            
            # Calculate delay
            delay_seconds = realtime - scheduled
            delay_minutes = int(delay_seconds / 60)
            
            # Get route and destination info
            trip = departure_data.get("trip", {})
            route = trip.get("route", {})
            route_short_name = route.get("shortName", "?")
            headsign = departure_data.get("headsign", "Unknown")
            
            return {
                ATTR_ROUTE: route_short_name,
                ATTR_DESTINATION: headsign,
                ATTR_SCHEDULED_TIME: departure_time.strftime("%H:%M"),
                "minutes": minutes,
                ATTR_REALTIME: is_realtime,
                ATTR_DELAY: delay_minutes if is_realtime else 0,
                "departure_time": departure_time.isoformat(),
            }
            
        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.debug("Error processing departure: %s", err)
            return None

    def _format_departure(self, departure: dict) -> str:
        """Format departure for display."""
        route = departure[ATTR_ROUTE]
        destination = departure[ATTR_DESTINATION]
        time = departure[ATTR_SCHEDULED_TIME]
        minutes = departure["minutes"]
        is_realtime = departure[ATTR_REALTIME]
        delay = departure[ATTR_DELAY]
        
        # Format: "3 → Palosaari | 08:45 (12 min) 🔴"
        realtime_indicator = " 🔴" if is_realtime else ""
        delay_text = f" (+{delay} min)" if delay > 0 else f" ({delay} min)" if delay < 0 else ""
        
        if minutes < 0:
            return f"{route} → {destination} | {time} (past){realtime_indicator}"
        elif minutes == 0:
            return f"{route} → {destination} | {time} (now){realtime_indicator}{delay_text}"
        else:
            return f"{route} → {destination} | {time} ({minutes} min){realtime_indicator}{delay_text}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self._stop_id in self.coordinator.data