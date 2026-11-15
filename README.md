# Madagascar Cyclone Decision Game

## Play the games

- **`index.html` — Full-season training game:** Choose **one storm** or a **full season of 2–7 storms**, sampled from **86 named WATTCH scenarios**, with a shared CHF 150,000 season budget, daily decision opportunities, forecast-track display, pre-activation/full-activation restrictions, and Boss (boss) feedback. Historical identities are hidden until each storm outcome screen; season players do not know the number of future storms.
- **`jokwe.html` — Approved single-storm Jokwe prototype:** Preserved separately, including its detailed daily RSMC-style forecast images and enlarged warehouse markers.

Play via GitHub Pages. The game loads its scenario and historical data as separate JSON files, so opening `index.html` directly from a local file may not work; use a local web server for offline development.

## Training-game rules

- Choose **Play one storm** or **Play a whole season** (2–7 randomly sampled storms). Difficulty controls the latest permitted pre-activation day: **Easy 3 days, Medium 4 days, Hard 5 days** before the modelled event. These are game constraints rather than official EAP deadlines.
- Three daily options: **Keep monitoring** (CHF 0); **Pre-activation** (CHF 20,000 per selected warehouse area, only with 3–7, 4–7, or 5–7 days remaining); and **Full activation** (CHF 8,000 per prepared area, within 0–3 days remaining). Full activation is impossible without pre-activation in that area.
- The real Madagascar cyclone EAP has a **pre-activation stage** when any DGM, RSMC La Réunion or ECMWF forecast indicates >50% probability of tropical-storm-strength landfall within 7 days, and **full activation** when DGM forecasts >118 km/h landfall within 48–72 hours. The game **does not have calibrated operational DGM warnings**, and uses a labelled illustrative ensemble-member fraction and wind indicator. Players can act without a simulated signal so that lucky decisions and defensible false alarms remain possible; the simulation judges decisions in context.
- No stop/reassessment action is implemented.
- Warehouse markers remain red until pre-activation, turn green when prepared, and dark green when fully activated. Stocks are storm-specific; CHF budget, Boss score and people reached carry across storms.
- Fictional dates are shown during play in December–April 2026–27; historical identity/date and the final feedback are revealed after each storm.
- Feedback is derived from **`data/feedback.json`**, a snapshot of the user-editable [Google Feedback Library](https://docs.google.com/spreadsheets/d/1kEIwFSZOG8nxThiheJkO-Tgtqn97HmlrawF9-gbB9FQ/edit), containing 20 objective outcomes (F01–F20) and 20 Boss variants (B01–B20). The objective row is assigned from the forecast, actual illustrative threshold, coverage, and spending, and the Boss row is selected separately so the Boss can react differently to the objective outcome.
- **Editing Google Sheets does not automatically refresh the website.** The current game serves the versioned JSON snapshot in GitHub; it must be re-exported after changes in Sheets. Some feedback rows describe circumstances not yet represented by the game's simplified mechanics, and are reserved for future use.

## Source and limitations

`data/scenarios-100.json` holds 100 WATTCH archive selections, but six currently lack sufficient reference track or ensemble information for the integrated replay, so the playable version loads **94 usable cases** from `data/scenarios.json`. Historical records are maintained separately in `data/historical.json`.

The source cases include **one forecast initialization** for each scenario; they do not supply a real sequence of operational daily forecast updates. The integrated game therefore creates **training updates** by adjusting the archived ensemble against the reference track at each replay day. These updates are *illustrative constructs*, not genuine WATTCH forecasts issued on successive dates. The game now shows the track only, not an uncertainty cone. Forecast valid-time points interpolate latitude, longitude and native 10-m wind values from within a single archived forecast initialization. No independent daily forecast initializations are available in these 94 scenarios; do not describe the training updates as genuine successive forecast runs. The storms are sampled from different historical years into **fictional training seasons**, not a real chronology.

The impact footprint (distance to selected warehouse locations), affected people, CHF costs, activation deadlines and Boss feedback are simplified gameplay assumptions and require review before the game can be used to assess real operational performance. Model 10-m wind speed values are treated as m/s for conversion to km/h, but the available embedded scenarios do not encode a wind-averaging period; never label these values as 1-minute or 10-minute sustained winds without source verification. IBTrACS preserves reporting-agency conventions (e.g. Réunion: 10-minute sustained, US: 1-minute sustained) and cannot be treated as homogenized. The map-derived reference-track crossing estimate is not a verified IBTrACS historical landfall observation. The embedded cases do not contain verified fatalities, damage or official landfall intensities; the season results intentionally mark these as unverified rather than fabricating them. Sources: https://zenodo.org/records/20446920 and https://www.ncei.noaa.gov/products/international-best-track-archive .

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

Retained the one-storm/season selector, fixed map and three difficulty options. Replaced the user-facing Preposition/Distribute options with Pre-activation/Full activation, with costed geographically targeted actions and no stop mechanism. Added separately rendered, spreadsheet-derived Objective Feedback and Boss feedback on every storm-completion card. The full 40-row feedback text snapshot is stored at `data/feedback.json` and includes source IDs. The wording remains editable in Google Sheets but is not live-synchronised. Current objective outcomes are illustrative because the simplified reference-track threshold and model ensemble approach probability are not operationally calibrated DGM warnings. Fixed an existing late-forecast null-median crash.

Automated DOM-mocked testing completed 72 playthroughs across the six combinations of game length and difficulty; the test runner exercised selecting Pre-activation, Full activation, budget carry-over and moving between storms, with no functional errors when respecting the current budget. This is not in-browser visual testing. Source of official EAP triggers: IFRC/CRM `MDRMG025 EAP Cyclone Summary`, dated 16 September 2025, page 3.

## Editing the front page without code (6 November 2026)

The opening-screen wording is now stored in the **Front page** tab (gid `20261106`) of the [Feedback Library Google Sheet](https://docs.google.com/spreadsheets/d/1kEIwFSZOG8nxThiheJkO-Tgtqn97HmlrawF9-gbB9FQ/edit#gid=20261106). Edit only **column B**, leaving the stable identifiers in column A unchanged. The HTML retains exact fallback copy. The site attempts a read-only Google Sheets Visualization JSON request scoped to `Front page!A1:B24` at load time; a private or inaccessible tab leaves fallback wording intact and gameplay unaffected.

**One-time publication step (owner):** In Google Sheets choose **File → Share → Publish to web** and select *only* **Front page** in the individual-sheet dropdown. Do **not** publish the entire workbook: the other tabs contain the separate feedback library and Boss variants. Check the published content settings to verify the other tabs remain unpublished. Publishing makes the front-page text public and can take a few minutes to update. The spreadsheet's normal editor permissions need not be changed. These steps have not been performed automatically, and live browser retrieval has not been independently validated since the tab is not yet published.

This changes **copy only**, not difficulty timings, the EAP triggers, the season selection or gameplay. The existing `data/feedback.json` sheet snapshot remains a separate non-live import.

## About page and two-stage forecast verification (15 November 2026)

`about.html` is a standalone, linked explanation of the game's purpose, WATTCH archive (94 currently playable cases), approximate pseudo-daily updates, EAP triggers, review methodology and the difference between official EAP rules and simplified game decisions. It links to the official IFRC cyclone EAP summary at https://go-api.ifrc.org/api/downloadfile/94300/MDRMG025%20EAP%20Cyclone%20Summary . The start screen places **About the game** to the right of **Start game**, also linking from the gameplay footer. Extended forecast methodology was shortened in-game and moved to the explanatory page.

The review now classifies forecast predictions **separately** at the two thresholds. The pre-activation forecast is assessed from eligible issue dates 5–7 days before the modelled event, using the fraction of ensemble members predicting tropical-storm strength (>=63 km/h) near Madagascar; its reference-track outcome separately uses >=63 km/h. The full-activation forecast is assessed at 2–3 days and compared against the reference track exceeding 118 km/h. Each yields Correct warning, Correct non-warning, Overforecast, Underforecast or Not assessable (if no suitable forecast briefing was recorded). These are *model-reference comparisons*, not calibrated verification or observed meteorological warnings. The separate assessments appear under **Sources and detailed review** so the minimal Scientist/Boss speech-bubble design is preserved.

The existing F01–F20 objective feedback rows still use the game's simplified overall impact classification (full-activation threshold), and the Boss matching now uses the full-activation forecast classification rather than conflating it with the pre-activation forecast. Wording in Google Sheets may need further editorial review for some combinations. The current output reflects the stored feedback JSON snapshot, not live sheet edits.

DOM-mocked regression testing completed 48 full game playthroughs across the six combinations of storm/season and difficulty with no failures, and found both stage classifications available for every completed storm. This does not replace visual testing in a browser.

## Historical impacts catalogue integration (15 November 2026)

The storm-end one-sentence historical description now prioritises `data/verified_impacts.json`, a read-only exported snapshot of the [Madagascar Cyclone Game – Verified Storm Impacts spreadsheet](https://docs.google.com/spreadsheets/d/1gIZZ_wpC0yXadie5wqWFOBNfKdGN8dy6fH8qiOSIiWw/edit#gid=1464705366). The source spreadsheet has 94 WATTCH event-ID rows, 86 with non-empty Madagascar impact summaries; the playable scenario file has 86 named scenarios. The old `data/historical.json` supplies additional verified information and a fallback for records without a catalogue impact summary.

The corrected Cela (`2003_tr0034`) review reads: “Cela brought widespread rainfall to Madagascar, including 317 mm in 24 hours at Morombe.” Its source sheet records a near-Vohémar landfall in December 2003 but the exact date is marked as unconfirmed; the game does not invent one. A WATTCH reference track passing close to Madagascar is not grounds for overriding historical reported impacts.

**Maintenance:** Updates to the Google Sheet do not automatically update `data/verified_impacts.json` and require regeneration of that versioned snapshot. The original 13-record `data/historical.json` remains unchanged. Avoid changing scenario inclusion when correcting impact lookup.
