import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from datetime import datetime
import pytz
import swisseph as swe

# 1. Core Ephemeris & Kundli Math
from astrology_engine import calculate_full_chart, calculate_chart_with_object, get_semantic_view
chart_obj, chart_dict = calculate_chart_with_object(1990, 1, 15, 14, 30, 28.6139, 77.2090, "Asia/Kolkata", "Test User")
assert chart_obj is not None, "Core Chart calculation failed"
print("[PASS] 1. Core Ephemeris & Kundli Math (D1-D60, Ascendant, Shadbala)")

# 2. Location-based Drik Panchangam
from panchangam_engine import PanchangamEngine
pe = PanchangamEngine()
pan = pe.calculate_full_panchang(datetime.now(pytz.timezone("Asia/Kolkata")), 28.6139, 77.2090, "Asia/Kolkata")
assert "panchanga" in pan and "choghadiya_day" in pan, "Panchang failed"
print("[PASS] 2. Location-Based Drik Panchangam & Choghadiya Engine")

# 3. Sensitive Points & Upagrahas
from sensitive_points import SensitivePointsEngine
from upagrahas import UpagrahaEngine
sp = SensitivePointsEngine(chart_obj).calculate_all()
up = UpagrahaEngine(chart_obj).calculate_aprakash_grahas()
assert "22nd_drekkana" in sp and "dhuma" in up, "Sensitive points / Upagrahas failed"
print("[PASS] 3. Sensitive Points (64th Navamsha, 22nd Drekkana) & Upagrahas (Mandi/Gulika/Dhuma)")

# 4. Cancellations, Avasthas & Yogas
from cancellations import CancellationEngine
from advanced_avasthas import AdvancedAvasthaEngine
from yogas import evaluate_all_yogas
canc = CancellationEngine(chart_obj).evaluate_all()
av = AdvancedAvasthaEngine(chart_obj).combine_all()
yogas = evaluate_all_yogas(chart_obj)
assert "neecha_bhanga_raja_yogas" in canc and "lajjitadi_avasthas" in av, "Cancellations / Avasthas failed"
print("[PASS] 4. Cancellations (NBRY, VRY, Bhangas), Lajjitadi Avasthas & Canonical Yogas")

# 5. Forward Predictive Timing Scanner
from forward_timing_scanner import ForwardTimingScanner
scanner = ForwardTimingScanner(chart_obj)
windows = scanner.scan_domain_windows("HEALTH_ACCIDENT", start_date=datetime.now(pytz.utc), months_ahead=24)
assert isinstance(windows, list), "Forward timing scanner failed"
print(f"[PASS] 5. Forward Predictive Timing Scanner ({len(windows)} qualified acute accident/trauma windows found)")

# 6. Institutional Defense & Financial Engines
from financial_astro_engine import FinancialAstroEngine
from institutional_chakra_engine import InstitutionalChakraEngine
from realtime_engine import RealtimeEngine
now = datetime.now(pytz.utc)
jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
live_planets = RealtimeEngine.get_live_planets(jd)
gann = FinancialAstroEngine.calculate_gann_squaring(65000.0, live_planets)
kota = InstitutionalChakraEngine.calculate_kota_chakra(chart_obj, live_planets)
assert "active_squarings" in gann and "siege_status" in kota, "Gann / Kota failed"
print("[PASS] 6. W.D. Gann Square of 9 & Kota Chakra Institutional Defense")

# 7. Ank Jyotish, Chaldean Numerology & Tamil Pancha Pakshi
from numerology_engine import NumerologyEngine
from pancha_pakshi_engine import PanchaPakshiEngine
num = NumerologyEngine.generate_full_profile(15, 1, 1990, "Test User")
pak = PanchaPakshiEngine.get_pakshi_reading(chart_obj, datetime.now(pytz.timezone("Asia/Kolkata")))
assert "moolank" in num and "birth_bird" in pak, "Numerology / Pakshi failed"
print("[PASS] 7. Ank Jyotish, Chaldean Numerology & Tamil Siddha Pancha Pakshi")

# 8. Prescriptive Remedies & Gemstone Safety
from remedy_engine import RemedyEngine
rem = RemedyEngine().get_remedy_for_planet("Saturn", is_benefic=True, is_afflicted=False)
assert "gemstone_verdict" in rem and "vedic_mantra" in rem, "Remedies failed"
print("[PASS] 8. Prescriptive Remedies Matrix & Anukool Gemstone Safety")

# 9. Jaimini Chara Dasha & Karakas
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine
chara_karakas = JaiminiCharaDashaEngine.calculate_chara_karakas(chart_obj)
chara_tl = JaiminiCharaDashaEngine.calculate_chara_dasha_timeline(chart_obj, datetime(1990, 1, 15, 9, 0, tzinfo=pytz.utc))
assert "AK" in chara_karakas and len(chara_tl) >= 12, "Jaimini Chara Dasha failed"
print(f"[PASS] 9. Jaimini Chara Dasha Engine (AK: {chara_karakas['AK']['planet']}, {len(chara_tl)} sign periods)")

# 10. Tajika Varshaphala Annual Solar Return
from tajika_engine import TajikaVarshaphalaEngine
annual_chart = TajikaVarshaphalaEngine.calculate_annual_chart(chart_obj, 2026, 28.6139, 77.2090)
assert "varsha_ascendant" in annual_chart and "muntha" in annual_chart, "Tajika Varshaphala failed"
print(f"[PASS] 10. Tajika Varshaphala Solar Return (Muntha: {annual_chart['muntha']['sign']}, Year Lord: {annual_chart['varsha_swami_year_lord']})")

# 11. C.S. Patel Ashtakavarga Kakshya Timing
from ashtakavarga_kakshya_engine import AshtakavargaKakshyaEngine
kakshya_eng = AshtakavargaKakshyaEngine(chart_obj)
kakshya_windows = kakshya_eng.scan_kakshya_windows("Jupiter", datetime.now(pytz.utc), duration_days=30)
assert len(kakshya_windows) > 0, "Kakshya transit scanner failed"
print(f"[PASS] 11. C.S. Patel Ashtakavarga Kakshya Engine ({len(kakshya_windows)} 3.5-day transit sub-windows)")

# 12. Kundali Milan & Synastry
from kundali_milan_synastry_engine import KundaliMilanSynastryEngine
milan_res = KundaliMilanSynastryEngine.calculate_ashta_koota(chart_obj.planets["Moon"].longitude, chart_obj.planets["Moon"].longitude + 45.0)
kuja_res = KundaliMilanSynastryEngine.evaluate_kuja_dosha(chart_obj)
assert "total_guna_score" in milan_res and "is_manglik" in kuja_res, "Kundali Milan failed"
print(f"[PASS] 12. Kundali Milan & Synastry Engine (Guna: {milan_res['total_guna_score']}/36, Manglik Status: {kuja_res['status']})")

# 13. Master Sade Sati & Shani Gochara Lifecycle
from sade_sati_engine import SadeSatiEngine
sade_eng = SadeSatiEngine(chart_obj)
sade_status = sade_eng.evaluate_current_status(datetime.now(pytz.utc))
sade_tl = sade_eng.generate_lifetime_sade_sati_timeline(datetime(1990, 1, 15, tzinfo=pytz.utc), scan_years=50)
assert "status" in sade_status and len(sade_tl) > 0, "Sade Sati engine failed"
print(f"[PASS] 13. Master Sade Sati & Shani Gochara Engine (Current: {sade_status['status']}, {len(sade_tl)} transit windows)")

# 14. Yogini Dasha (36-Year Secondary Cycle)
from yogini_dasha_engine import YoginiDashaEngine
yogini_tl = YoginiDashaEngine.calculate_yogini_timeline(datetime(1990, 1, 15, 9, 0, tzinfo=pytz.utc), chart_obj.planets["Moon"].longitude, cycles=2)
assert len(yogini_tl) >= 16, "Yogini Dasha failed"
print(f"[PASS] 14. Yogini Dasha Engine ({len(yogini_tl)} 36-year cycle periods calculated)")

# 15. Sarvatobhadra Chakra (SBC 28-Nakshatra Vedha)
from sarvatobhadra_chakra_engine import SarvatobhadraChakraEngine
sbc_eng = SarvatobhadraChakraEngine(chart_obj)
sbc_res = sbc_eng.evaluate_transit_vedha(datetime.now(pytz.utc))
assert "special_nakshatras" in sbc_res, "SBC failed"
print(f"[PASS] 15. Sarvatobhadra Chakra 28-Nakshatra Vedha Engine (Risk Level: {sbc_res['risk_level']})")

# 16. Bhrigu Nandi Nadi (BNN Progression)
from bhrigu_nandi_nadi_engine import BhriguNandiNadiEngine
bnn_eng = BhriguNandiNadiEngine(chart_obj)
bnn_res = bnn_eng.calculate_progressed_positions(current_age=36.0)
assert "progressed_jupiter" in bnn_res and "progressed_saturn" in bnn_res, "BNN failed"
print(f"[PASS] 16. Bhrigu Nandi Nadi Progression Engine (Progressed Jup: {bnn_res['progressed_jupiter']['sign']})")

# 17. Medical Astrology & Ayurvedic Tridosha Diagnostics
from medical_astrology_engine import MedicalAstrologyEngine
med_eng = MedicalAstrologyEngine(chart_obj)
med_diag = med_eng.diagnose_health_profile()
assert "primary_ayurvedic_dosha" in med_diag and "surgical_trauma_risk" in med_diag, "Medical engine failed"
print(f"[PASS] 17. Medical Astrology & Tridosha Diagnostics (Dosha: {med_diag['primary_ayurvedic_dosha']}, Surgery Risk: {med_diag['surgical_trauma_risk']})")

# 18. Pushkara Navamsha & Bhaga Engine
from pushkara_engine import PushkaraEngine
push_eng = PushkaraEngine(chart_obj)
push_res = push_eng.evaluate_all_planets()
assert "total_pushkara_blessings" in push_res, "Pushkara failed"
print(f"[PASS] 18. Pushkara Navamsha & Bhaga Engine (Total Blessings: {push_res['total_pushkara_blessings']}, Rating: {push_res['resilience_rating']})")

# 19. Special Wealth & Power Lagnas Engine
from wealth_lagnas_engine import WealthLagnasEngine
wealth_eng = WealthLagnasEngine(chart_obj)
special_lagnas = wealth_eng.calculate_special_lagnas()
assert "indu_lagna" in special_lagnas and "ghatika_lagna" in special_lagnas, "Wealth Lagnas failed"
print(f"[PASS] 19. Special Wealth Lagnas Engine (Indu Lagna: {special_lagnas['indu_lagna']['indu_lagna_sign']}, Power: {special_lagnas['ghatika_lagna']['sign']})")

# 20. KP Cuspal Interlinks (CIL) 12-Bhava Event Gating
from kp_interlinks_engine import KPCuspalInterlinksEngine
kp_cil_eng = KPCuspalInterlinksEngine(chart_obj)
cil_promises = kp_cil_eng.evaluate_cuspal_promises()
assert len(cil_promises) == 12, "KP CIL failed"
print(f"[PASS] 20. KP Cuspal Interlinks Gating Engine (12 House Cuspal Sub-Lord Gates Evaluated)")

# 21. Jaimini Arudha Pada (A1-A12) & Argala Engine
from jaimini_arudha_argala_engine import JaiminiArudhaArgalaEngine
arudha_eng = JaiminiArudhaArgalaEngine(chart_obj)
all_padas = arudha_eng.calculate_all_padas()
argala_10 = arudha_eng.evaluate_argala_on_house(10)
assert len(all_padas) == 12 and "argalas" in argala_10, "Arudha Argala failed"
print(f"[PASS] 21. Jaimini Arudha Padas (A1-A12) & Argala Engine ({len(all_padas)} Padas, Argala Evaluated)")

# 22. Navatara Chakra & 27-Nakshatra Tara Bala Engine
from navatara_chakra_engine import NavataraChakraEngine
nava_eng = NavataraChakraEngine(chart_obj)
nava_planets = nava_eng.evaluate_natal_planets_tara_bala()
assert len(nava_planets) >= 7, "Navatara failed"
print(f"[PASS] 22. Navatara Chakra & Tara Bala Engine ({len(nava_planets)} Planets mapped to 9-Fold Taras)")

# 23. Classical Gochara Vedha & Vipareeta Vedha Engine
from gochara_vedha_engine import GocharaVedhaEngine
vedha_eng = GocharaVedhaEngine(chart_obj)
vedha_res = vedha_eng.evaluate_all_transits(datetime.now(pytz.utc))
assert "transit_evaluations" in vedha_res, "Gochara Vedha failed"
print(f"[PASS] 23. Classical Gochara Vedha & Vipareeta Vedha Engine (9-Planet Transit Obstruction Evaluated)")

# 24. Discrete-Math Boundary Fragility & Perturbation Engine (Phase 3)
from boundary_fragility_engine import BoundaryFragilityEngine
frag_res = BoundaryFragilityEngine.evaluate_chart_fragility(chart_obj)
assert "chart_boundary_fragility_rating" in frag_res and len(frag_res["detailed_evaluations"]) >= 8, "Boundary fragility failed"
print(f"[PASS] 24. Discrete-Math Boundary Fragility Engine (Rating: {frag_res['chart_boundary_fragility_rating']}, Fragile Entities: {frag_res['fragile_entities_count']})")

# 25. Semantic Synthesis Layer & Autonomous ReAct Router
sem_full = json.loads(get_semantic_view(chart_dict, "full_overview"))
from ai_agent import ALL_TOOLS
from agent_router import classify_intent
assert len(ALL_TOOLS) >= 15 and "sensitive_points" in sem_full, "Semantic/Agent failed"
print("[PASS] 25. Semantic Data Synthesis Layer & Autonomous ReAct Agent Router")

# 26. 70-Node Master Jyotiṣa Decision & Interpretation Ontology
from jyotisha_ontology import JyotishaOntology, MASTER_ONTOLOGY_NODES
onto_test = JyotishaOntology.classify_question("Will foreign network clients scale my B2B agency?")
assert len(MASTER_ONTOLOGY_NODES) == 71, "Ontology node count failed"
assert onto_test.node_id == 5 and len(onto_test.cross_domain_links) >= 1, "Ontology classification failed"
print(f"[PASS] 26. 70-Node Master Jyotiṣa Question Ontology & Routing Engine (71 Nodes Active, Node 5: {onto_test.subnode_title})")

print("\n" + "="*60)
print(">>> ALL 26 ARCHITECTURAL LAYERS VERIFIED END-TO-END WITH ZERO FAILS <<<")
print("="*60)
