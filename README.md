# Madagascar Cyclone Decision Game

## Play the games

- **`index.html` — Full-season training game (new):** Each new game randomly selects **2–7 storms** drawn without replacement from **94 usable WATTCH scenarios**, with a shared CHF 150,000 season budget, daily decision opportunities, forecast-map envelope, warehouse prepositioning/distribution restrictions, and Chef (boss) feedback.
- **`jokwe.html` — Approved single-storm Jokwe prototype:** Preserved separately, including its detailed daily RSMC-style forecast images and enlarged warehouse markers.

Open `index.html` locally in Chrome after downloading it; its 94-scenario dataset is embedded so no server is required. The repository is private, so GitHub Pages is not currently available.

## Training-game rules

- Decide daily: **Keep monitoring**, **Preposition Kits**, or **Distribute Kits**.
- Preposition costs CHF 20,000 per warehouse and requires 4+ days remaining in the approximate event window.
- Distribute costs CHF 8,000 per stocked warehouse and requires 0–3 days remaining.
- Stock is storm-specific; the **budget, Chef happiness, and cumulative reach** are carried across the season.
- The season ends after its sampled 2–7 storms. Select **New season** for a new random selection.

## Source and limitations

`data/scenarios-100.json` holds 100 WATTCH archive selections, but six currently lack sufficient reference track or ensemble information for the integrated replay, so the playable version embeds **94 usable cases**.

The source cases include **one forecast initialization** for each scenario; they do not supply a real sequence of operational daily forecast updates. The integrated game therefore creates **training updates** by adjusting the archived ensemble against the reference track at each replay day. These updates are *illustrative constructs*, not genuine WATTCH forecasts issued on successive dates. The maps use an approximate positional uncertainty envelope and do not represent calibrated 75% probability of landfall. The storms are sampled from different historical years into **fictional training seasons**, not a real chronology.

The impact footprint (distance to selected warehouse locations), affected people, CHF costs, activation deadlines and Chef feedback are simplified gameplay assumptions and require review before the game can be used to assess real operational performance. Wind units are treated as m/s in the game and should be checked against source metadata before any scientific claims.

The original `js/seasons.js` exposes reusable `makeSeason()` and `loadCatalogue()` utilities if the game is modularized later.
