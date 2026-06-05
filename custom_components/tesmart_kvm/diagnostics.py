"""Diagnostics support for TESmart KVM."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import TesmartConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: TesmartConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    del hass
    coordinator = config_entry.runtime_data.coordinator

    return {
        "entry": {
            "title": config_entry.title,
            "data": dict(config_entry.data),
            "options": dict(config_entry.options),
        },
        "current_input": coordinator.data,
        "last_update_success": coordinator.last_update_success,
    }
