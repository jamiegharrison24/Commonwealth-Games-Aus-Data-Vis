# Top of the Table: Australia at the Commonwealth Games, 1930–2026

FIT3179 Data Visualisation 2 · Monash University · Semester 2, 2026 · Author: Jamie

**Live page:** https://<your-github-username>.github.io/<repo-name>/

A narrative web visualisation of how Australia came to dominate the Commonwealth Games, where its medals come from, who won them, and whether the Games have got easier. It includes 3 maps and 11 charts, all built with Vega-Lite 5, in a dark "stadium night" design with light chapters for the denser charts.

## Structure

| Path | Contents |
|---|---|
| `index.html` | The single-page story |
| `css/style.css` | Layout, typography and colour system |
| `js/main.js` | Embeds every chart with a shared theme |
| `js/specs/*.vg.json` | One readable Vega-Lite specification per chart |
| `data/` | Tidy CSV data used by the charts, plus TopoJSON/GeoJSON boundaries in `data/geo/` |
| `sketch/` | PDF of the hand-drawn A4 sketch |

## Charts and idioms

0. Every Australian medal: unit column chart (hero)
1. Host cities: proportional symbol map (Equal Earth) with region zoom buttons
2. Team travel: origin–destination flow map (azimuthal equidistant, centred on Canberra)
3. Medal-table rank: bump chart
4. Share of athletes vs share of medals: surplus/deficit (gap) line chart
5. Home advantage: dumbbell (range) charts
6. Medals by sport and Games: heatmap
7. All-time medals by sport: Marimekko chart
8. Most decorated Australians: timeline with nested proportional circles
9. Commonwealth vs Olympic winning marks: strip plot with median line
10. Olympic standard of Commonwealth champions: matrix (categorical heatmap)
11. Olympic medallists at the next Commonwealth Games: unit chart
12. Birmingham 2022 vs Glasgow 2026: waffle charts
13. Medals per million people: classed choropleth map (Equal Earth) with region zoom buttons and a 2022/2026 switch

## Data sources

- Commonwealth Games medal tables and Australian team records (Commonwealth Sport, compiled on Wikipedia); total athletes per Games from each Games’ Wikipedia infobox (1966 and 1970 totals include officials)
- Olympic athletics results 1968–2024 ([Olympedia](https://www.olympedia.org))
- Population 2024 (World Bank WDI; ONS mid-2024 for the UK nations)
- Boundaries: Natural Earth 1:50m map units

## Licence

Text and code: CC BY-SA 4.0. Natural Earth data is public domain.
