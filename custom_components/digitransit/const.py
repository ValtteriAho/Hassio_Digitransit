"""Constants for the Digitransit integration."""

from __future__ import annotations

DOMAIN = "digitransit"

CONF_API_KEY = "api_key"
CONF_STOPS = "stops"
CONF_STOP_ID = "stop_id"
CONF_NUM_DEPARTURES = "num_departures"
CONF_ROUTER = "router"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ALLOWED_ROUTES = "allowed_routes"

ATTR_STOP_CODE = "stop_code"
ATTR_DEPARTURES = "departures"
ATTR_NEXT_DEPARTURE = "next_departure"
ATTR_ROUTE = "route"
ATTR_DESTINATION = "destination"
ATTR_SCHEDULED_TIME = "scheduled_time"
ATTR_ESTIMATED_TIME = "estimated_time"
ATTR_REALTIME = "realtime"
ATTR_DELAY = "delay"
ATTR_STATUS = "status"
ATTR_STATUS_ICON = "status_icon"
ATTR_STATUS_COLOR = "status_color"
ATTR_ALERTS = "alerts"
ATTR_VEHICLE_MODE = "vehicle_mode"

DEFAULT_NUM_DEPARTURES = 5
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 15
MAX_SCAN_INTERVAL = 300

# Available routers for Digitransit API v2
API_ROUTERS = {
    "finland": "https://api.digitransit.fi/routing/v2/finland/gtfs/v1",
    "waltti": "https://api.digitransit.fi/routing/v2/waltti/gtfs/v1",
    "hsl": "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1",
    "varely": "https://api.digitransit.fi/routing/v2/varely/gtfs/v1",
    "tampere": "https://api.digitransit.fi/routing/v2/tampere/gtfs/v1",
    "turku": "https://api.digitransit.fi/routing/v2/turku/gtfs/v1",
    "jyvaskyla": "https://api.digitransit.fi/routing/v2/jyvaskyla/gtfs/v1",
    "oulu": "https://api.digitransit.fi/routing/v2/oulu/gtfs/v1",
    "lahti": "https://api.digitransit.fi/routing/v2/lahti/gtfs/v1",
}

DEFAULT_ROUTER = "waltti"
