"""Golden regression baseline: deterministic chart snapshots for known births.

Writes/compares a JSON snapshot so pre-deployment vs post-deployment results
can be byte-compared. Run with `--record` to (re)write the baseline.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SNAP = Path(__file__).parent / "golden_baseline.json"

CASES = [
    # (name, y, m, d, h, min, lat, lon, tz)
    ("india_1947", 1947, 8, 15, 0, 0, 28.6139, 77.2090, "Asia/Kolkata"),
    ("sajal_2006", 2006, 3, 3, 18, 20, 17.385, 78.4867, "Asia/Kolkata"),
    ("user_2008", 2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata"),
    ("jobs_1955", 1955, 2, 24, 7, 15, 37.3382, -122.0312, "America/Los_Angeles"),
    ("vivekananda_1863", 1863, 1, 12, 6, 33, 22.5726, 88.3639, "Asia/Kolkata"),
]

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]


def snapshot():
    from astrology_engine import calculate_chart_with_object
    from dasha_engine import DashaEngine
    from datetime import datetime
    import pytz

    out = {}
    for name, y, m, d, h, mi, lat, lon, tz in CASES:
        chart_obj, chart_dict = calculate_chart_with_object(y, m, d, h, mi, lat, lon, tz)
        planets = {}
        for p in PLANETS:
            if p in chart_obj.planets:
                pl = chart_obj.planets[p]
                planets[p] = {
                    "sign": pl.sign,
                    "degree": round(pl.degree, 6),
                    "nakshatra": pl.nakshatra,
                    "pada": pl.nakshatra_pada,
                    "retrograde": bool(pl.retrograde),
                    "house": pl.house,
                }
        # dasha timeline head (deterministic from birth)
        utc = pytz.timezone(tz).localize(datetime(y, m, d, h, mi)).astimezone(pytz.utc).replace(tzinfo=None)
        moon = chart_obj.planets["Moon"]
        moon_lon = chart_obj.get_sign_index(moon.sign) * 30 + moon.degree
        tl = DashaEngine.calculate_vimshottari_timeline(utc, moon_lon, num_levels=3)
        md_heads = [(md["lord"], md["start"], md["end"]) for md in tl[:5]]
        out[name] = {
            "ascendant": {"sign": chart_obj.ascendant_sign, "degree": round(chart_obj.ascendant_degree, 6)},
            "planets": planets,
            "md_head": [[l, s, e] for (l, s, e) in md_heads],
        }
    return out


def main():
    record = "--record" in sys.argv
    snap = snapshot()
    if record or not SNAP.exists():
        SNAP.write_text(json.dumps(snap, indent=1, sort_keys=True))
        print(f"WROTE baseline: {SNAP} ({len(snap)} charts)")
        return 0
    base = json.loads(SNAP.read_text())
    diffs = []
    for name in base:
        if json.dumps(base[name], sort_keys=True) != json.dumps(snap.get(name), sort_keys=True):
            diffs.append(name)
    if diffs:
        print("GOLDEN MISMATCH:", diffs)
        for n in diffs:
            print("  base:", json.dumps(base[n], sort_keys=True)[:400])
            print("  now :", json.dumps(snap.get(n), sort_keys=True)[:400])
        return 1
    print(f"GOLDEN OK — {len(base)} charts byte-identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
