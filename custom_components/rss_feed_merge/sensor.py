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
    """Groups the title and summary of every selected feed sensor by source."""

    _attr_name = "All News Feeds"
    _attr_icon = "mdi:newspaper-variant-multiple"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, feeds: list[str]) -> None:
        self._feeds = feeds
        self._attr_unique_id = f"{entry.entry_id}_all_news_feeds"
        self._attr_native_value = 0
        self._attr_extra_state_attributes = {"sources": []}

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
        sources: list[dict] = []
        total = 0
        for feed in self._feeds:
            state = self.hass.states.get(feed)
            entries = state.attributes.get("entries") if state else None
            if not entries or not isinstance(entries, list):
                _LOGGER.debug("Skipping %s - no entries found", feed)
                continue
            slim = [
                {"title": e.get("title", ""), "summary": e.get("summary", "")}
                for e in entries
                if isinstance(e, dict)
            ]
            sources.append(
                {
                    "name": state.attributes.get("friendly_name", feed),
                    "entity_id": feed,
                    "entries": slim,
                }
            )
            total += len(slim)
        self._attr_native_value = total
        self._attr_extra_state_attributes = {"sources": sources}
        _LOGGER.debug("Combined %s articles from %s feeds", total, len(sources))
