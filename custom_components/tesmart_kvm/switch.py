"""Switches for TESmart KVM (write-only settings, hence optimistic)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import TesmartConfigEntry
from .api import TesmartError
from .coordinator import TesmartDataUpdateCoordinator
from .entity import TesmartEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: TesmartConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the TESmart KVM switches."""
    del hass
    coordinator = config_entry.runtime_data.coordinator
    async_add_entities(
        [
            TesmartBuzzerSwitch(coordinator),
            TesmartInputDetectionSwitch(coordinator),
        ]
    )


class TesmartOptimisticSwitch(TesmartEntity, SwitchEntity, RestoreEntity):
    """Base class for write-only switch settings."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_assumed_state = True

    def __init__(self, coordinator: TesmartDataUpdateCoordinator, key: str) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, key)
        self._attr_is_on = True

    async def async_added_to_hass(self) -> None:
        """Restore the last state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state in ("on", "off"):
            self._attr_is_on = last_state.state == "on"

    async def _async_apply(self, enabled: bool) -> None:
        """Send the setting to the switch."""
        raise NotImplementedError

    async def _async_set(self, enabled: bool) -> None:
        try:
            await self._async_apply(enabled)
        except TesmartError as err:
            raise HomeAssistantError(str(err)) from err
        self._attr_is_on = enabled
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the setting on."""
        del kwargs
        await self._async_set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the setting off."""
        del kwargs
        await self._async_set(False)


class TesmartBuzzerSwitch(TesmartOptimisticSwitch):
    """Buzzer (beep on input change)."""

    _attr_name = "Buzzer"
    _attr_icon = "mdi:volume-high"

    def __init__(self, coordinator: TesmartDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, "buzzer")

    async def _async_apply(self, enabled: bool) -> None:
        await self.coordinator.client.async_set_buzzer(enabled)


class TesmartInputDetectionSwitch(TesmartOptimisticSwitch):
    """Automatic input detection."""

    _attr_name = "Input detection"
    _attr_icon = "mdi:magnify-scan"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: TesmartDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, "input_detection")

    async def _async_apply(self, enabled: bool) -> None:
        await self.coordinator.client.async_set_input_detection(enabled)
