"""Base entities for TESmart KVM."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_INPUTS, DEFAULT_INPUTS, DOMAIN
from .coordinator import TesmartDataUpdateCoordinator


class TesmartEntity(CoordinatorEntity[TesmartDataUpdateCoordinator]):
    """Base TESmart KVM entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TesmartDataUpdateCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        entry = self.coordinator.config_entry
        inputs = entry.data.get(CONF_INPUTS, DEFAULT_INPUTS)
        return DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="TESmart",
            model=f"{inputs}-port HDMI KVM switch",
        )
