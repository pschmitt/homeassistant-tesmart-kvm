"""Services for the TESmart KVM integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .api import TesmartError
from .const import ATTR_COMMAND, ATTR_DEVICE_ID, DOMAIN, SERVICE_SEND_RAW

SEND_RAW_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_COMMAND): cv.string,
        vol.Optional(ATTR_DEVICE_ID): cv.string,
    }
)


def _async_resolve_entry(hass: HomeAssistant, call: ServiceCall) -> ConfigEntry:
    """Resolve the targeted config entry from the service call."""
    entries = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.state is ConfigEntryState.LOADED
    ]
    if not entries:
        raise ServiceValidationError("No loaded TESmart KVM config entry found")

    device_id: str | None = call.data.get(ATTR_DEVICE_ID)
    if device_id is None:
        if len(entries) > 1:
            raise ServiceValidationError(
                "Multiple TESmart KVM devices are configured, please pass device_id"
            )
        return entries[0]

    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)
    if device is None:
        raise ServiceValidationError(f"Unknown device_id: {device_id}")
    for entry in entries:
        if entry.entry_id in device.config_entries:
            return entry
    raise ServiceValidationError(f"Device {device_id} is not a TESmart KVM device")


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the TESmart KVM services."""

    async def async_handle_send_raw(call: ServiceCall) -> ServiceResponse:
        """Send a raw hex command to the switch."""
        entry = _async_resolve_entry(hass, call)
        client = entry.runtime_data.client

        command = call.data[ATTR_COMMAND].replace(" ", "").replace("\\x", "")
        try:
            payload = bytes.fromhex(command)
        except ValueError as err:
            raise ServiceValidationError(f"Invalid hex command: {err}") from err

        try:
            response = await client.async_send_raw(payload)
        except TesmartError as err:
            raise HomeAssistantError(str(err)) from err

        if call.return_response:
            return {"response": response.hex()}
        return None

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_RAW,
        async_handle_send_raw,
        schema=SEND_RAW_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
