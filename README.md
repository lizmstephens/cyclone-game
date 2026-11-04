# Madagascar Cyclone Decision Game

## Play the games

- **`index.html` — Full-season training game:** Each new game randomly selects **2–7 storms** drawn without replacement from **94 usable WATTCH scenarios**, with a shared CHF 150,000 season budget, daily decision opportunities, forecast-track display, warehouse prepositioning/distribution restrictions, and Chef (boss) feedback. Players do not see the total number of storms or historical storm identities until the season ends.
- **`jokwe.html` — Approved single-storm Jokwe prototype:** Preserved separately, including its detailed daily RSMC-style forecast images and enlarged warehouse markers.

Open `index.html` locally in Chrome after downloading it; its 94-scenario dataset is embedded so no server is required. The repository is public and can be deployed with GitHub Pages.

## Training-game rules

- Decide daily: **Keep monitoring**, **Preposition Kits**, or **Distribute Kits**.
- Preposition costs CHF 20,000 per warehouse; the deadline depends on the chosen mode (Easy: 3+ days, Medium: 4+ days, Hard: 5+ days before the approximate event window).
- Distribute costs CHF 8,000 per stocked warehouse and is allowed from the end of the prepositioning window until the event (0 to fewer than 3/4/5 days remaining, by difficulty).
- Stock is storm-specific; the **budget, Chef happiness, and cumulative reach** are carried across the season.
- The season ends after its sampled 2–7 storms. The results screen reveals historical WATTCH storm names, years, geographic reference-track context and game outcomes. Select **New season** for another random selection.
- Warehouse markers start red, turn green when kits are prepositioned and darken when kits have been distributed.
- A fixed-coordinate Madagascar coastline replaces the earlier schematic outline; the map scale stays fixed rather than changing between forecast briefings.
- Players see fictional dates during a single **December–April 2026–27** training season. The historical forecast times remain internal for dataset interpolation and are revealed with the storm identities after the season.

## Source and limitations

`data/scenarios-100.json` holds 100 WATTCH archive selections, but six currently lack sufficient reference track or ensemble information for the integrated replay, so the playable version embeds **94 usable cases**.

The source cases include **one forecast initialization** for each scenario; they do not supply a real sequence of operational daily forecast updates. The integrated game therefore creates **training updates** by adjusting the archived ensemble against the reference track at each replay day. These updates are *illustrative constructs*, not genuine WATTCH forecasts issued on successive dates. The game now shows the track only, not an uncertainty cone. Forecast valid-time points interpolate latitude, longitude and native 10-m wind values from within a single archived forecast initialization. No independent daily forecast initializations are available in these 94 embedded scenarios; do not describe the training updates as genuine successive forecast runs. The storms are sampled from different historical years into **fictional training seasons**, not a real chronology.

The impact footprint (distance to selected warehouse locations), affected people, CHF costs, activation deadlines and Chef feedback are simplified gameplay assumptions and require review before the game can be used to assess real operational performance. Model 10-m wind speed values are treated as m/s for conversion to km/h, but the available embedded scenarios do not encode a wind-averaging period; never label these values as 1-minute or 10-minute sustained winds without source verification. IBTrACS preserves reporting-agency conventions (e.g. Réunion: 10-minute sustained, US: 1-minute sustained) and cannot be treated as homogenized. The map-derived reference-track crossing estimate is not a verified IBTrACS historical landfall observation. The embedded cases do not contain verified fatalities, damage or official landfall intensities; the season results intentionally mark these as unverified rather than fabricating them. Sources: https://zenodo.org/records/20446920 and https://www.ncei.noaa.gov/products/international-best-track-archive .

The original `js/seasons.js` exposes reusable `makeSeason()` and `loadCatalogue()` utilities if the game is modularized later.
