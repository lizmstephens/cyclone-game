# Madagascar Cyclone Decision Game

Interactive training prototype for anticipatory action decisions under uncertain cyclone forecasts.

## Current version
- Three actions: **Keep monitoring**, **Preposition kits**, **Distribute kits**.
- Shared budget in CHF, warehouse selections, and Secretary General responses.
- 11 WATTCH ensemble-member tracks for a Jokwe hindcast forecast initialized 4 March 2008 00 UTC.
- Madagascar geographic outline loaded dynamically from world-atlas; fallback included.
- Front-end code in `index.html`, `style.css`, and `js/game.js`.
- Forecast extract in `data/jokwe.json`.

## How to preview locally
Download or clone this repository, then run a local web server from its folder:

```bash
python -m http.server 8000
```

Open http://localhost:8000/ in your browser. Opening the HTML file directly may block loading its JSON data.

## Still to develop
- Convert the wider 100-case scenario library to compact per-case JSON.
- Integrate *successive* WATTCH forecast initializations; this prototype advances through the valid times of one initialization.
- Confirm actual warehouse locations from the implementation plan/photo.
- Add user-facing landfall and intensity probabilities, and estimated exposed populations.
- Develop scoring, interpretation of triggers, and realistic SG reactions.

Costs, population outcomes and warehouse coordinates are placeholders for game design, not operational data. No forecast probabilities or daily updated forecasts have been fabricated and labelled as WATTCH.

Repository is private; GitHub Pages publishing has not been enabled.
