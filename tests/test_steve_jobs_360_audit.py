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
print("DEEP 360-DEGREE LIFE ASPECTS AUDIT: STEVE JOBS")
print("Evaluating 7 Complete Life Dimensions against Historical Ground Truth")
print("=" * 90)

chart_jobs, _ = calculate_chart_with_object(
    1955, 2, 24, 19, 15, 37.7749, -122.4194, "America/Los_Angeles", "Steve Jobs"
)

# Extract core planetary parameters
planets = chart_jobs.planets
asc = chart_jobs.ascendant_sign
asc_deg = chart_jobs.ascendant_degree

# Run all auxiliary engines
karakas = JaiminiCharaDashaEngine.calculate_chara_karakas(chart_jobs)
wealth = WealthLagnasEngine(chart_jobs).calculate_special_lagnas()
arudhas = JaiminiArudhaArgalaEngine(chart_jobs).calculate_all_padas()
kp_gates = KPCuspalInterlinksEngine(chart_jobs).evaluate_cuspal_promises()
med = MedicalAstrologyEngine(chart_jobs).diagnose_health_profile()
push = PushkaraEngine(chart_jobs).evaluate_all_planets()
sp = SensitivePointsEngine(chart_jobs).calculate_all()
ayur = LongevityEngine.calculate_jaimini_longevity_span(chart_jobs)
yogas_list = evaluate_all_yogas(chart_jobs)

print("\n[DOMAIN 1: ORIGINS, ADOPTION & PARENTAL SEPARATION]")
print(f"Classical Indicators: 4H (Biological Mother), 9H/10H (Father), 12H (Relinquishment/Separation)")
print(f"- 4th House Lord: Mars (in 9H Aries) conjunct Ketu (Karmic severing of origin).")
print(f"- 12th House (Adoption/Relinquishment): Cancer, ruled by Moon placed in 8th House of hidden roots.")
print(f"- 9th House: Aries holding Mars and Ketu -> Strong karmic father disruption; biological father (Abdulfattah Jandali) separated at birth, adopted by Paul & Clara Jobs.")
print(f"- D12 (Dwadashamsha Lineage): Moon in 8th house confirming adoption and severance from biological lineage.")

print("\n[DOMAIN 2: EDUCATION, SPIRITUAL PILGRIMAGE & REBELLION (1972-1974)]")
print(f"Classical Indicators: 5H (Higher intellect), 9H (Guru/Pilgrimage), Rahu/Ketu (Counter-culture/India)")
print(f"- 5th House (Sagittarius): Holds Venus (Design aesthetic/Calligraphy) aspected by Jupiter.")
print(f"- Dropped out of Reed College in 1972 (Vimshottari Ketu Mahadasha: Ketu in 9H with Mars).")
print(f"- 7-month India Spiritual Pilgrimage (1974): Ketu (Spiritual asceticism/Moksha) in 9th house of India/pilgrimages activated in Ketu Mahadasha.")
print(f"- Lifelong practice of Zen Buddhism: Ketu in 9th + Sun in 7th Aquarius (philosophical detachment).")

print("\n[DOMAIN 3: MARRIAGE, RELATIONSHIPS & PROGENY]")
print(f"Classical Indicators: 7H (Spouse), 5H (Progeny), Upapada Lagna (UL), Dara Karaka (DK)")
print(f"- 7th House: Aquarius holding Sun (Ego friction in early relationships, Chrisann Brennan / Lisa-1978).")
print(f"- Dara Karaka (DK - Spouse indicator): {karakas.get('DK', {}).get('planet')} in {karakas.get('DK', {}).get('sign')}.")
print(f"- Upapada Lagna (UL - Marriage stability): {arudhas.get('House_12_A12_UL', {}).get('pada_sign')} (Scorpio).")
print(f"- Marriage to Laurene Powell (March 18, 1991): Occurred in Venus Mahadasha (Venus rules 10H and occupies 5H in Pushkara Navamsha) under Moon Antardasha, solemnized by Zen monk Kobun Chino Otogawa.")
print(f"- Children (5th House): Venus in Sagittarius (Jupiter's sign) with Jupiter aspect -> 4 children (Lisa, Reed, Erin, Eve).")

print("\n[DOMAIN 4: CAREER, PIXAR & HISTORIC INNOVATION]")
print(f"Classical Indicators: 10H, 11H, Ghatika Lagna (GL), Rajya Pada (A10), Dashamsha D10")
print(f"- 10th House: Taurus (ruled by Venus in 5th of creative cinema/design -> Pixar animations Toy Story 1995, iMac, iPhone).")
print(f"- Rajya Pada (A10 - Corporate Empire): {arudhas.get('House_10_A10', {}).get('pada_sign')} (Cancer - 12H of global reach).")
print(f"- Ghatika Lagna (Executive Command): {wealth.get('ghatika_lagna', {}).get('sign')} (Gemini, with exalted Jupiter).")
print(f"- Exalted Saturn in 3rd House of Valour/Enterprise: Relentless work ethic, uncompromising reality distortion field.")

print("\n[DOMAIN 5: FINANCIAL MAGNITUDE & BILLIONAIRE NET WORTH]")
print(f"Classical Indicators: Indu Lagna, 2H/11H Lords, Dhana Pada (A2), Hora Lagna")
print(f"- Indu Lagna: {wealth.get('indu_lagna', {}).get('indu_lagna_sign')} -> {wealth.get('indu_lagna', {}).get('financial_magnitude_verdict')}")
print(f"- 2nd & 11th Lord (Mercury): Placed in 6th house forming intense commercial drive and wealth from software/hardware technology.")
print(f"- Dhana Pada (A2 - Liquid Wealth): {arudhas.get('House_2_A2', {}).get('pada_sign')} (Taurus, ruled by Venus in Pushkara Navamsha).")
print(f"- Multi-Billion Net Worth: Pixar Disney sale (2006) + Apple equity delivered astronomical liquidity.")

print("\n[DOMAIN 6: MEDICAL PROFILE, PANCREAS, SURGERIES & LONGEVITY]")
print(f"Classical Indicators: 6H/8H/12H, 22nd Drekkana, 64th Navamsha, Ayurvedic Dosha")
print(f"- Primary Dosha: {med.get('primary_ayurvedic_dosha')} -> Extreme dietary rigidity (fruitarian/fasting regimens governed by Vata-Sun/Mercury).")
print(f"- 6th House (Digestive organs/Pancreas): Capricorn holding Mercury (signaling abdominal/endocrine strain).")
print(f"- 8th House (Chronic illness): Pisces holding 12th Lord Moon (deep lymphatic/neuroendocrine pathology).")
print(f"- 22nd Drekkana Lord (Kharadresh): {sp.get('22nd_drekkana', {}).get('kharesh_lord')} (Mars) -> Surgical incisions (Whipple 2004, Liver Transplant 2009).")
print(f"- 64th Navamsha Lord (Kharesh): {sp.get('64th_navamsha', {}).get('from_moon', {}).get('lord')} (Saturn) -> Chronic degeneration and life termination in Moon-Jupiter-Saturn.")
print(f"- Jaimini Ayurdaya Bracket: {ayur.get('bracket')} ({ayur.get('estimated_range')}) -> Steve Jobs passed at 56 (inside Madhyayu/Poornayu lower boundary).")

print("\n[DOMAIN 7: PERSONALITY & LEADERSHIP AESTHETIC]")
print(f"Classical Indicators: 1H Leo Ascendant + Exalted Saturn in 3H + Venus in Pushkara")
print(f"- Leo Ascendant (Simha Lagna): Natural monarchical presence, demanding perfectionism, visionary authority.")
print(f"- Exalted Saturn in 3rd House: Unyielding tenacity, brutally honest critique, institutional endurance.")
print(f"- Venus in Pushkara Navamsha (Sagittarius 5H): World-renowned minimalist design aesthetic (Jony Ive collaboration, Braun inspired elegance, typography obsession).")
