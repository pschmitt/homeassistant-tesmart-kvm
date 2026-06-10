"""The TESmart KVM integration."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import TesmartClient
from .const import DEFAULT_PORT, PLATFORMS
from .coordinator import TesmartDataUpdateCoordinator
from .helpers import get_mac_address
from .services import async_setup_services

# Cap the first refresh: the client's connect-retry loop can take ~50s
# against an unreachable switch, well past HA's setup patience.
FIRST_REFRESH_TIMEOUT = 15


@dataclass
class TesmartRuntimeData:
    """Runtime data for a TESmart KVM config entry."""

    client: TesmartClient
    coordinator: TesmartDataUpdateCoordinator


type TesmartConfigEntry = ConfigEntry[TesmartRuntimeData]


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the TESmart KVM integration."""
    del config
    async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant, config_entry: TesmartConfigEntry
) -> bool:
    """Set up TESmart KVM from a config entry."""
    client = TesmartClient(
        host=config_entry.data[CONF_HOST],
        port=config_entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    coordinator = TesmartDataUpdateCoordinator(hass, config_entry, client)
    try:
        async with asyncio.timeout(FIRST_REFRESH_TIMEOUT):
            await coordinator.async_config_entry_first_refresh()
    except TimeoutError as err:
        raise ConfigEntryNotReady(
            f"Timeout connecting to {config_entry.data[CONF_HOST]}"
        ) from err

    # The first refresh just talked to the switch, so the neighbor table
    # should be fresh. Best effort: the switch has no MAC/serial query.
    coordinator.mac = await hass.async_add_executor_job(
        get_mac_address, config_entry.data[CONF_HOST]
    )

    config_entry.runtime_data = TesmartRuntimeData(
        client=client,
        coordinator=coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(
        config_entry.add_update_listener(async_update_listener)
    )
    return True


async def async_unload_entry(
    hass: HomeAssistant, config_entry: TesmartConfigEntry
) -> bool:
    """Unload a TESmart KVM config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def async_update_listener(
    hass: HomeAssistant, config_entry: TesmartConfigEntry
) -> None:
    """Reload the integration after options changes."""
    await hass.config_entries.async_reload(config_entry.entry_id)
