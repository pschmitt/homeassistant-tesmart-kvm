# TESmart KVM for Home Assistant

`tesmart_kvm` is a Home Assistant custom integration for
[TESmart](https://buytesmart.com/) HDMI KVM switches with a LAN port. It speaks the
vendor's simple hex protocol over TCP (port 5000 by default) — no extra dependencies,
no shell scripts.

## Features

- **Select**
  - `Input`: shows the currently active input and switches inputs
  - `LED timeout`: `never` / `10s` / `30s` (write-only setting, optimistic state)
- **Switches** (write-only settings, optimistic state)
  - `Buzzer`: beep on input change
  - `Input detection` (disabled by default)
- **Service**
  - `tesmart_kvm.send_raw`: send an arbitrary hex command (e.g. `aabb031000ee`) and
    optionally get the raw response back

## Installation

### HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=pschmitt&repository=homeassistant-tesmart-kvm&category=integration)

1. Click the badge above, or open HACS and add
   `https://github.com/pschmitt/homeassistant-tesmart-kvm` as a custom repository of
   type **Integration**.
2. Install **TESmart KVM**.
3. Restart Home Assistant.

### Manual

Copy `custom_components/tesmart_kvm` from this repository into your Home Assistant
`custom_components/tesmart_kvm` directory and restart.

## Configuration

The integration is configured from the Home Assistant UI:

1. Go to **Settings → Devices & services**.
2. Add **TESmart KVM**.
3. Enter the host, port (default `5000`) and the number of inputs of your switch.

## Notes

- The switch only reports the currently active input. Buzzer, LED timeout and input
  detection are write-only: the integration tracks the last value it sent
  (restored across restarts).
- The integration polls the active input every 30 seconds by default (configurable).

## Related

- [pschmitt/tesmart.sh](https://github.com/pschmitt/tesmart.sh) — the shell client this
  integration replaces

## License

GPL-3.0. TESmart and related marks belong to their respective owners.
