"""Config flow for TESmart KVM."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)

from .api import TesmartClient, TesmartError
from .const import (
    CONF_INPUTS,
    DEFAULT_INPUTS,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_INPUTS,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class TesmartConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TESmart KVM."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> TesmartOptionsFlow:
        """Return the options flow for this handler."""
        del config_entry
        return TesmartOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = int(user_input[CONF_PORT])
            client = TesmartClient(host=host, port=port)
            try:
                await client.async_get_input()
            except TesmartError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception(
                    "Unexpected exception while validating TESmart config"
                )
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                title = user_input.get(CONF_NAME) or "TESmart KVM"
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_INPUTS: int(user_input[CONF_INPUTS]),
                    },
                )

        defaults = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=defaults.get(CONF_HOST, "")
                    ): TextSelector(),
                    vol.Optional(
                        CONF_NAME, default=defaults.get(CONF_NAME, "TESmart KVM")
                    ): TextSelector(),
                    vol.Required(
                        CONF_PORT, default=defaults.get(CONF_PORT, DEFAULT_PORT)
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=1, max=65535, mode=NumberSelectorMode.BOX
                        )
                    ),
                    vol.Required(
                        CONF_INPUTS, default=defaults.get(CONF_INPUTS, DEFAULT_INPUTS)
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=2, max=MAX_INPUTS, mode=NumberSelectorMode.BOX, step=1
                        )
                    ),
                }
            ),
            errors=errors,
        )


class TesmartOptionsFlow(OptionsFlow):
    """Handle options for TESmart KVM."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage the TESmart KVM options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            mode=NumberSelectorMode.BOX,
                            step=1,
                        )
                    )
                }
            ),
        )
