"""
Regression Test Suite — Astrology AI Engine
Locks in validated reference values (cross-checked against PyJHora & SwissEph).

Run: python test_engine_validation.py
"""
import sys
import json
from datetime import datetime

PASS = 0
FAIL = 0
FAILURES = []

def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {label}")
    else:
        FAIL += 1
        FAILURES.append(f"{label} {detail}")
        print(f"  [FAIL] {label} {detail}")


def main():
    from astrology_engine import calculate_chart_with_object

    # ---- Reference chart: user natal (validated vs PyJHora D1) ----
    chart_obj, _ = calculate_chart_with_object(
        2008, 8, 1, 18, 25, 16.8185549, 82.0641497, "Asia/Kolkata")

    print("== 1. Natal positions (D1, Lahiri) ==")
    REF = {
        "Ascendant": ("Capricorn", 14.21),
        "Sun": ("Cancer", 15.66), "Moon": ("Cancer", 17.17),
        "Mars": ("Leo", 24.78), "Mercury": ("Cancer", 18.67),
        "Jupiter": ("Sagittarius", 20.69), "Venus": ("Leo", 0.31),
        "Saturn": ("Leo", 13.82), "Rahu": ("Capricorn", 24.54),
        "Ketu": ("Cancer", 24.54),
    }
    for name, (ref_sign, ref_deg) in REF.items():
        if name == "Ascendant":
            s, d = chart_obj.ascendant_sign, chart_obj.ascendant_degree
        else:
            p = chart_obj.planets[name]
            s, d = p.sign, p.degree
        check(f"{name} {s} {d:.2f}",
              s == ref_sign and abs(d - ref_deg) < 0.05,
              f"(expected {ref_sign} {ref_deg})")

    print("== 2. Nakshatra of Moon (dasha seed) ==")
    # Moon at 107.17 absolute -> Ashlesha (3.8% elapsed), lord Mercury
    from astrology_engine import calculate_nakshatra
    ZOD = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
           "Sagittarius","Capricorn","Aquarius","Pisces"]
    moon = chart_obj.planets["Moon"]
    moon_lon = ZOD.index(moon.sign) * 30 + moon.degree
    nak, pada, lord = calculate_nakshatra(moon_lon)
    check(f"Moon nakshatra {nak} (lord {lord})",
          nak == "Ashlesha" and lord == "Mercury")

    print("== 3. Vimshottari dasha periods ==")
    from dasha_engine import DashaEngine
    tl = DashaEngine.calculate_vimshottari_timeline(datetime(2008, 8, 1, 12, 55), moon_lon)
    # Birth balance: Mercury MD ends ~Dec 2024; Ketu MD 2024.95-2031.95
    lords = [t.get("lord") for t in tl[:5]]
    check(f"MD sequence {lords}", lords == ["Mercury", "Ketu", "Venus", "Sun", "Moon"])
    cur = DashaEngine.get_current_dasha(tl, datetime(2026, 9, 6))
    check(f"Current (2026-09-06): {cur['mahadasha']}-{cur['antardasha']}",
          cur["mahadasha"] == "Ketu" and cur["antardasha"] == "Sun")

    print("== 4. Chara Karakas (absolute-longitude ranking) ==")
    from jaimini_engine import JaiminiEngine
    mapping = JaiminiEngine.calculate_chara_karakas(chart_obj)
    expected_karakas = {"AK": "Jupiter", "AmK": "Mars", "BK": "Saturn",
                        "MK": "Venus", "PK": "Mercury", "GK": "Moon", "DK": "Sun"}
    check(f"Karakas {mapping}", mapping == expected_karakas)

    print("== 5. Arudha Lagna ==")
    arudhas = JaiminiEngine.calculate_all_arudhas(chart_obj)
    check(f"AL = {arudhas.get('AL')}", arudhas.get("AL") == "Pisces")
    check(f"A11 = {arudhas.get('A11')}", arudhas.get("A11") == "Pisces")

    print("== 6. Varga math (D9/D10 vs PyJHora longitudes) ==")
    from varga_engine import VargaEngine
    PJH_LONS = {"Sun": ("Cancer", 16.80), "Moon": ("Cancer", 18.30),
                "Mars": ("Leo", 25.93), "Mercury": ("Cancer", 19.82),
                "Jupiter": ("Sagittarius", 21.82), "Venus": ("Leo", 1.46),
                "Saturn": ("Leo", 14.96)}
    PJH_D9 = {"Sun": "Sagittarius", "Moon": "Sagittarius", "Mars": "Scorpio",
              "Mercury": "Sagittarius", "Jupiter": "Libra", "Venus": "Aries",
              "Saturn": "Leo"}
    PJH_D10 = {"Sun": "Leo", "Moon": "Virgo", "Mars": "Aries", "Mercury": "Virgo",
               "Jupiter": "Cancer", "Venus": "Leo", "Saturn": "Sagittarius"}
    for name, (sign, deg) in PJH_LONS.items():
        d9 = VargaEngine.calc_d9_navamsha(sign, deg)
        d10 = VargaEngine.calc_d10_dasamsha(sign, deg)
        check(f"{name} D9 {d9}", d9 == PJH_D9[name])
        check(f"{name} D10 {d10}", d10 == PJH_D10[name])

    print("== 7. KP chart (correct IST timezone) ==")
    from kp_engine import KPEngine
    res = KPEngine.calculate_kp_chart(2008, 8, 1, 18, 25,
                                      16.8185549, 82.0641497, "Asia/Kolkata")
    c1 = res["cusps"][0]
    check(f"KP Cusp1 {c1['sign']} {c1['degree']:.2f}",
          c1["sign"] == "Capricorn" and abs(c1["degree"] - 14.31) < 0.1)
    c10 = res["cusps"][9]
    check(f"KP 10th CSL = {c10['sub_lord']}", c10["sub_lord"] == "Mercury")
    csl = res["csl_analysis"]["career_10th_csl"]
    check(f"Career promise {csl['status']}", csl["status"] == "STRONG_CAREER_PROMISE")

    print("== 8. Ayanamsha isolation (KP call must not corrupt Lahiri) ==")
    import swisseph as swe
    res2 = KPEngine.calculate_kp_chart(2008, 8, 1, 18, 25,
                                       16.8185549, 82.0641497, "Asia/Kolkata")
    chart2, _ = calculate_chart_with_object(
        2008, 8, 1, 18, 25, 16.8185549, 82.0641497, "Asia/Kolkata")
    jup = chart2.planets["Jupiter"]
    check(f"Lahiri preserved after KP call (Jupiter {jup.sign} {jup.degree:.2f})",
          jup.sign == "Sagittarius" and abs(jup.degree - 20.69) < 0.05)

    print("== 9. Yogas fire on this chart ==")
    from yogas import evaluate_all_yogas
    ys = evaluate_all_yogas(chart_obj)
    names = [y["name"] for y in ys]
    # Tolerate naming variants ("Budhaditya" vs "Budhaditya Yoga")
    names_lc = [n.lower() for n in names]
    check("Budhaditya detected", any("budhaditya" in n for n in names_lc))
    check("Raja Yoga detected", any("raja yoga" in n for n in names_lc))
    check("Dhana Yoga detected", any("dhana yoga" in n for n in names_lc))
    check("No false Mahapurusha (Venus Leo 8th)", not any("malavya" in n for n in names_lc))

    print("== 10. Ashtakavarga total ==")
    sav = chart_obj.sarvashtakavarga
    check(f"SAV total = {sum(sav.values())}", sum(sav.values()) == 337)

    print()
    print(f"RESULT: {PASS} passed, {FAIL} failed")
    if FAILURES:
        print("Failures:")
        for f in FAILURES:
            print("  -", f)
        sys.exit(1)


if __name__ == "__main__":
    main()
