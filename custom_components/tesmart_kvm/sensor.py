"""Sensors for TESmart KVM."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TesmartConfigEntry
from .coordinator import TesmartDataUpdateCoordinator
from .entity import TesmartEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: TesmartConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the TESmart KVM sensors."""
    del hass
    coordinator = config_entry.runtime_data.coordinator
    if coordinator.mac is None:
        return
    async_add_entities([TesmartMacSensor(coordinator)])


class TesmartMacSensor(TesmartEntity, SensorEntity):
    """MAC address of the switch (closest thing to a serial number)."""

    _attr_name = "MAC address"
    _attr_icon = "mdi:network"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TesmartDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "mac_address")

    @property
    def native_value(self) -> str | None:
        """Return the MAC address."""
        if self.coordinator.mac is None:
            return None
        return format_mac(self.coordinator.mac)
