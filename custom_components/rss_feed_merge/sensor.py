"""Combined news feed sensor."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_FEEDS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    feeds = entry.options.get(CONF_FEEDS, entry.data.get(CONF_FEEDS, []))
    async_add_entities([AllNewsFeedsSensor(entry, feeds)])


class AllNewsFeedsSensor(SensorEntity):
    """Merges the 'entries' attribute of every selected feed sensor."""

    _attr_name = "All News Feeds"
    _attr_icon = "mdi:newspaper-variant-multiple"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, feeds: list[str]) -> None:
        self._feeds = feeds
        self._attr_unique_id = f"{entry.entry_id}_all_news_feeds"
        self._attr_native_value = 0
        self._attr_extra_state_attributes = {"entries": []}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_track_state_change_event(self.hass, self._feeds, self._feed_changed)
        )
        self._recalculate()

    @callback
    def _feed_changed(self, event) -> None:
        self._recalculate()
        self.async_write_ha_state()

    def _recalculate(self) -> None:
        all_entries: list = []
        for feed in self._feeds:
            state = self.hass.states.get(feed)
            entries = state.attributes.get("entries") if state else None
            if entries and isinstance(entries, list):
                all_entries.extend(entries)
            else:
                _LOGGER.debug("Skipping %s - no entries found", feed)
        self._attr_native_value = len(all_entries)
        self._attr_extra_state_attributes = {"entries": all_entries}
        _LOGGER.debug("Combined %s articles from %s feeds", len(all_entries), len(self._feeds))
