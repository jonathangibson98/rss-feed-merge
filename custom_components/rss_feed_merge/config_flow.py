"""Config flow for RSS Feed Merge."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_FEEDS, CONF_NAME, DEFAULT_NAME, DOMAIN


def _feeds_selector() -> selector.EntitySelector:
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", multiple=True)
    )


class RssFeedMergeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle setup. Run it as many times as you want, once per merge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            name = user_input[CONF_NAME].strip() or DEFAULT_NAME
            # One merge per name, so you can't accidentally make duplicates.
            await self.async_set_unique_id(name.lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=name,
                data={CONF_NAME: name, CONF_FEEDS: user_input[CONF_FEEDS]},
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_FEEDS, default=[]): _feeds_selector(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return RssFeedMergeOptionsFlow()


class RssFeedMergeOptionsFlow(config_entries.OptionsFlow):
    """Let you change the feed list for one merge later."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(
            CONF_FEEDS, self.config_entry.data.get(CONF_FEEDS, [])
        )
        schema = vol.Schema(
            {vol.Required(CONF_FEEDS, default=current): _feeds_selector()}
        )
        return self.async_show_form(step_id="init", data_schema=schema)
