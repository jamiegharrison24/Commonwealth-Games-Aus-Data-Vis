"""Adds the Games highlight to every chart that has a Games (year) in it.

Each chart gets two params, pickYear (0 = nothing picked) and pickLabel (e.g. "Perth 1962"),
which js/main.js sets on every chart when the reader clicks a Games link in the text. Run once from the repo root:
    python scripts/add_pick_games.py
Re-running is safe: charts that already have pickYear are skipped.
"""
import json
from pathlib import Path

SPECS = Path(__file__).resolve().parent.parent / 'js' / 'specs'
FONT = 'Libre Franklin, Helvetica Neue, Arial, sans-serif'
INK, WHITE = '#1d1d1b', '#ffffff'
PARAMS = [{"name": "pickYear", "value": 0}, {"name": "pickLabel", "value": ""}]
GAMES_CSV = {"url": "data/games.csv", "format": {"type": "csv", "parse": {"year": "number", "lat": "number", "lon": "number", "km_from_canberra": "number"}}}


def on(min_year=1900):
    return {"expr": f"pickYear >= {min_year} ? 1 : 0"}


def year_rule(color, min_year=1900, dummy=None):
    """Dashed vertical rule + label on a quantitative year axis."""
    # The filter matters: with nothing picked, a mark at pickYear = 0 sits far off the axis and
    # Vega's fit-x autosize then shrinks the whole chart to zero width. Filtering removes the mark.
    return {
        "data": {"values": [dummy or {}]},
        "transform": [{"filter": f"pickYear >= {min_year}"}],
        "layer": [
            {"mark": {"type": "rule", "strokeDash": [4, 3], "strokeWidth": 1.6},
             "encoding": {"x": {"datum": {"expr": "pickYear"}, "type": "quantitative"},
                          "y": {"value": 0}, "y2": {"value": {"expr": "height"}},
                          "color": {"value": color}, "opacity": {"value": on(min_year)},
                          "detail": None, "tooltip": None, "size": None, "strokeWidth": None}},
            # Label sits just above the plot (the spec gets 22px top padding so it isn't clipped) and
            # switches to left/right alignment near either end so it never runs off the chart.
            {"mark": {"type": "text", "baseline": "bottom", "dy": -4, "fontSize": 12.5, "fontWeight": 800, "font": FONT,
                      "align": {"expr": "scale('x', pickYear) < 70 ? 'left' : scale('x', pickYear) > width - 70 ? 'right' : 'center'"},
                      "dx": {"expr": "scale('x', pickYear) < 70 ? -3 : scale('x', pickYear) > width - 70 ? 3 : 0"}},
             "encoding": {"x": {"datum": {"expr": "pickYear"}, "type": "quantitative"},
                          "y": {"value": 0}, "text": {"value": {"expr": "pickLabel"}},
                          "color": {"value": color}, "opacity": {"value": on(min_year)},
                          "detail": None, "tooltip": None, "size": None}},
        ],
    }


def year_band(color, opacity, axis='x', min_year=1900, dummy=None, outline=False):
    """Highlight one band of an ordinal year axis (a column, or a row when axis='y')."""
    other = 'y' if axis == 'x' else 'x'
    mark = {"type": "rect"}
    enc = {axis: {"datum": {"expr": "pickYear"}, "type": "ordinal"},
           other: {"value": 0}, f"{other}2": {"value": {"expr": "height" if other == 'y' else "width"}},
           "opacity": {"value": {"expr": f"pickYear >= {min_year} ? 1 : 0"}}, "tooltip": None}
    if outline:
        mark.update(filled=False, strokeWidth=2.5, cornerRadius=2)
        enc["stroke"] = {"value": color}
        enc["color"] = {"value": color}
    else:
        mark.update(fill=color, fillOpacity=opacity)
        enc["color"] = {"value": color}
    return {"data": {"values": [dummy or {}]}, "mark": mark, "encoding": enc}


def ring(color, extra_filter='true', size=700, label=True):
    """Ring + label around the picked host city on a map (lon/lat)."""
    base = {"data": GAMES_CSV, "transform": [{"filter": f"datum.year == pickYear && ({extra_filter})"}]}
    layers = [{"mark": {"type": "circle", "filled": False, "stroke": color, "strokeWidth": 2.5, "size": size},
               "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"}}}]
    if label:
        layers.append({"mark": {"type": "text", "align": "left", "baseline": "top", "dx": 16, "dy": 14, "fontSize": 13, "fontWeight": 800, "font": FONT, "color": color},
                       "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                                    "text": {"field": "label"}}})
    return {**base, "layer": layers}


def load(name):
    return json.loads((SPECS / f'{name}.vg.json').read_text(encoding='utf-8'))


def save(name, spec):
    (SPECS / f'{name}.vg.json').write_text(json.dumps(spec, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def add(name, fn):
    s = load(name)
    if any(p.get('name') == 'pickYear' for p in s.get('params', [])):
        print('skip', name); return
    s['params'] = s.get('params', []) + PARAMS
    if name in ('03_rank_bump_chart', '04_athlete_vs_medal_share_gap', '09_athletics_strip_plot'):
        s['padding'] = {"top": 22, "left": 4, "right": 4, "bottom": 4}
    fn(s)
    s['description'] = s.get('description', '') + ' Games links in the text set pickYear/pickLabel to highlight that Games.'
    save(name, s); print('added', name)


# Only charts in chapters that have a Games link in the text get the highlight:
# ch1 host map, ch3 bump + gap, ch4 dumbbell, ch5 heatmap, ch7 strip + matrix + unit chart.
# ---- ch1 host map: ring around the host city (light) ----
add('01_host_cities_map', lambda s: s['layer'].append(ring(INK, size=900)))
# ---- ch3 bump + gap (light) ----
add('03_rank_bump_chart', lambda s: s['layer'].insert(0, year_rule(INK, dummy={"year": 0, "rank": 1, "nation": "", "group": "Other"})))
add('04_athlete_vs_medal_share_gap', lambda s: s['layer'].append(year_rule(INK, dummy={"year": 0})))


# ---- ch4 dumbbell: shade the row if the pick is a home Games (light) ----
def dumbbell(s):
    for panel in s['hconcat']:
        panel['layer'].insert(0, {"transform": [{"filter": "datum.home_year == pickYear"}],
                                  "mark": {"type": "rect", "fill": "#f0c13f", "fillOpacity": 0.35},
                                  "encoding": {"x": {"value": 0}, "x2": {"value": {"expr": "width"}}}})
add('05_home_advantage_dumbbell', dumbbell)
# ---- ch5 heatmap: outline the Games column (light) ----
add('06_sport_heatmap', lambda s: s['layer'].append(year_band(INK, 0, dummy={"year": 0, "sport_group": ""}, outline=True)))
# ---- ch7 strip plot, matrix, unit chart (dark; athletics comparison starts in 1970) ----
add('09_athletics_strip_plot', lambda s: s['layer'].append(year_rule(WHITE, min_year=1970)))


def matrix(s):
    sp = s['spec']
    inner = {"mark": sp.pop('mark'), "encoding": sp.pop('encoding')}
    band = year_band(WHITE, 0, min_year=1970, outline=True)
    band['encoding']['x']['scale'] = inner['encoding']['x']['scale']
    sp['encoding'] = {"x": inner['encoding'].pop('x')}
    sp['layer'] = [inner, band]
add('10_olympic_standard_matrix', matrix)
add('11_olympians_unit_chart', lambda s: s['layer'].insert(0, year_band('#f0c13f', 0.22, axis='y', min_year=1970, dummy={"cg_year": 0, "i": 0})))
