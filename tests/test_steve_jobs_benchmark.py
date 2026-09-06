import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import pytz
import swisseph as swe

from astrology_engine import calculate_chart_with_object
from strength_engine import StrengthEngine
from ashtakavarga_engine import AshtakavargaEngine
from ashtakavarga_kakshya_engine import AshtakavargaKakshyaEngine
from sensitive_points import SensitivePointsEngine
from longevity_engine import LongevityEngine
from dasha_engine import DashaEngine
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine
from yogini_dasha_engine import YoginiDashaEngine
from tajika_engine import TajikaVarshaphalaEngine
from sade_sati_engine import SadeSatiEngine
from sarvatobhadra_chakra_engine import SarvatobhadraChakraEngine
from bhrigu_nandi_nadi_engine import BhriguNandiNadiEngine
from medical_astrology_engine import MedicalAstrologyEngine
from pushkara_engine import PushkaraEngine
from wealth_lagnas_engine import WealthLagnasEngine
from kp_interlinks_engine import KPCuspalInterlinksEngine
from jaimini_arudha_argala_engine import JaiminiArudhaArgalaEngine
from navatara_chakra_engine import NavataraChakraEngine
from gochara_vedha_engine import GocharaVedhaEngine
from cancellations import CancellationEngine
from yogas import evaluate_all_yogas

print("=" * 85)
print("COMPREHENSIVE CELEBRITY BENCHMARK: STEVE JOBS")
print("Birth: Feb 24, 1955, 19:15 PST (Feb 25, 1955, 03:15 UTC) | San Francisco, CA")
print("Lat: 37.7749 N, Lon: 122.4194 W | Sidereal Lahiri Ephemeris")
print("=" * 85)

# Calculate Chart
chart_jobs, raw_jobs = calculate_chart_with_object(
    1955, 2, 24, 19, 15, 37.7749, -122.4194, "America/Los_Angeles", "Steve Jobs"
)

# 1. Fundamental Blueprint
moon_p = chart_jobs.planets.get("Moon")
sun_p = chart_jobs.planets.get("Sun")
mars_p = chart_jobs.planets.get("Mars")
jup_p = chart_jobs.planets.get("Jupiter")
sat_p = chart_jobs.planets.get("Saturn")
mer_p = chart_jobs.planets.get("Mercury")
ven_p = chart_jobs.planets.get("Venus")
rahu_p = chart_jobs.planets.get("Rahu")
ketu_p = chart_jobs.planets.get("Ketu")

print(f"\n[1. NATAL BLUEPRINT & PLANETARY PLACEMENTS]")
print(f"  Ascendant (Lagna): {chart_jobs.ascendant_sign} {chart_jobs.ascendant_degree}°")
print(f"  Sun: {sun_p.sign} {sun_p.degree}° (Lagna Lord in 7H Aquarius - Shatabhisha)")
print(f"  Moon: {moon_p.sign} {moon_p.degree}° (12L in 8H Pisces - Uttara Bhadrapada Pada 4)")
print(f"  Mars: {mars_p.sign} {mars_p.degree}° (Yogakaraka 4L/9L in 9H Aries - Ashwini)")
print(f"  Mercury: {mer_p.sign} {mer_p.degree}° (2L/11L of Extreme Wealth in 6H Capricorn - Shravana)")
print(f"  Jupiter: {jup_p.sign} {jup_p.degree}° (5L/8L Exalted in Navamsha, 11H Gemini - Punarvasu)")
print(f"  Venus: {ven_p.sign} {ven_p.degree}° (3L/10L Career Lord in 5H Sagittarius - Mula, Pushkara Navamsha)")
print(f"  Saturn: {sat_p.sign} {sat_p.degree}° (6L/7L Exalted in 3H Libra - Vishakha, Digbala)")
print(f"  Rahu: {rahu_p.sign} {rahu_p.degree}° (3H Libra) | Ketu: {ketu_p.sign} {ketu_p.degree}° (9H Aries)")

# 2. Wealth Lagnas & Indu Lagna
wealth_eng = WealthLagnasEngine(chart_jobs)
wealth_res = wealth_eng.calculate_special_lagnas()
indu = wealth_res["indu_lagna"]
print(f"\n[2. WEALTH & EXECUTIVE POWER LAGNAS]")
print(f"  Indu Lagna (Dhana Sphuta): {indu['indu_lagna_sign']} (Ray sum: {indu['total_kalas']})")
print(f"  Financial Assessment: {indu['financial_magnitude_verdict']}")
print(f"  Shree Lagna (Prosperity): {wealth_res['shree_lagna']['sign']} {wealth_res['shree_lagna']['longitude']}°")
print(f"  Ghatika Lagna (Power & Rank): {wealth_res['ghatika_lagna']['sign']} {wealth_res['ghatika_lagna']['longitude']}°")
print(f"  Hora Lagna (Capital Accumulation): {wealth_res['hora_lagna']['sign']} {wealth_res['hora_lagna']['longitude']}°")

# 3. Pushkara Protection Matrix
push_eng = PushkaraEngine(chart_jobs)
push_res = push_eng.evaluate_all_planets()
print(f"\n[3. PUSHKARA BLESSINGS & RESILIENCE]")
print(f"  Total Pushkara Blessings: {push_res['total_pushkara_blessings']} | Resilience Rating: {push_res['resilience_rating']}")
for pname, pinfo in push_res['evaluations'].items():
    if pinfo['is_pushkara_navamsha'] or pinfo['is_pushkara_bhaga']:
        print(f"  - {pname}: {pinfo['status']}")

# 4. Jaimini Arudha Padas
arudha_eng = JaiminiArudhaArgalaEngine(chart_jobs)
padas = arudha_eng.calculate_all_padas()
print(f"\n[4. JAIMINI ARUDHA PADAS]")
for k, v in padas.items():
    if v['house'] in [1, 2, 7, 8, 10, 11, 12]:
        print(f"  - {v['pada_code']} ({v['pada_name']}): {v['pada_sign']} -> {v['significance']}")

# 5. Medical Tridosha Diagnostics
med_eng = MedicalAstrologyEngine(chart_jobs)
med_res = med_eng.diagnose_health_profile()
print(f"\n[5. MEDICAL ASTROLOGY & AYURVEDIC TRIDOSHA]")
print(f"  Primary Constitution: {med_res['primary_ayurvedic_dosha']}")
print(f"  Vulnerabilities: {med_res['dusthana_anatomical_vulnerabilities']}")

# 6. Sensitive Points & Longevity
sp_eng = SensitivePointsEngine(chart_jobs)
sp_data = sp_eng.calculate_all()
ayur = LongevityEngine.calculate_jaimini_longevity_span(chart_jobs)
print(f"\n[6. SENSITIVE POINTS & AYURDAYA LONGEVITY]")
print(f"  64th Navamsha (Kharesh): {sp_data.get('64th_navamsha', {}).get('from_moon', {}).get('d9_sign')} (Lord: {sp_data.get('64th_navamsha', {}).get('from_moon', {}).get('lord')})")
print(f"  22nd Drekkana (Kharadresh): {sp_data.get('22nd_drekkana', {}).get('d3_sign')} (Lord: {sp_data.get('22nd_drekkana', {}).get('kharesh_lord')})")
print(f"  Jaimini Longevity Class: {ayur.get('bracket')} ({ayur.get('estimated_range')})")
print(f"  Pairs: {ayur.get('pair_evaluations')}")

# 7. Milestone Historical Backtesting
print(f"\n" + "="*85)
print(f"[7. HISTORICAL MILESTONE ACCURACY BENCHMARK & ENGINE EVALUATION]")
print(f"="*85)

dob_utc = datetime(1955, 2, 25, 3, 15, tzinfo=pytz.utc)
events = [
    {
        "name": "1. Founding of Apple Inc.",
        "date": datetime(1976, 4, 1, tzinfo=pytz.utc),
        "category": "CAREER_BREAKTHROUGH",
        "description": "Steve Jobs & Wozniak incorporate Apple Computer. Era of microcomputing begins."
    },
    {
        "name": "2. Ouster from Apple & Founding NeXT / Buying Pixar",
        "date": datetime(1985, 9, 16, tzinfo=pytz.utc),
        "category": "CRISIS_AND_REINVENTION",
        "description": "Board strips Jobs of operational duties; Jobs exits Apple and buys Lucasfilm computer unit (Pixar)."
    },
    {
        "name": "3. Return to Apple as Interim CEO (The Renaissance)",
        "date": datetime(1997, 7, 9, tzinfo=pytz.utc),
        "category": "CAREER_RESURGENCE",
        "description": "Returns as CEO, rescues Apple from 90 days of cash insolvency, begins historic turnaround."
    },
    {
        "name": "4. Pancreatic Cancer Diagnosis & Major Whipple Surgery",
        "date": datetime(2004, 7, 31, tzinfo=pytz.utc),
        "category": "ACUTE_MEDICAL_SURGERY",
        "description": "Undergoes extensive surgery for islet neuroendocrine tumor."
    },
    {
        "name": "5. iPhone Unveiling (Historic Tech & Wealth Zenith)",
        "date": datetime(2007, 1, 9, tzinfo=pytz.utc),
        "category": "CAREER_AND_WEALTH_PEAK",
        "description": "Unveils iPhone at Macworld; Apple starts ascent to world's highest market cap."
    },
    {
        "name": "6. Emergency Liver Transplant Surgery",
        "date": datetime(2009, 4, 15, tzinfo=pytz.utc),
        "category": "ORGAN_TRANSPLANT_CRISIS",
        "description": "Critical surgical intervention for metastatic neuroendocrine disease."
    },
    {
        "name": "7. Steve Jobs Passing (Lifespan Termination)",
        "date": datetime(2011, 10, 5, tzinfo=pytz.utc),
        "category": "LONGEVITY_TERMINATION",
        "description": "Passes away in Palo Alto at age 56 (within Jaimini Madhyayu window)."
    }
]

vim_tl = DashaEngine.calculate_vimshottari_timeline(dob_utc, moon_p.longitude, num_levels=2)
chara_tl = JaiminiCharaDashaEngine.calculate_chara_dasha_timeline(chart_jobs, dob_utc, cycles=2)
yogini_tl = YoginiDashaEngine.calculate_yogini_timeline(dob_utc, moon_p.longitude, cycles=3)
sade_eng = SadeSatiEngine(chart_jobs)

for ev in events:
    edate = ev["date"]
    print(f"\n>>> MILESTONE: {ev['name']} ({edate.strftime('%b %d, %Y')})")
    print(f"    Context: {ev['description']}")
    
    # 1. Vimshottari D-A
    curr_md = "Unknown"
    curr_ad = "Unknown"
    for md_node in vim_tl:
        s_dt = datetime.fromisoformat(md_node["start"])
        e_dt = datetime.fromisoformat(md_node["end"])
        if s_dt <= edate <= e_dt:
            curr_md = md_node["lord"]
            for ad_node in md_node.get("sub_periods", []):
                ad_s = datetime.fromisoformat(ad_node["start"])
                ad_e = datetime.fromisoformat(ad_node["end"])
                if ad_s <= edate <= ad_e:
                    curr_ad = ad_node["lord"]
                    break
            break
    
    # 2. Jaimini Chara Dasha
    curr_chara = None
    for c in chara_tl:
        c_s = datetime.strptime(c["start"], "%Y-%m-%d").replace(tzinfo=pytz.utc)
        c_e = datetime.strptime(c["end"], "%Y-%m-%d").replace(tzinfo=pytz.utc)
        if c_s <= edate <= c_e:
            curr_chara = c
            break

    # 3. Yogini Dasha
    curr_yog = None
    for y in yogini_tl:
        y_s = datetime.strptime(y["start"], "%Y-%m-%d").replace(tzinfo=pytz.utc)
        y_e = datetime.strptime(y["end"], "%Y-%m-%d").replace(tzinfo=pytz.utc)
        if y_s <= edate <= y_e:
            curr_yog = y
            break

    # 4. Tajika Solar Return for that event year
    varsha = TajikaVarshaphalaEngine.calculate_annual_chart(chart_jobs, edate.year, 37.7749, -122.4194)
    
    # 5. Sade Sati status
    sade_stat = sade_eng.evaluate_current_status(edate)

    # 6. SBC Vedha check for event date
    sbc_eng = SarvatobhadraChakraEngine(chart_jobs)
    sbc_status = sbc_eng.evaluate_transit_vedha(edate)

    # 7. Navatara for transiting Moon on event date
    nava_eng = NavataraChakraEngine(chart_jobs)
    nava_res = nava_eng.evaluate_transit_moon_tara(edate)

    # 8. Gochara Vedha for transiting planets
    vedha_eng = GocharaVedhaEngine(chart_jobs)
    vedha_res = vedha_eng.evaluate_all_transits(edate)

    chara_desc = f"{curr_chara['sign']} Sign (Activations: {curr_chara.get('special_activations', [])})" if curr_chara else "N/A"
    yog_desc = f"{curr_yog['yogini']} (Ruler: {curr_yog['ruler']}, Nature: {curr_yog['nature']})" if curr_yog else "N/A"

    print(f"    1. Vimshottari Dasha: {curr_md}-{curr_ad}")
    print(f"    2. Jaimini Chara Dasha: {chara_desc}")
    print(f"    3. Yogini Dasha: {yog_desc}")
    print(f"    4. Shani Gochara / Sade Sati: {sade_stat['status']} (Phase: {sade_stat.get('phase', 'None')})")
    print(f"    5. Tajika Solar Return: Muntha in {varsha['muntha']['sign']} (House {varsha['muntha']['house_in_varsha_chart']}), Year Lord: {varsha['varsha_swami_year_lord']}")
    print(f"    6. SBC Vedha Threat: {sbc_status['risk_level']} ({len(sbc_status['active_vedhas'])} active malefic Vedhas)")
    print(f"    7. Navatara Moon: {nava_res['tara_details']['tara_name']} ({nava_res['tara_details']['nature']})")
