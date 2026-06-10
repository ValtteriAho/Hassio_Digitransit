"""Unit tests for sensor departure formatting."""

import pytest

pytest.importorskip("homeassistant")

from custom_components.digitransit.const import (
    ATTR_DELAY,
    ATTR_DESTINATION,
    ATTR_REALTIME,
    ATTR_ROUTE,
    ATTR_SCHEDULED_TIME,
)
from custom_components.digitransit.sensor import DigitransitSensor


class _DummyCoordinator:
    """Minimal coordinator stub for unit tests."""

    data = {}


def _make_sensor() -> DigitransitSensor:
    return DigitransitSensor(
        _DummyCoordinator(),
        {
            "stop_id": "Vaasa:159712",
            "name": "Test Stop",
            "num_departures": 5,
            "router": "waltti",
        },
    )


def test_format_departure_now_realtime_delay() -> None:
    sensor = _make_sensor()
    formatted = sensor._format_departure(
        {
            ATTR_ROUTE: "3",
            ATTR_DESTINATION: "Palosaari",
            ATTR_SCHEDULED_TIME: "08:45",
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
            "minutes": 12,
            ATTR_REALTIME: False,
            ATTR_DELAY: 0,
        }
    )

    assert formatted == "4 → Keskusta | 09:10 (12 min)"
