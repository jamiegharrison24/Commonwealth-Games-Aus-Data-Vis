# Data pipeline

These Python scripts collected and tidied the data in `../data/`. They were run once (29 September 2026) and are kept for transparency.

Run order:

1. `wget.py` — throttled downloader for Wikipedia page source (cached in `wiki/`).
2. `oly.py`, then `oly_fix.py` — download and parse Olympic athletics results (1968–2024) from Olympedia.
3. `cg_ath.py` — parse every Commonwealth Games athletics medallist and mark (1930–2026).
4. `aus_medalists.py` — parse Australian medallist lists for every Games.
5. `build_data.py` — medal tables, `games.csv`, Australian medals by sport, most decorated athletes.
6. `build_data2.py` — flow-map data, distance rings, per-capita data, map centroids.
7. `build_ath.py`, `build_stars.py`, `build_extra.py`, `build_waffle.py` — athletics comparison, Olympians-at-CG, home-advantage and waffle data.

Helper modules: `games.py` (list of Games), `parse_mt.py` (medal-table parser), `parse_sport.py` and `medalists2.py` (medals-by-sport parsers).

Paths inside the scripts point to the author's working folders and need adjusting to re-run.
