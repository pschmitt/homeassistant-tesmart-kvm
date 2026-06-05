"""Base entities for TESmart KVM."""

from __future__ import annotations

from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
    format_mac,
)
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
        connections: set[tuple[str, str]] = set()
        if self.coordinator.mac:
            connections.add(
                (CONNECTION_NETWORK_MAC, format_mac(self.coordinator.mac))
            )
        return DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            connections=connections,
            name=entry.title,
            manufacturer="TESmart",
            model=f"{inputs}-port HDMI KVM switch",
        )
