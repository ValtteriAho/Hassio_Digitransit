"""Static guardrail checks for config flow behavior.

These tests avoid Home Assistant runtime dependencies by validating
that key guardrail logic remains present in source code.
"""

from pathlib import Path


def _read_config_flow_source() -> str:
    root = Path(__file__).resolve().parents[1]
    path = root / "custom_components" / "digitransit" / "config_flow.py"
    return path.read_text(encoding="utf-8")


def test_duplicate_stop_error_is_defined_and_used() -> None:
    source = _read_config_flow_source()

    assert 'errors["base"] = "already_added_stop"' in source
    assert 'existing_entry.data.get(CONF_STOPS, [])' in source


def test_options_flow_updates_entry_data_and_options() -> None:
    source = _read_config_flow_source()

    assert "class DigitransitOptionsFlow(config_entries.OptionsFlowWithReload):" in source
    assert "self.hass.config_entries.async_update_entry(" in source
    assert "CONF_STOPS: stops" in source
    assert "options=user_input" in source
