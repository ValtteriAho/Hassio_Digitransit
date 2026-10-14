"""Unit tests for sensor departure formatting, vehicle modes, and alerts."""

import pytest

pytest.importorskip("homeassistant")

from custom_components.digitransit.const import (
    ATTR_DELAY,
    ATTR_DESTINATION,
    ATTR_ESTIMATED_TIME,
    ATTR_REALTIME,
    ATTR_ROUTE,
    ATTR_SCHEDULED_TIME,
    CONF_ALLOWED_ROUTES,
)
from custom_components.digitransit.sensor import (
    DigitransitSensor,
    DigitransitTimestampSensor,
)


class _DummyCoordinator:
    """Minimal coordinator stub for unit tests."""

    def __init__(self) -> None:
        self.data: dict = {}
        self.last_update_success: bool = True


def _make_sensor(allowed_routes: str = "") -> DigitransitSensor:
    config = {
        "stop_id": "Vaasa:159712",
        "name": "Test Stop",
        "num_departures": 5,
        "router": "waltti",
    }
    if allowed_routes:
        config[CONF_ALLOWED_ROUTES] = allowed_routes
    return DigitransitSensor(_DummyCoordinator(), config)


def test_format_departure_now_realtime_delay() -> None:
    sensor = _make_sensor()
    formatted = sensor._format_departure(
        {
            ATTR_ROUTE: "3",
            ATTR_DESTINATION: "Palosaari",
            ATTR_SCHEDULED_TIME: "08:45",
            ATTR_ESTIMATED_TIME: "08:45",
            "minutes": 0,
            ATTR_REALTIME: True,
            ATTR_DELAY: 2,
        }
    )

    assert formatted == "3 → Palosaari | 08:45 (now) 🔴 (+2 min)"


def test_format_departure_future_not_realtime() -> None:
    sensor = _make_sensor()
    formatted = sensor._format_departure(
        {
            ATTR_ROUTE: "4",
            ATTR_DESTINATION: "Keskusta",
            ATTR_SCHEDULED_TIME: "09:10",
            ATTR_ESTIMATED_TIME: "09:10",
            "minutes": 12,
            ATTR_REALTIME: False,
            ATTR_DELAY: 0,
        }
    )

    assert formatted == "4 → Keskusta | 09:10 (12 min)"


def test_format_departure_past() -> None:
    sensor = _make_sensor()
    formatted = sensor._format_departure(
        {
            ATTR_ROUTE: "1",
            ATTR_DESTINATION: "Tori",
            ATTR_SCHEDULED_TIME: "08:00",
            ATTR_ESTIMATED_TIME: "08:00",
            "minutes": -1,
            ATTR_REALTIME: False,
            ATTR_DELAY: 0,
        }
    )

    assert formatted == "1 → Tori | 08:00 (past)"


def test_route_filtering_allows_matching_route() -> None:
    sensor = _make_sensor(allowed_routes="3, 4")
    raw_departure = {
        "serviceDay": 1700000000,
        "scheduledDeparture": 3600,
        "realtimeDeparture": 3600,
        "realtime": False,
        "headsign": "Palosaari",
        "trip": {"route": {"shortName": "3"}},
    }
    processed = sensor._process_departure(raw_departure)
    assert processed is not None
    assert processed[ATTR_ROUTE] == "3"


def test_route_filtering_drops_non_matching_route() -> None:
    sensor = _make_sensor(allowed_routes="3, 4")
    raw_departure = {
        "serviceDay": 1700000000,
        "scheduledDeparture": 3600,
        "realtimeDeparture": 3600,
        "realtime": False,
        "headsign": "Vaskiluoto",
        "trip": {"route": {"shortName": "10"}},
    }
    processed = sensor._process_departure(raw_departure)
    assert processed is None


def test_timestamp_sensor_initialization() -> None:
    sensor = DigitransitTimestampSensor(
        _DummyCoordinator(),
        {
            "stop_id": "Vaasa:159712",
            "name": "Test Stop",
            "num_departures": 5,
            "router": "waltti",
        },
    )
    assert sensor.unique_id == "digitransit_Vaasa:159712_next_departure_time"
    assert sensor.name == "Next departure time"


def test_vehicle_mode_and_alerts() -> None:
    coord = _DummyCoordinator()
    coord.data = {
        "Vaasa:159712": {
            "vehicleMode": "TRAM",
            "alerts": [
                {
                    "alertHeaderText": "Delays expected",
                    "alertDescriptionText": "Track maintenance",
                    "alertSeverityLevel": "WARNING",
                }
            ],
            "stoptimesWithoutPatterns": [],
        }
    }
    sensor = DigitransitSensor(
        coord,
        {
            "stop_id": "Vaasa:159712",
            "name": "Test Stop",
            "num_departures": 5,
            "router": "waltti",
        },
    )
    assert sensor._get_vehicle_mode() == "TRAM"
    assert sensor.icon == "mdi:tram"
    alerts = sensor._get_alerts()
    assert len(alerts) == 1
    assert alerts[0]["header"] == "Delays expected"
    attrs = sensor.extra_state_attributes
    assert attrs["vehicle_mode"] == "TRAM"
    assert attrs["has_alerts"] is True
