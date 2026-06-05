"""Select entities for TESmart KVM."""

from __future__ import annotations

import asyncio

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import TesmartConfigEntry
from .api import TesmartError
from .const import CONF_INPUTS, DEFAULT_INPUTS, LED_TIMEOUT_NEVER, LED_TIMEOUT_OPTIONS
from .coordinator import TesmartDataUpdateCoordinator
from .entity import TesmartEntity

# Give the switch a moment to settle before confirming the new input
SET_INPUT_SETTLE_DELAY = 1.0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: TesmartConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the TESmart KVM selects."""
    del hass
    coordinator = config_entry.runtime_data.coordinator
    inputs = config_entry.data.get(CONF_INPUTS, DEFAULT_INPUTS)
    async_add_entities(
        [
            TesmartInputSelect(coordinator, inputs),
            TesmartLedTimeoutSelect(coordinator),
        ]
    )


class TesmartInputSelect(TesmartEntity, SelectEntity):
    """Currently active KVM input."""

    _attr_name = "Input"
    _attr_icon = "mdi:video-input-hdmi"

    def __init__(
        self,
        coordinator: TesmartDataUpdateCoordinator,
        inputs: int,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "input")
        self._attr_options = [str(i) for i in range(1, inputs + 1)]

    @property
    def current_option(self) -> str | None:
        """Return the currently active input."""
        current = self.coordinator.data
        if current is None or not 1 <= current <= len(self._attr_options):
            return None
        return str(current)

    async def async_select_option(self, option: str) -> None:
        """Switch to the given input."""
        try:
            await self.coordinator.client.async_set_input(int(option))
        except TesmartError as err:
            raise HomeAssistantError(str(err)) from err
        await asyncio.sleep(SET_INPUT_SETTLE_DELAY)
        await self.coordinator.async_request_refresh()


class TesmartLedTimeoutSelect(TesmartEntity, SelectEntity, RestoreEntity):
    """LED timeout setting (write-only, hence optimistic)."""

    _attr_name = "LED timeout"
    _attr_icon = "mdi:timer-outline"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_assumed_state = True
    _attr_options = list(LED_TIMEOUT_OPTIONS)

    def __init__(self, coordinator: TesmartDataUpdateCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "led_timeout")
        self._attr_current_option = LED_TIMEOUT_NEVER

    async def async_added_to_hass(self) -> None:
        """Restore the last selected option."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state in LED_TIMEOUT_OPTIONS:
            self._attr_current_option = last_state.state

    async def async_select_option(self, option: str) -> None:
        """Set the LED timeout."""
        try:
            await self.coordinator.client.async_set_led_timeout(
                LED_TIMEOUT_OPTIONS[option]
            )
        except TesmartError as err:
            raise HomeAssistantError(str(err)) from err
        self._attr_current_option = option
        self.async_write_ha_state()
