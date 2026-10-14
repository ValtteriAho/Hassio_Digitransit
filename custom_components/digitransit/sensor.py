"""Sensor platform for Digitransit integration."""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any, ClassVar

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import DigitransitCoordinator
from .const import (
    ATTR_ALERTS,
    ATTR_DELAY,
    ATTR_DEPARTURES,
    ATTR_DESTINATION,
    ATTR_ESTIMATED_TIME,
    ATTR_NEXT_DEPARTURE,
    ATTR_REALTIME,
    ATTR_ROUTE,
    ATTR_SCHEDULED_TIME,
    ATTR_STATUS,
    ATTR_STATUS_COLOR,
    ATTR_STATUS_ICON,
    ATTR_STOP_CODE,
    ATTR_VEHICLE_MODE,
    CONF_ALLOWED_ROUTES,
    CONF_STOPS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Digitransit sensors based on a config entry."""
    coordinator: DigitransitCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []
    for stop in entry.data.get(CONF_STOPS, []):
        entities.append(DigitransitSensor(coordinator, stop))
        entities.append(DigitransitNextThreeSensor(coordinator, stop))
        entities.append(DigitransitTimestampSensor(coordinator, stop))

    async_add_entities(entities)


class DigitransitBaseEntity(CoordinatorEntity[DigitransitCoordinator]):
    """Base entity for Digitransit stop sensors."""

    _attr_has_entity_name = True

    _STATUS_ICONS: ClassVar[dict[str, str]] = {
        "On time": "mdi:clock-check-outline",
        "Late": "mdi:clock-alert-outline",
        "Early": "mdi:clock-fast",
        "Scheduled": "mdi:clock-outline",
    }

    _STATUS_COLORS: ClassVar[dict[str, str]] = {
        "On time": "green",
        "Late": "red",
        "Early": "dodgerblue",
        "Scheduled": "gray",
    }

    _VEHICLE_ICONS: ClassVar[dict[str, str]] = {
        "BUS": "mdi:bus",
        "TRAM": "mdi:tram",
        "RAIL": "mdi:train",
        "SUBWAY": "mdi:subway-variant",
        "FERRY": "mdi:ferry",
    }

    def __init__(
        self,
        coordinator: DigitransitCoordinator,
        stop_config: dict[str, Any],
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._stop_id: str = stop_config["stop_id"]
        self._stop_name: str = stop_config["name"]
        self._num_departures: int = stop_config.get("num_departures", 5)
        self._router: str = stop_config.get("router", "waltti")

        # Parse allowed routes for filtering (e.g. "3, 4" or ["3", "4"])
        raw_routes = stop_config.get(CONF_ALLOWED_ROUTES)
        if isinstance(raw_routes, list):
            self._allowed_routes: set[str] | None = {
                str(r).strip() for r in raw_routes if str(r).strip()
            }
        elif isinstance(raw_routes, str) and raw_routes.strip():
            self._allowed_routes = {
                r.strip() for r in raw_routes.split(",") if r.strip()
            }
        else:
            self._allowed_routes = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device metadata grouping all sensors for this stop."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._stop_id)},
            manufacturer="Digitransit",
            model=f"Public Transit Stop ({self._get_vehicle_mode().capitalize()})",
            name=self._stop_name,
        )

    @property
    def available(self) -> bool:
        """Return whether entity has valid coordinator data."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._stop_id in self.coordinator.data
        )

    def _get_vehicle_mode(self) -> str:
        """Return primary vehicle mode for the stop (BUS, TRAM, RAIL, SUBWAY, FERRY)."""
        if not self.coordinator.data or self._stop_id not in self.coordinator.data:
            return "BUS"
        stop_data = self.coordinator.data[self._stop_id]
        return str(stop_data.get("vehicleMode") or "BUS").upper()

    def _get_alerts(self) -> list[dict[str, Any]]:
        """Return parsed disruption alerts for the stop."""
        if not self.coordinator.data or self._stop_id not in self.coordinator.data:
            return []
        stop_data = self.coordinator.data[self._stop_id]
        raw_alerts = stop_data.get("alerts") or []
        alerts: list[dict[str, Any]] = []
        for alert in raw_alerts:
            alerts.append(
                {
                    "header": alert.get("alertHeaderText") or "",
                    "description": alert.get("alertDescriptionText") or "",
                    "severity": alert.get("alertSeverityLevel") or "UNKNOWN",
                }
            )
        return alerts

    def _get_raw_departures(self) -> list[dict[str, Any]]:
        """Return raw departure items from coordinator data."""
        if not self.coordinator.data or self._stop_id not in self.coordinator.data:
            return []
        stop_data = self.coordinator.data[self._stop_id]
        return stop_data.get("stoptimesWithoutPatterns") or []

    def _process_departure(
        self, departure_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Process and validate a single departure dictionary."""
        try:
            trip = departure_data.get("trip") or {}
            route_info = trip.get("route") or {}
            route_short_name = str(route_info.get("shortName") or "?")

            # Apply route filtering if configured
            if (
                self._allowed_routes is not None
                and route_short_name not in self._allowed_routes
            ):
                return None

            service_day = departure_data.get("serviceDay", 0)
            scheduled = departure_data.get("scheduledDeparture", 0)
            realtime = departure_data.get("realtimeDeparture", scheduled)
            is_realtime = departure_data.get("realtime", False)

            scheduled_timestamp = service_day + scheduled
            realtime_timestamp = service_day + realtime

            # Use local time for display
            tz = dt_util.get_default_time_zone()
            scheduled_dt = datetime.fromtimestamp(scheduled_timestamp, tz=tz)
            realtime_dt = datetime.fromtimestamp(realtime_timestamp, tz=tz)

            now = dt_util.now()
            departure_time = realtime_dt if is_realtime else scheduled_dt
            seconds_to_departure = (departure_time - now).total_seconds()

            if 0 <= seconds_to_departure < 60:
                minutes = 0
            else:
                minutes = math.floor(seconds_to_departure / 60)

            # Calculate delay in minutes
            delay_seconds = realtime - scheduled
            delay_minutes = int(delay_seconds / 60)

            if not is_realtime:
                status = "Scheduled"
            elif delay_minutes > 0:
                status = f"Late by {delay_minutes} min"
            elif delay_minutes < 0:
                status = f"Early by {abs(delay_minutes)} min"
            else:
                status = "On time"

            if status.startswith("Late"):
                status_icon = self._STATUS_ICONS["Late"]
                status_color = self._STATUS_COLORS["Late"]
            elif status.startswith("Early"):
                status_icon = self._STATUS_ICONS["Early"]
                status_color = self._STATUS_COLORS["Early"]
            elif status == "On time":
                status_icon = self._STATUS_ICONS["On time"]
                status_color = self._STATUS_COLORS["On time"]
            else:
                status_icon = self._STATUS_ICONS["Scheduled"]
                status_color = self._STATUS_COLORS["Scheduled"]

            headsign = departure_data.get("headsign") or "Unknown"
            departure_timestamp = (
                realtime_timestamp if is_realtime else scheduled_timestamp
            )
            mode = str(route_info.get("mode") or self._get_vehicle_mode()).upper()

            return {
                ATTR_ROUTE: route_short_name,
                ATTR_DESTINATION: headsign,
                ATTR_SCHEDULED_TIME: scheduled_dt.strftime("%H:%M"),
                ATTR_ESTIMATED_TIME: realtime_dt.strftime("%H:%M"),
                "minutes": minutes,
                ATTR_REALTIME: is_realtime,
                ATTR_DELAY: delay_minutes if is_realtime else 0,
                ATTR_STATUS: status,
                ATTR_STATUS_ICON: status_icon,
                ATTR_STATUS_COLOR: status_color,
                "departure_time": departure_time.isoformat(),
                "departure_timestamp": departure_timestamp,
                "mode": mode,
            }
        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.debug("Error processing departure: %s", err)
            return None

    def _get_upcoming_departures(
        self,
        departures: list[dict[str, Any]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return processed upcoming departures sorted chronologically."""
        raw_items = departures if departures is not None else self._get_raw_departures()
        upcoming: list[dict[str, Any]] = []

        for item in raw_items:
            processed = self._process_departure(item)
            if processed and processed["minutes"] >= 0:
                upcoming.append(processed)

        upcoming.sort(key=lambda x: x.get("departure_timestamp", 0))
        if limit is not None:
            return upcoming[:limit]
        return upcoming

    def _get_next_departure(
        self,
        departures: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """Return the next upcoming departure."""
        upcoming = self._get_upcoming_departures(departures, limit=1)
        return upcoming[0] if upcoming else None

    def _format_departure(self, departure: dict[str, Any]) -> str:
        """Format departure for textual display."""
        route = departure[ATTR_ROUTE]
        destination = departure[ATTR_DESTINATION]
        time = departure.get(ATTR_ESTIMATED_TIME, departure[ATTR_SCHEDULED_TIME])
        minutes = departure["minutes"]
        is_realtime = departure.get(ATTR_REALTIME, False)
        delay = departure.get(ATTR_DELAY, 0)

        realtime_indicator = " 🔴" if is_realtime else ""
        delay_text = (
            f" (+{delay} min)" if delay > 0 else f" ({delay} min)" if delay < 0 else ""
        )

        if minutes < 0:
            return f"{route} → {destination} | {time} (past){realtime_indicator}"
        if minutes == 0:
            return f"{route} → {destination} | {time} (now){realtime_indicator}{delay_text}"
        return f"{route} → {destination} | {time} ({minutes} min){realtime_indicator}{delay_text}"


class DigitransitSensor(DigitransitBaseEntity, SensorEntity):
    """Representation of the main Digitransit bus stop sensor."""

    _attr_icon = "mdi:bus"

    def __init__(
        self,
        coordinator: DigitransitCoordinator,
        stop_config: dict[str, Any],
    ) -> None:
        """Initialize the primary departure sensor."""
        super().__init__(coordinator, stop_config)
        self._attr_unique_id = f"{DOMAIN}_{self._stop_id}_next_departure"
        self._attr_name = "Next departure"

    @property
    def native_value(self) -> str | None:
        """Return the relative duration string to the next departure."""
        next_departure = self._get_next_departure()
        if not next_departure:
            return None

        minutes = next_departure["minutes"]
        if minutes == 0:
            return "Now"
        if minutes == 1:
            return "1 min"
        return f"{minutes} min"

    @property
    def icon(self) -> str:
        """Return mode and status-based icon for the next departure."""
        mode = self._get_vehicle_mode()
        base_icon = self._VEHICLE_ICONS.get(mode, "mdi:bus")

        next_departure = self._get_next_departure()
        if not next_departure:
            return base_icon

        status = next_departure.get(ATTR_STATUS, "")
        if status.startswith("Late"):
            return self._STATUS_ICONS["Late"]
        if status.startswith("Early"):
            return self._STATUS_ICONS["Early"]

        return base_icon

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed departure attributes including alerts and mode."""
        if not self.coordinator.data or self._stop_id not in self.coordinator.data:
            return {}

        stop_data = self.coordinator.data[self._stop_id]
        raw_departures = stop_data.get("stoptimesWithoutPatterns") or []
        alerts = self._get_alerts()

        attributes: dict[str, Any] = {
            ATTR_STOP_CODE: stop_data.get("code", ""),
            "stop_id": self._stop_id,
            "stop_name": stop_data.get("name", self._stop_name),
            "router": self._router,
            ATTR_VEHICLE_MODE: self._get_vehicle_mode(),
            ATTR_ALERTS: alerts,
            "has_alerts": len(alerts) > 0,
        }

        upcoming = self._get_upcoming_departures(
            raw_departures, limit=self._num_departures
        )
        attributes[ATTR_DEPARTURES] = upcoming

        for idx, departure in enumerate(upcoming):
            attributes[f"lahto_{idx + 1}"] = self._format_departure(departure)

        if upcoming:
            attributes[ATTR_NEXT_DEPARTURE] = upcoming[0]

        return attributes


class DigitransitNextThreeSensor(DigitransitBaseEntity, SensorEntity):
    """Representation of next three departures in a compact pipe-separated string."""

    _attr_icon = "mdi:bus-clock"

    def __init__(
        self,
        coordinator: DigitransitCoordinator,
        stop_config: dict[str, Any],
    ) -> None:
        """Initialize the next three departures sensor."""
        super().__init__(coordinator, stop_config)
        self._attr_unique_id = f"{DOMAIN}_{self._stop_id}_next_three"
        self._attr_name = "Next 3 departures"

    @property
    def icon(self) -> str:
        """Return vehicle-specific clock icon."""
        mode = self._get_vehicle_mode()
        if mode == "RAIL":
            return "mdi:train-car"
        if mode == "TRAM":
            return "mdi:tram"
        return "mdi:bus-clock"

    @property
    def native_value(self) -> str | None:
        """Return compact text with the next three upcoming departure times."""
        upcoming = self._get_upcoming_departures(limit=3)
        if not upcoming:
            return "No departures"

        return " | ".join(
            dep.get(ATTR_ESTIMATED_TIME, dep[ATTR_SCHEDULED_TIME]) for dep in upcoming
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return attributes for next three departures."""
        if not self.coordinator.data or self._stop_id not in self.coordinator.data:
            return {}

        stop_data = self.coordinator.data[self._stop_id]
        upcoming = self._get_upcoming_departures(limit=3)
        alerts = self._get_alerts()

        attributes: dict[str, Any] = {
            ATTR_STOP_CODE: stop_data.get("code", ""),
            "stop_id": self._stop_id,
            "stop_name": stop_data.get("name", self._stop_name),
            "router": self._router,
            ATTR_VEHICLE_MODE: self._get_vehicle_mode(),
            ATTR_ALERTS: alerts,
            "has_alerts": len(alerts) > 0,
            ATTR_DEPARTURES: upcoming,
        }

        for idx, departure in enumerate(upcoming):
            attributes[f"departure_{idx + 1}"] = self._format_departure(departure)

        return attributes


class DigitransitTimestampSensor(DigitransitBaseEntity, SensorEntity):
    """Representation of the next upcoming departure as a native timestamp sensor."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-start"

    def __init__(
        self,
        coordinator: DigitransitCoordinator,
        stop_config: dict[str, Any],
    ) -> None:
        """Initialize the timestamp sensor."""
        super().__init__(coordinator, stop_config)
        self._attr_unique_id = f"{DOMAIN}_{self._stop_id}_next_departure_time"
        self._attr_name = "Next departure time"

    @property
    def native_value(self) -> datetime | None:
        """Return the next departure as a timezone-aware UTC datetime."""
        next_departure = self._get_next_departure()
        if not next_departure:
            return None

        timestamp = next_departure.get("departure_timestamp")
        if timestamp:
            return dt_util.utc_from_timestamp(timestamp)
        return None
