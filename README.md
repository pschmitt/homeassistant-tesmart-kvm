<p align="center">
  <img src="logo.png" width="128" alt="TESmart logo">
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/marketplace_repository/?owner=pschmitt&amp;repository=homeassistant-tesmart-kvm&amp;category=integration"><img src="https://my.home-assistant.io/badges/marketplace_repository.svg" alt="Open this integration in Home Assistant Marketplace"></a>
</p>

<h1 align="center">TESmart KVM for Home Assistant</h1>

<p align="center">Switch inputs and control settings on TESmart LAN HDMI KVMs over TCP.</p>

The integration speaks TESmart's hex protocol on port 5000 by default; it
does not need a separate shell client or extra dependencies.

## Features

- **Input selection:** Report the current input and switch between available inputs.
- **Device settings:** Control buzzer, input detection and LED timeout with optimistic state for write-only values.
- **Raw service:** Send a hex command and optionally read its response through `tesmart_kvm.send_raw`.
- **Device identity:** Resolve the switch's MAC from the local neighbor table when available; the protocol does not expose a serial or MAC query.

## Install

Use the Marketplace badge above on Home Assistant 2026.11 or later to add this
repository as a custom integration. On older versions, add it as a HACS
custom repository of type **Integration**. Install and restart Home Assistant.
The badge does not imply a public catalog listing. For manual installation,
copy `custom_components/tesmart_kvm/` into Home Assistant's
`custom_components/` directory and restart.

## Quick start

1. Add **TESmart KVM** under **Settings → Devices & services → Add integration**.
2. Enter the switch's host, port (default `5000`) and number of inputs.
3. Use its Input selector to switch between connected devices.

The integration polls the active input every 30 seconds by default; other
settings are write-only and restore the last value sent by Home Assistant.

## License

[GPL-3.0](LICENSE). TESmart logos belong to their respective owners and are
not relicensed under GPL.
