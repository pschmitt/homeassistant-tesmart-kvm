"""Data update coordinator for TESmart KVM."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TesmartClient, TesmartError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TesmartDataUpdateCoordinator(DataUpdateCoordinator[int]):
    """Poll the currently active input."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: TesmartClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config_entry.entry_id}",
            update_interval=timedelta(
                seconds=config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                )
            ),
        )
        self.config_entry = config_entry
        self.client = client
        # Discovered from the neighbor table after the first connection
        self.mac: str | None = None

    async def _async_update_data(self) -> int:
        """Fetch the currently active input."""
        try:
            return await self.client.async_get_input()
        except TesmartError as err:
            raise UpdateFailed(str(err)) from err
