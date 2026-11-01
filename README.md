# Madagascar Cyclone Decision Game

A browser-based training game exploring cyclone forecast uncertainty and anticipatory action under a shared seasonal budget.

## Playable prototype
The current `index.html` runs a daily Cyclone Jokwe sequence from 25 February to 10 March 2008, showing RSMC-inspired forecast maps based on WATTCH hindcast ensembles, with intermediate days constructed between actual initialization dates.

The player chooses **Keep monitoring**, **Preposition Kits**, or **Distribute Kits**, subject to lead-time restrictions and availability of prepositioned stocks. The game tracks CHF expenditure, indicative beneficiaries and the **Chef (boss)**'s reactions.

Warehouse dots and location labels have been enlarged for readability.

## Scenario library and variable seasons — under development
- `data/scenarios-100.json`: 100 distinct Madagascar-relevant cases extracted from the user-provided WATTCH archives, including ensemble tracks, landfall records and reference tracks.
- `js/seasons.js`: `loadCatalogue()` and `makeSeason()` to select a **variable number of independent storms**, currently 2–7 (weighted counts of 10%, 20%, 25%, 20%, 15%, 10%).
- The sampler draws cases from different historical years to produce a **fictional training season**. They must not be described as a historically observed sequence of storms.
- The new sampler is not yet wired into the playable Jokwe HTML. A future step is transforming each selected ensemble forecast into its own day-by-day forecast briefing, then connecting seasons, scoring and budget persistence to the game.

## Scientific/data caveats
WATTCH trajectories are physically plausible hindcast ensembles, not necessarily the operational forecasts seen at the time. A 12-hour forecast-valid-time series from one initialization is not the same as updated daily forecasts. Daily update graphics between distinct initializations require explicit interpolation. WATTCH's `Wind` units and any exposure estimates should be checked against the metadata. Geographic warehouse locations and costs are placeholders pending verification.

## Hosting
The repository is private. GitHub Pages is not enabled. The current `index.html` embeds its forecast images so it can be downloaded and opened locally in a browser.
