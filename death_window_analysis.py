"""
DEATH-WINDOW ANALYSIS (unconstrained mode) — all charts in the corpus.
Method (strict classical, deterministic):
  1. Jaimini 3-Pair Ayurdaya bracket + Kakshya Vriddhi/Hrasa (longevity_engine.py)
  2. Maraka identification: 2nd/7th lords, Badhaka lord, 8th lord,
     occupants of houses 2/7/8 (BPHS Ch. 44-46)
  3. Vimshottari D-A-P scan INSIDE the longevity bracket: death windows =
     periods where >=2 of {MD, AD, PD} are Maraka lords (double-maraka),
     or Maraka MD + secondary significator AD, etc.
  4. Ranked by maraka convergence strength.
Track B: bracket + window mechanics are exact math; death-DATE skill is
UNMEASURED at exact-day level (celebrity layer below shows real hits and misses).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import datetime, pytz
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from longevity_engine import LongevityEngine

CHARTS = {
    "YOU (2008-08-01)":      {"b": (2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata"), "status": "alive"},
    "HER (2008-04-05)":      {"b": (2008, 4, 5, 6, 15, 50.348, 18.916, "Europe/Warsaw"), "status": "alive"},
    "BROTHER (2003-06-05)":  {"b": (2003, 6, 5, 17, 45, 17.6868, 83.2185, "Asia/Kolkata"), "status": "alive"},
    "FATHER (1975-05-06)":   {"b": (1975, 5, 6, 7, 15, 16.8667, 81.9333, "Asia/Kolkata"), "status": "alive"},
    "MOTHER (1980-10-01)":   {"b": (1980, 10, 1, 20, 25, 16.8667, 81.9333, "Asia/Kolkata"), "status": "alive"},
    "STEVE JOBS":            {"b": (1955, 2, 24, 19, 15, 37.7749, -122.4194, "America/Los_Angeles"), "died": "2011-10-05"},
    "EINSTEIN":              {"b": (1879, 3, 14, 11, 30, 48.4011, 9.9876, "Europe/Berlin"), "died": "1955-04-18"},
    "PRINCESS DIANA":        {"b": (1961, 7, 1, 19, 45, 52.83, 0.50, "Europe/London"), "died": "1997-08-31"},
    "WALT DISNEY":           {"b": (1901, 12, 5, 0, 35, 41.8781, -87.6298, "America/Chicago"), "died": "1966-12-15"},
    "ELON MUSK":             {"b": (1971, 6, 28, 7, 30, -25.7479, 28.2293, "Africa/Johannesburg"), "status": "alive"},
    "DONALD TRUMP":          {"b": (1946, 6, 14, 10, 54, 40.7282, -73.7949, "America/New_York"), "status": "alive"},
    "BARACK OBAMA":          {"b": (1961, 8, 4, 19, 24, 21.3069, -157.8583, "Pacific/Honolulu"), "status": "alive"},
    "AMITABH BACHCHAN":      {"b": (1942, 10, 11, 16, 0, 25.4358, 81.8463, "Asia/Kolkata"), "status": "alive"},
    "TIGER WOODS":           {"b": (1975, 12, 30, 22, 50, 33.7879, -117.8531, "America/Los_Angeles"), "status": "alive"},
}

BRACKET_AGES = {"Alpayu": (0, 33), "Madhyayu": (33, 66), "Deerghayu": (66, 105)}
LORDS = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun",
         "Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
         "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
ZOD = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def _to_dt(s):
    d = datetime.datetime.fromisoformat(s)
    return pytz.utc.localize(d) if d.tzinfo is None else d.astimezone(pytz.utc)

def analyze(name, info):
    y, m, d, h, mi, lat, lon, tz = info["b"]
    chart, _ = calculate_chart_with_object(y, m, d, h, mi, lat, lon, tz, name=name)
    birth_utc = pytz.utc.localize(datetime.datetime(y, m, d, h, mi))  # caller passes local wall time; engine handles tz internally
    # engine expects local time + tz; recompute UTC properly:
    import zoneinfo
    try:
        local = datetime.datetime(y, m, d, h, mi)
        birth_utc = local.replace(tzinfo=zoneinfo.ZoneInfo(tz)).astimezone(pytz.utc)
    except Exception:
        pass

    lon_ = LongevityEngine.calculate_jaimini_3_pairs(chart)
    mar = LongevityEngine.identify_marakas(chart)
    bracket = lon_["final_adjusted_category"]
    lo_age, hi_age = BRACKET_AGES[bracket]

    asc_idx = ZOD.index(chart.ascendant_sign)
    h2_lord = LORDS[ZOD[(asc_idx + 1) % 12]]
    h7_lord = LORDS[ZOD[(asc_idx + 6) % 12]]
    h8_lord = LORDS[ZOD[(asc_idx + 7) % 12]]
    modality = {"Aries":"Movable","Taurus":"Fixed","Gemini":"Dual","Cancer":"Movable","Leo":"Fixed","Virgo":"Dual",
                "Libra":"Movable","Scorpio":"Fixed","Sagittarius":"Dual","Capricorn":"Movable","Aquarius":"Fixed","Pisces":"Dual"}[chart.ascendant_sign]
    badhaka_h = 11 if modality == "Movable" else (9 if modality == "Fixed" else 7)
    badhaka_lord = LORDS[ZOD[(asc_idx + badhaka_h - 1) % 12]]
    occ = {h: [n for n, p in chart.planets.items() if getattr(p, "house", None) == h] for h in (2, 7, 8)}
    secondary = {h8_lord, badhaka_lord} | set(occ[2]) | set(occ[7]) | set(occ[8])
    maraka = {h2_lord, h7_lord}

    moon = chart.planets["Moon"]
    moon_lon = ZOD.index(moon.sign) * 30.0 + moon.degree
    tl = DashaEngine.calculate_vimshottari_timeline(birth_utc, moon_lon, num_levels=3)

    win_lo = birth_utc + datetime.timedelta(days=lo_age * 365.25)
    win_hi = birth_utc + datetime.timedelta(days=hi_age * 365.25)

    results = []
    for md in tl:
        md_s, md_e = _to_dt(md["start"]), _to_dt(md["end"])
        if md_e < win_lo or md_s > win_hi:
            continue
        for ad in md.get("sub_periods", []):
            ad_s, ad_e = _to_dt(ad["start"]), _to_dt(ad["end"])
            if ad_e < win_lo or ad_s > win_hi:
                continue
            for pd in ad.get("sub_periods", []):
                pd_s, pd_e = _to_dt(pd["start"]), _to_dt(pd["end"])
                if pd_e < win_lo or pd_s > win_hi:
                    continue
                triad = [md["lord"], ad["lord"], pd["lord"]]
                n_maraka = sum(1 for t in triad if t in maraka)
                n_sec = sum(1 for t in triad if t in secondary and t not in maraka)
                strength = n_maraka * 1.0 + n_sec * 0.5
                if n_maraka >= 2 or (n_maraka >= 1 and n_sec >= 1 and triad[0] in maraka):
                    results.append({
                        "start": max(pd_s, win_lo), "end": min(pd_e, win_hi),
                        "triad": " -> ".join(triad), "strength": strength,
                        "n_maraka": n_maraka, "n_secondary": n_sec,
                        "md_maraka": triad[0] in maraka,
                    })

    results.sort(key=lambda r: (-r["strength"], r["start"]))
    return chart, lon_, mar, (h2_lord, h7_lord, h8_lord, badhaka_lord, occ), bracket, (lo_age, hi_age), results

def main():
    print("=" * 100)
    print("DEATH-WINDOW ANALYSIS — ALL CHARTS — Jaimini bracket + Maraka D-A-P convergence (Lahiri)")
    print("=" * 100)
    for name, info in CHARTS.items():
        try:
            chart, lon_, mar, lords, bracket, ages, results = analyze(name, info)
        except Exception as e:
            print(f"\n### {name}: ERROR {e}")
            continue
        h2, h7, h8, badh, occ = lords
        print(f"\n{'='*100}")
        print(f"### {name}")
        print(f"    Lagna {chart.ascendant_sign} | Bracket: {bracket} (raw Jaimini vote: {lon_['raw_mathematical_baseline'].split()[0]})")
        if lon_["kakshya_adjustments"]:
            for a in lon_["kakshya_adjustments"]:
                print(f"      {a}")
        print(f"    Marakas: 2L {h2}, 7L {h7} | 8L {h8} | Badhaka {badh}")
        if any(occ.values()):
            print(f"    House occupants: H2 {occ[2]} H7 {occ[7]} H8 {occ[8]}")
        print(f"    Scan range: age {ages[0]}–{ages[1]}")

        if "died" in info:
            d_age = (datetime.date.fromisoformat(info["died"]) - datetime.date(chart.birth_time.year if hasattr(chart, "birth_time") else 1950, 1, 1)).days / 365.25
            hit = any(r["start"].date() <= datetime.date.fromisoformat(info["died"]) <= r["end"].date() for r in results)
            print(f"    ACTUAL DEATH: {info['died']}  | inside maraka window: {'YES' if hit else 'NO'}")

        if not results:
            print("    No double-maraka windows found inside the bracket (rare).")
        else:
            print(f"    Double-maraka convergence windows ({len(results)} found; top shown):")
            shown = set()
            count = 0
            for r in results:
                key = (r["start"].strftime("%Y-%m"), r["triad"])
                if key in shown:
                    continue
                shown.add(key)
                count += 1
                if count > 8:
                    break
                mid = r["start"] + (r["end"] - r["start"]) / 2
                print(f"      [{r['strength']:.1f}] {r['start'].strftime('%Y-%m-%d')} -> {r['end'].strftime('%Y-%m-%d')}"
                      f"  (peak ~{mid.strftime('%Y-%m-%d')})  {r['triad']}"
                      f"  [MD-maraka: {'Y' if r['md_maraka'] else 'n'}]")

if __name__ == "__main__":
    main()
