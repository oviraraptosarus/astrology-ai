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

print("=" * 90)
print("DEEP 360-DEGREE LIFE ASPECTS AUDIT: ELON MUSK")
print("Birth: June 28, 1971, 06:30 SAST (04:30 UTC) | Pretoria, South Africa")
print("Lat: 25.7479 S, Lon: 28.2293 E | Sidereal Lahiri Ephemeris")
print("=" * 90)

chart_musk, _ = calculate_chart_with_object(
    1971, 6, 28, 6, 30, -25.7479, 28.2293, "Africa/Johannesburg", "Elon Musk"
)

# Extract Core Parameters
planets = chart_musk.planets
moon_p = planets.get("Moon")
sun_p = planets.get("Sun")
mars_p = planets.get("Mars")
jup_p = planets.get("Jupiter")
sat_p = planets.get("Saturn")
mer_p = planets.get("Mercury")
ven_p = planets.get("Venus")
rahu_p = planets.get("Rahu")
ketu_p = planets.get("Ketu")

# Run all master engines
karakas = JaiminiCharaDashaEngine.calculate_chara_karakas(chart_musk)
wealth = WealthLagnasEngine(chart_musk).calculate_special_lagnas()
arudhas = JaiminiArudhaArgalaEngine(chart_musk).calculate_all_padas()
med = MedicalAstrologyEngine(chart_musk).diagnose_health_profile()
push = PushkaraEngine(chart_musk).evaluate_all_planets()
sp = SensitivePointsEngine(chart_musk).calculate_all()
ayur = LongevityEngine.calculate_jaimini_longevity_span(chart_musk)
yogas_list = evaluate_all_yogas(chart_musk)

print(f"\n[1. NATAL BLUEPRINT & ASTROMETRICS]")
print(f"  Ascendant (Lagna): {chart_musk.ascendant_sign} {chart_musk.ascendant_degree}°")
print(f"  Moon: {moon_p.sign} {moon_p.degree}° ({moon_p.nakshatra} Pada {moon_p.nakshatra_pada}) - House {moon_p.house} (Simha Moon)")
print(f"  Sun: {sun_p.sign} {sun_p.degree}° ({sun_p.nakshatra}) - House {sun_p.house}")
print(f"  Mars: {mars_p.sign} {mars_p.degree}° (Exalted in Capricorn {mars_p.degree}°, Ruchaka Yoga / 7H/8H)")
print(f"  Saturn: {sat_p.sign} {sat_p.degree}° (11H/12H Lord in Taurus)")
print(f"  Jupiter: {jup_p.sign} {jup_p.degree}° (Retrograde in Scorpio 5H/6H)")
print(f"  Mercury: {mer_p.sign} {mer_p.degree}° (Lagna Lord in Gemini / Cancer border)")
print(f"  Venus: {ven_p.sign} {ven_p.degree}° (Taurus {ven_p.degree}° - Own Sign Malavya/Dhana)")

print(f"\n[2. WEALTH & MULTI-CENTIBILLIONAIRE MAGNITUDE]")
indu = wealth["indu_lagna"]
print(f"  Indu Lagna (Wealth Ascendant): {indu['indu_lagna_sign']} (Total Kalas: {indu['total_kalas']})")
print(f"  Indu Assessment: {indu['financial_magnitude_verdict']}")
print(f"  Hora Lagna (Capital Accumulation): {wealth['hora_lagna']['sign']} {wealth['hora_lagna']['longitude']}°")
print(f"  Dhana Pada (A2 - Liquid Net Worth): {arudhas.get('House_2_A2', {}).get('pada_sign')}")
print(f"  Labha Pada (A11 - Extreme Cash Flow): {arudhas.get('House_11_A11', {}).get('pada_sign')}")
print(f"  Ground Truth: Peak Net Worth $300B+ (World's Richest Individual, 2021-Present).")

print(f"\n[3. CAREER, SPACEX, TESLA & INDUSTRIAL EMPIRES]")
print(f"  Rajya Pada (A10 - Public Office/Empire): {arudhas.get('House_10_A10', {}).get('pada_sign')}")
print(f"  Ghatika Lagna (Executive Power & Stature): {wealth['ghatika_lagna']['sign']} {wealth['ghatika_lagna']['longitude']}°")
print(f"  Exalted Mars (Rocketry, Explosions, Heavy Manufacturing, Physics, Aerospace Engineering).")
print(f"  Ground Truth: Founded SpaceX (Rockets/Mars exploration), Built Tesla (EVs/Robotics), Starlink, xAI, Neuralink.")

print(f"\n[4. RELATIONSHIPS, MARRIAGES & MULTIPLE PROGENY]")
print(f"  Dara Karaka (DK - Spouse Indicator): {karakas.get('DK', {}).get('planet')} in {karakas.get('DK', {}).get('sign')}")
print(f"  Upapada Lagna (UL - Marriage): {arudhas.get('House_12_A12_UL', {}).get('pada_sign')}")
print(f"  7th House / Cusp: Exalted Mars sitting on 7H/8H axis -> Intense martial dynamic, multiple high-profile marriages (Justine Wilson, Talulah Riley twice) and 10+ children (5th house Jupiter in Scorpio).")

print(f"\n[5. SENSITIVE POINTS & AYURDAYA LONGEVITY]")
print(f"  64th Navamsha Lord: {sp.get('64th_navamsha', {}).get('from_moon', {}).get('lord')}")
print(f"  22nd Drekkana Lord: {sp.get('22nd_drekkana', {}).get('kharesh_lord')}")
print(f"  Jaimini Longevity: {ayur.get('bracket')} ({ayur.get('estimated_range')})")

print(f"\n" + "="*90)
print(f"[6. HISTORICAL MILESTONE ACCURACY BENCHMARK: ELON MUSK]")
print(f"="*90)

dob_utc = datetime(1971, 6, 28, 4, 30, tzinfo=pytz.utc)
events = [
    {
        "name": "1. Zip2 Sold to Compaq for $307 Million",
        "date": datetime(1999, 2, 1, tzinfo=pytz.utc),
        "description": "First massive liquidity event; netted $22 million personal payout."
    },
    {
        "name": "2. Severe Cerebral Malaria (Near-Fatal Medical Crisis)",
        "date": datetime(2000, 12, 15, tzinfo=pytz.utc),
        "description": "Contracted severe falciparum malaria in South Africa; ICU hospitalization near death."
    },
    {
        "name": "3. PayPal Sold to eBay for $1.5 Billion",
        "date": datetime(2002, 10, 3, tzinfo=pytz.utc),
        "description": "Netted $180M payout, immediately funded SpaceX ($100M) and Tesla ($70M)."
    },
    {
        "name": "4. Falcon 1 Flight 4 Success & $1.6B NASA Contract",
        "date": datetime(2008, 9, 28, tzinfo=pytz.utc),
        "description": "SpaceX rescues company on 4th launch, receives NASA CRS contract, saves Tesla from bankruptcy."
    },
    {
        "name": "5. Tesla IPO on NASDAQ (Historic Capital Resurgence)",
        "date": datetime(2010, 6, 29, tzinfo=pytz.utc),
        "description": "First American car company IPO since Ford in 1956."
    },
    {
        "name": "6. Becomes Richest Person on Earth ($185B+)",
        "date": datetime(2021, 1, 7, tzinfo=pytz.utc),
        "description": "Tesla stock surges 700%, overtaking Jeff Bezos as wealthiest human."
    },
    {
        "name": "7. Acquisition of Twitter / X ($44 Billion)",
        "date": datetime(2022, 10, 27, tzinfo=pytz.utc),
        "description": "Major corporate restructuring and free speech platform takeover."
    }
]

vim_tl = DashaEngine.calculate_vimshottari_timeline(dob_utc, moon_p.longitude, num_levels=2)
chara_tl = JaiminiCharaDashaEngine.calculate_chara_dasha_timeline(chart_musk, dob_utc, cycles=2)
yogini_tl = YoginiDashaEngine.calculate_yogini_timeline(dob_utc, moon_p.longitude, cycles=3)
sade_eng = SadeSatiEngine(chart_musk)

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

    # 4. Sade Sati status
    sade_stat = sade_eng.evaluate_current_status(edate)

    # 5. SBC Vedha check for event date
    sbc_eng = SarvatobhadraChakraEngine(chart_musk)
    sbc_status = sbc_eng.evaluate_transit_vedha(edate)

    # 6. Navatara for transiting Moon on event date
    nava_eng = NavataraChakraEngine(chart_musk)
    nava_res = nava_eng.evaluate_transit_moon_tara(edate)

    chara_desc = f"{curr_chara['sign']} Sign (Activations: {curr_chara.get('special_activations', [])})" if curr_chara else "N/A"
    yog_desc = f"{curr_yog['yogini']} (Ruler: {curr_yog['ruler']}, Nature: {curr_yog['nature']})" if curr_yog else "N/A"

    print(f"    1. Vimshottari Dasha: {curr_md}-{curr_ad}")
    print(f"    2. Jaimini Sign Dasha: {chara_desc}")
    print(f"    3. Yogini Dasha: {yog_desc}")
    print(f"    4. Shani Gochara / Sade Sati: {sade_stat['status']} (Phase: {sade_stat.get('phase', 'None')})")
    print(f"    5. SBC Vedha Threat: {sbc_status['risk_level']} ({len(sbc_status['active_vedhas'])} active malefic Vedhas)")
    print(f"    6. Navatara Moon: {nava_res['tara_details']['tara_name']} ({nava_res['tara_details']['nature']})")
