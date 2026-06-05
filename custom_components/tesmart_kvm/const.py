"""Constants for the TESmart KVM integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "tesmart_kvm"
PLATFORMS: list[Platform] = [Platform.SELECT, Platform.SENSOR, Platform.SWITCH]

CONF_INPUTS = "inputs"

DEFAULT_PORT = 5000
DEFAULT_INPUTS = 8
MAX_INPUTS = 16
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 5

LED_TIMEOUT_NEVER = "never"
LED_TIMEOUT_10S = "10s"
LED_TIMEOUT_30S = "30s"
LED_TIMEOUT_OPTIONS: dict[str, int] = {
    LED_TIMEOUT_NEVER: 0,
    LED_TIMEOUT_10S: 10,
    LED_TIMEOUT_30S: 30,
}

SERVICE_SEND_RAW = "send_raw"
ATTR_COMMAND = "command"
ATTR_DEVICE_ID = "device_id"
