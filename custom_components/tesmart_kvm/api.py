"""Async TCP client for TESmart KVM switches.

Implements the simple hex protocol spoken by TESmart HDMI KVM switches on
TCP port 5000 (see the vendor manuals at
https://buytesmart.com/pages/support-manuals).
"""

from __future__ import annotations

import asyncio
import contextlib
import logging

_LOGGER = logging.getLogger(__name__)

CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 1.0
RETRY_DELAY = 0.2
DEFAULT_RETRIES = 10

GET_INPUT_COMMAND = bytes.fromhex("aabb031000ee")
GET_INPUT_RESPONSE_PREFIX = bytes.fromhex("aabb0311")


class TesmartError(Exception):
    """Base error for the TESmart client."""


class TesmartConnectionError(TesmartError):
    """Raised when the switch cannot be reached or does not answer."""


def _set_input_command(input_id: int) -> bytes:
    return bytes((0xAA, 0xBB, 0x03, 0x01, input_id, 0xEE))


def _set_buzzer_command(enabled: bool) -> bytes:
    return bytes((0xAA, 0xBB, 0x03, 0x02, int(enabled), 0xEE))


def _set_led_timeout_command(seconds: int) -> bytes:
    return bytes((0xAA, 0xBB, 0x03, 0x03, seconds, 0xEE))


def _set_input_detection_command(enabled: bool) -> bytes:
    return bytes((0xAA, 0xBB, 0x03, 0x81, int(enabled), 0xEE))


class TesmartClient:
    """Talk to a TESmart KVM switch over TCP."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize the client."""
        self.host = host
        self.port = port
        # The switch handles exactly one connection at a time
        self._lock = asyncio.Lock()

    async def _send_once(self, payload: bytes) -> bytes:
        """Open a connection, send the payload, and read the response."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=CONNECT_TIMEOUT,
            )
        except (TimeoutError, OSError) as err:
            raise TesmartConnectionError(
                f"Cannot connect to {self.host}:{self.port}: {err}"
            ) from err

        try:
            writer.write(payload)
            await asyncio.wait_for(writer.drain(), timeout=CONNECT_TIMEOUT)
            try:
                return await asyncio.wait_for(reader.read(64), timeout=READ_TIMEOUT)
            except TimeoutError:
                return b""
        except (TimeoutError, OSError) as err:
            raise TesmartConnectionError(
                f"I/O error talking to {self.host}:{self.port}: {err}"
            ) from err
        finally:
            writer.close()
            with contextlib.suppress(TimeoutError, OSError):
                await asyncio.wait_for(writer.wait_closed(), timeout=CONNECT_TIMEOUT)

    async def _send(
        self,
        payload: bytes,
        *,
        expect: bytes | None = None,
        retries: int = 1,
    ) -> bytes:
        """Send a command, optionally retrying until a valid response arrives."""
        async with self._lock:
            last_error: TesmartConnectionError | None = None
            for attempt in range(retries):
                if attempt:
                    await asyncio.sleep(RETRY_DELAY)
                try:
                    data = await self._send_once(payload)
                except TesmartConnectionError as err:
                    last_error = err
                    continue
                if expect is None:
                    return data
                if expect in data:
                    return data
            if last_error is not None:
                raise last_error
            raise TesmartConnectionError(
                f"No valid response from {self.host}:{self.port} "
                f"after {retries} attempt(s)"
            )

    async def async_get_input(self) -> int:
        """Return the currently active input (1-based)."""
        data = await self._send(
            GET_INPUT_COMMAND,
            expect=GET_INPUT_RESPONSE_PREFIX,
            retries=DEFAULT_RETRIES,
        )
        index = data.find(GET_INPUT_RESPONSE_PREFIX)
        offset = index + len(GET_INPUT_RESPONSE_PREFIX)
        if offset >= len(data):
            raise TesmartConnectionError(f"Truncated response: {data.hex()}")
        value = data[offset]
        # Quirk carried over from tesmart.sh: a stray 0x11 means input 1
        if value == 0x11:
            return 1
        return value + 1

    async def async_set_input(self, input_id: int) -> None:
        """Switch to the given input (1-based)."""
        await self._send(_set_input_command(input_id))

    async def async_set_buzzer(self, enabled: bool) -> None:
        """Enable or mute the buzzer."""
        await self._send(_set_buzzer_command(enabled))

    async def async_set_led_timeout(self, seconds: int) -> None:
        """Set the LED timeout (0, 10 or 30 seconds)."""
        await self._send(_set_led_timeout_command(seconds))

    async def async_set_input_detection(self, enabled: bool) -> None:
        """Enable or disable automatic input detection."""
        await self._send(_set_input_detection_command(enabled))

    async def async_send_raw(self, payload: bytes) -> bytes:
        """Send a raw command and return the raw response."""
        return await self._send(payload)
