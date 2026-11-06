# Madagascar Cyclone Decision Game

## Play the games

- **`index.html` — Full-season training game:** Choose **one storm** or a **full season of 2–7 storms**, sampled from **94 usable WATTCH scenarios**, with a shared CHF 150,000 season budget, daily decision opportunities, forecast-track display, pre-activation/full-activation restrictions, and Chef (boss) feedback. Historical identities are hidden until each storm outcome screen; season players do not know the number of future storms.
- **`jokwe.html` — Approved single-storm Jokwe prototype:** Preserved separately, including its detailed daily RSMC-style forecast images and enlarged warehouse markers.

Play via GitHub Pages. The game loads its scenario and historical data as separate JSON files, so opening `index.html` directly from a local file may not work; use a local web server for offline development.

## Training-game rules

- Choose **Play one storm** or **Play a whole season** (2–7 randomly sampled storms). Difficulty controls the latest permitted pre-activation day: **Easy 3 days, Medium 4 days, Hard 5 days** before the modelled event. These are game constraints rather than official EAP deadlines.
- Three daily options: **Keep monitoring** (CHF 0); **Pre-activation** (CHF 20,000 per selected warehouse area, only with 3–7, 4–7, or 5–7 days remaining); and **Full activation** (CHF 8,000 per prepared area, within 0–3 days remaining). Full activation is impossible without pre-activation in that area.
- The real Madagascar cyclone EAP has a **pre-activation stage** when any DGM, RSMC La Réunion or ECMWF forecast indicates >50% probability of tropical-storm-strength landfall within 7 days, and **full activation** when DGM forecasts >118 km/h landfall within 48–72 hours. The game **does not have calibrated operational DGM warnings**, and uses a labelled illustrative ensemble-member fraction and wind indicator. Players can act without a simulated signal so that lucky decisions and defensible false alarms remain possible; the simulation judges decisions in context.
- No stop/reassessment action is implemented.
- Warehouse markers remain red until pre-activation, turn green when prepared, and dark green when fully activated. Stocks are storm-specific; CHF budget, Chef score and people reached carry across storms.
- Fictional dates are shown during play in December–April 2026–27; historical identity/date and the final feedback are revealed after each storm.
- Feedback is derived from **`data/feedback.json`**, a snapshot of the user-editable [Google Feedback Library](https://docs.google.com/spreadsheets/d/1kEIwFSZOG8nxThiheJkO-Tgtqn97HmlrawF9-gbB9FQ/edit), containing 20 objective outcomes (F01–F20) and 20 Boss variants (B01–B20). The objective row is assigned from the forecast, actual illustrative threshold, coverage, and spending, and the Boss row is selected separately so the Boss can react differently to the objective outcome.
- **Editing Google Sheets does not automatically refresh the website.** The current game serves the versioned JSON snapshot in GitHub; it must be re-exported after changes in Sheets. Some feedback rows describe circumstances not yet represented by the game's simplified mechanics, and are reserved for future use.

## Source and limitations

`data/scenarios-100.json` holds 100 WATTCH archive selections, but six currently lack sufficient reference track or ensemble information for the integrated replay, so the playable version loads **94 usable cases** from `data/scenarios.json`. Historical records are maintained separately in `data/historical.json`.

The source cases include **one forecast initialization** for each scenario; they do not supply a real sequence of operational daily forecast updates. The integrated game therefore creates **training updates** by adjusting the archived ensemble against the reference track at each replay day. These updates are *illustrative constructs*, not genuine WATTCH forecasts issued on successive dates. The game now shows the track only, not an uncertainty cone. Forecast valid-time points interpolate latitude, longitude and native 10-m wind values from within a single archived forecast initialization. No independent daily forecast initializations are available in these 94 scenarios; do not describe the training updates as genuine successive forecast runs. The storms are sampled from different historical years into **fictional training seasons**, not a real chronology.

The impact footprint (distance to selected warehouse locations), affected people, CHF costs, activation deadlines and Chef feedback are simplified gameplay assumptions and require review before the game can be used to assess real operational performance. Model 10-m wind speed values are treated as m/s for conversion to km/h, but the available embedded scenarios do not encode a wind-averaging period; never label these values as 1-minute or 10-minute sustained winds without source verification. IBTrACS preserves reporting-agency conventions (e.g. Réunion: 10-minute sustained, US: 1-minute sustained) and cannot be treated as homogenized. The map-derived reference-track crossing estimate is not a verified IBTrACS historical landfall observation. The embedded cases do not contain verified fatalities, damage or official landfall intensities; the season results intentionally mark these as unverified rather than fabricating them. Sources: https://zenodo.org/records/20446920 and https://www.ncei.noaa.gov/products/international-best-track-archive .

The original `js/seasons.js` exposes reusable `makeSeason()` and `loadCatalogue()` utilities if the game is modularized later.

## Verification (4 November 2026)

The updated embedded game script passed a JavaScript syntax check. In a DOM-mocked execution, 12 simulated season calculations (2–7 cyclones each) completed with finite latitudes, longitudes and wind estimates and rendered the final summary. An additional 15 full-season decision/advance-button simulations using **Keep monitoring** advanced correctly through 2–7 storms without getting stuck. These are automated logic checks; browser visual inspection and scenario-by-scenario historical verification remain outstanding.

Historical storm-name/impact enrichment has **not** been completed: all 94 embedded scenarios lack verified impact fields, agency-specific sustained-wind observations and a verified IBTrACS link. They show archive-based crossing estimates and links to source repositories, explicitly distinguished from observed historical landfall intensity. This is an important prerequisite before describing observed landfall winds or casualties in a public-facing version.

## Historical storm enrichment (4 November 2026)

The integrated game now includes sourced historical landfall/impact annotations for **13 of 94** scenarios, including Gafilo, Elita, Ivan, Bingiza, Giovanna, Haruna, Enawo, Ava, Belna, Batsirai, Freddy, Gamane and Chido. Historical deaths and damages are only included when supported by the linked reports, with source-specific date and geographic scope.

The summaries currently contain **10 source-checked RSMC La Réunion near-landfall 10-minute sustained-wind fixes** (in knots converted to km/h) for Elita, Gafilo, Ivan, Giovanna, Haruna, Enawo, Ava, Belna, Batsirai and Freddy. The best-track fixes are at discrete times and can be offshore or inland, rather than exact shoreline-crossing observations. Bingiza's Réunion wind field is missing at crossing, so its nearby JTWC 1-minute estimates remain a separately labelled note. No 1-minute/10-minute conversion is assumed. WATTCH's '10-m wind' describes height, *not* a 10-minute averaging period. Following these changes, 35 additional automated full-season decision-and-advance simulations completed without errors and no duplicate Dando was encountered. A further 45 full-season progressions (15 each for Easy, Medium and Hard) all completed, confirming the selected prepositioning deadlines were applied. Browser visual testing and the full 94-scenario impact verification are still outstanding.

## One-storm mode check (4 November 2026)

Added a start-page game-length selector to the existing `index.html`, leaving forecast generation, warehouse actions, and season progression shared. Automated DOM-mocked regression checks completed 90 games (15 per each combination of one storm/season and Easy/Medium/Hard) successfully, including the correct end-summary wording and single-storm termination. These are logic checks, not visual in-browser testing.

## EAP and feedback update (6 November 2026)

Retained the one-storm/season selector, fixed map and three difficulty options. Replaced the user-facing Preposition/Distribute options with Pre-activation/Full activation, with costed geographically targeted actions and no stop mechanism. Added separately rendered, spreadsheet-derived Objective Feedback and Chef feedback on every storm-completion card. The full 40-row feedback text snapshot is stored at `data/feedback.json` and includes source IDs. The wording remains editable in Google Sheets but is not live-synchronised. Current objective outcomes are illustrative because the simplified reference-track threshold and model ensemble approach probability are not operationally calibrated DGM warnings. Fixed an existing late-forecast null-median crash.

Automated DOM-mocked testing completed 72 playthroughs across the six combinations of game length and difficulty; the test runner exercised selecting Pre-activation, Full activation, budget carry-over and moving between storms, with no functional errors when respecting the current budget. This is not in-browser visual testing. Source of official EAP triggers: IFRC/CRM `MDRMG025 EAP Cyclone Summary`, dated 16 September 2025, page 3.
