# RSS Feed Merge

A Home Assistant custom integration that combines multiple RSS/news feed sensors into one.

Pick your feed sensors in the UI, name the merge, and you get a sensor (like `sensor.all_news_feeds`) holding every article from all of them. Want a separate one for sports, local news, tech? Run setup again and make as many merges as you want. It's built for dashboards, markdown cards, and AI/LLM automations that need one list of headlines instead of five.

This started life as an AppDaemon app and was rebuilt as a proper integration, so there's no AppDaemon dependency, no YAML to edit, and no restart needed to change your feeds.

## Features

- Set up and configured entirely from the UI (no YAML)
- **Add as many merges as you want**, each with its own name, feeds, and sensor
- Change your feed list anytime with **Configure**, and it reloads on its own
- Updates instantly whenever any source feed updates
- One sensor with the total article count as its state and the articles grouped by source in a `sources` attribute
- Keeps only each article's title and summary
- Skips any feed that's unavailable or has no entries instead of breaking

## Requirements

- Home Assistant 2024.8 or newer
- Source sensors that expose an `entries` attribute containing a list of articles (for example, sensors from the [Feedparser](https://github.com/custom-components/feedparser) custom integration)

## Installation

### HACS (custom repository)

1. In HACS, open the three-dot menu and choose **Custom repositories**.
2. Add `https://github.com/YOUR_USERNAME/rss-feed-merge` with category **Integration**.
3. Search for **RSS Feed Merge**, install it, and restart Home Assistant.

### Manual

1. Download this repo.
2. Copy the `custom_components/rss_feed_merge` folder into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant (a full restart, not a reload).

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **RSS Feed Merge**.
3. Give the merge a name (this becomes the sensor name) and select the feed sensors you want combined.
4. Want another merge? Repeat steps 1-3 with a different name.

To change the feeds for a merge later, open that entry and click **Configure**. To rename one, delete it and re-add it.

## What you get

| Entity | State | Attributes |
|---|---|---|
| `sensor.<your merge name>` (e.g. `sensor.all_news_feeds`, `sensor.sports_news`) | Total number of articles across that merge's feeds | `sources`: a list with one section per feed |

Each item in `sources` looks like this:

```yaml
sources:
  - name: WSPA            # the feed sensor's friendly name
    entity_id: sensor.wspa
    entries:
      - title: Headline here
        summary: Short summary here
```

Only the `title` and `summary` of each article are kept. Everything else (links, tags, images, authors) is dropped, which also keeps the sensor small.

Merge names must be unique. Each merge is its own entry, so you can edit or delete them independently.

## Example: markdown card

Each feed gets its own heading:

```yaml
type: markdown
content: >
  {% for s in state_attr('sensor.all_news_feeds', 'sources') or [] %}
  ## {{ s.name }}
  {% for e in s.entries[:5] %}
  **{{ e.title }}**

  {{ e.summary }}

  {% endfor %}
  {% endfor %}
```

## Good to know

- **Articles are not sorted or de-duplicated.** Each feed keeps its own order, and feeds appear in the order you selected them.
- **Recorder size limit.** Home Assistant won't store attributes over 16 KB in the database, and a lot of feeds can still go past that even with only titles and summaries. The sensor still works live, but you'd get a warning in the log. Excluding it from the recorder is cheap insurance and keeps your database lean:

  ```yaml
  recorder:
    exclude:
      entities:
        - sensor.all_news_feeds
        - sensor.sports_news   # add each merge sensor you create
  ```

  If you already have a `recorder:` section, add only the `exclude:` part under it.
- **Migrating from the AppDaemon app?** Remove or disable the old app before adding this integration, since both create `sensor.all_news_feeds`. Existing installs of this integration keep working as-is and keep their old sensor name.

## Troubleshooting

- **Integration doesn't appear in the Add Integration list:** Make sure the folder is named `rss_feed_merge` (underscores, not dashes) and that you did a full restart.
- **Sensor shows 0:** The selected sensors need an `entries` attribute with a list in it. Check them in Developer Tools → States.
- **Want more detail:** Add this to `configuration.yaml`, restart, and check the log:

  ```yaml
  logger:
    logs:
      custom_components.rss_feed_merge: debug
  ```

## Contributing

Bug reports and pull requests are welcome. Open an issue and include your Home Assistant version and any relevant log output.

## License

MIT (add a `LICENSE` file to match).
