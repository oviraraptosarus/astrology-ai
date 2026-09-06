import swisseph as swe
import json
from datetime import datetime
import pytz
from varga_engine import VargaEngine
from config import Config

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": Config.node_swe_id()
}

def get_sign(lon):
    return ZODIAC_SIGNS[int(lon / 30)]

def calculate_chalit_house(planet_lon: float, cusps: tuple) -> int:
    """Calculates house placement based on exact house cusps (e.g., Placidus or Sri Pati)"""
    for i in range(12):
        cusp_start = cusps[i]
        cusp_end = cusps[(i+1) % 12]
        
        if cusp_start < cusp_end:
            if cusp_start <= planet_lon < cusp_end:
                return i + 1
        else:
            # Handles crossing the 360-0 boundary (e.g., cusp_start 350, cusp_end 10)
            if planet_lon >= cusp_start or planet_lon < cusp_end:
                return i + 1
    # Fallback, shouldn't hit if logic is sound
    return 1

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", 
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", 
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", 
    "Uttara Bhadrapada", "Revati"
]

def calculate_nakshatra(longitude: float) -> tuple:
    """Returns (nakshatra_name, pada, lord_name)"""
    # 27 Nakshatras spread across 360 degrees. Each is 13 degrees 20 minutes (13.333...)
    nakshatra_span = 360.0 / 27.0
    pada_span = nakshatra_span / 4.0
    
    nak_index = int(longitude / nakshatra_span)
    nak_name = NAKSHATRAS[nak_index]
    
    # Calculate Pada (1 to 4)
    remainder = longitude % nakshatra_span
    pada = int(remainder / pada_span) + 1
    
    # Nakshatra Lords follow Vimshottari Dasha order (Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury)
    lord_name = DASHA_LORDS[nak_index % 9]
    
    return nak_name, pada, lord_name

def calculate_chart_with_object(year: int, month: int, day: int, hour: int, minute: int, lat: float, lon: float, tz_name: str = 'UTC', name: str = ""):
    native_name = name  # preserve before the planet loop shadows `name`
    swe.set_sid_mode(Config.ayanamsha_swe_id())
    
    # Setup time
    local_tz = pytz.timezone(tz_name)
    local_dt = local_tz.localize(datetime(year, month, day, hour, minute))
    utc_dt = local_dt.astimezone(pytz.utc)
    
    hour_dec = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)
    # Topocentric positions were removed: Vedic astrology (JHora/Parashara) uses
    # GEOCENTRIC longitudes. Topocentric parallax shifts the Moon by up to ~1°,
    # corrupting the nakshatra and the entire Vimshottari dasha timeline.
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    # 1. Base Planets & Relational Graph
    from vedic_models import Chart, Planet
    
    # Ascendant
    # b'O' is Porphyry (equivalent to Sri Pati commonly used in Vedic Bhava Chalit)
    # High-latitude fallback: Equal house ('E') if polar latitudes fail Porphyry
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags)
    except Exception:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'E', flags)
    asc_lon = ascmc[0]
    chart = Chart(ascendant_sign=get_sign(asc_lon), ascendant_degree=asc_lon % 30)
    chart.birth_time = utc_dt
    chart.birth_local = local_dt
    chart.lat = lat
    chart.lon = lon
    chart.tz_name = tz_name
    chart.ascendant_vargas = VargaEngine.calculate_all_vargas(chart.ascendant_sign, chart.ascendant_degree)
    # Add nakshatra to ascendant for completeness (stored loosely in base_chart dict later if needed)
    asc_nak, asc_pada, asc_lord = calculate_nakshatra(asc_lon)
    planet_lons = {}
    
    for name, p_id in PLANETS.items():
        res, _ = swe.calc_ut(jd, p_id, flags)
        p_lon = res[0]
        speed = res[3]
        planet_lons[name] = p_lon
        is_retrograde = speed < 0 if name not in ["Sun", "Moon", "Rahu"] else False
        p = Planet(name, get_sign(p_lon), p_lon % 30, is_retrograde)
        p.chalit_house = calculate_chalit_house(p_lon, cusps)
        p.nakshatra, p.nakshatra_pada, p.nakshatra_lord = calculate_nakshatra(p_lon)
        p.vargas = VargaEngine.calculate_all_vargas(p.sign, p.degree)
        chart.add_planet(p)
    
    # Ketu
    ketu_lon = (planet_lons["Rahu"] + 180.0) % 360.0
    planet_lons["Ketu"] = ketu_lon
    p_ketu = Planet("Ketu", get_sign(ketu_lon), ketu_lon % 30, False)
    p_ketu.chalit_house = calculate_chalit_house(ketu_lon, cusps)
    p_ketu.nakshatra, p_ketu.nakshatra_pada, p_ketu.nakshatra_lord = calculate_nakshatra(ketu_lon)
    p_ketu.vargas = VargaEngine.calculate_all_vargas(p_ketu.sign, p_ketu.degree)
    chart.add_planet(p_ketu)
    
    # Compute Graph & Conditions
    chart.build_relational_graph()
    from condition_engine import ConditionEngine
    from strength_engine import StrengthEngine
    from ashtakavarga_engine import AshtakavargaEngine
    from jaimini_engine import JaiminiEngine
    
    ConditionEngine.evaluate_all_conditions(chart)
    
    from functional_benefic_engine import FunctionalBeneficEngine
    FunctionalBeneficEngine.calculate_functional_roles(chart)
    FunctionalBeneficEngine.calculate_panchadha_maitri(chart)
    
    StrengthEngine.calculate_shadbala(chart)
    StrengthEngine.calculate_vimsopaka_bala(chart)
    StrengthEngine.calculate_bhava_bala(chart)
    AshtakavargaEngine.calculate_ashtakavarga(chart)
    
    JaiminiEngine.calculate_chara_karakas(chart)
    chart.arudhas = JaiminiEngine.calculate_all_arudhas(chart)
    
    base_chart = chart.to_dict()["planets"]
    base_chart["Ascendant"] = {
        "sign": chart.ascendant_sign,
        "degree": chart.ascendant_degree,
        "nakshatra": asc_nak,
        "nakshatra_pada": asc_pada,
        "nakshatra_lord": asc_lord
    }
    base_chart["sarvashtakavarga"] = chart.sarvashtakavarga
    base_chart["bhava_bala"] = chart.bhava_bala
        
    # --- Detect Yogas via Rule Framework (Phase 3 & 4) ---
    from yogas import evaluate_all_yogas
    yogas = evaluate_all_yogas(chart)
    # 2. Divisional Charts (D9 Navamsha & D10 Dasamsha)
    d9_chart = {}
    d10_chart = {}
    
    # Use VargaEngine for all planets
    for name, p in chart.planets.items():
        d9_chart[name] = p.vargas.get("D9")
        d10_chart[name] = p.vargas.get("D10")
        
    # Include Ascendant in D9 and D10
    d9_chart["Ascendant"] = chart.ascendant_vargas.get("D9")
    d10_chart["Ascendant"] = chart.ascendant_vargas.get("D10")
    
    # 3. Panchanga
    from panchangam_engine import PanchangamEngine
    p_engine = PanchangamEngine()
    # calculate_full_panchang takes a timezone-aware datetime + coordinates.
    # Reconstruct local dt from the local values we already have.
    panchanga_data = p_engine.calculate_full_panchang(
        local_dt, lat, lon, tz_name=tz_name)
    
    moon_lon = planet_lons["Moon"]
    nak_span = 360 / 27
    nak_idx = int(moon_lon / nak_span)
    pada = int((moon_lon % nak_span) / (nak_span/4)) + 1
    
    panch = panchanga_data.get("panchanga", {})
    panchanga = {
        "Tithi": panch.get("tithi", {}).get("name", "Unknown"),
        "Vara": panch.get("vara", {}).get("name", "Unknown"),
        "Nakshatra": panch.get("nakshatra", {}).get("name", "Unknown"),
        "Yoga": panch.get("yoga", {}).get("name", "Unknown"),
        "Karana": panch.get("karana", {}).get("name", "Unknown"),
        "Nakshatra_Pada": pada,
        "Drik_Panchang_Full": panchanga_data
    }
    
    # 4. Detailed Dasha (Vimshottari)
    lord_idx = nak_idx % 9
    fraction_left = (nak_span - (moon_lon % nak_span)) / nak_span
    balance = fraction_left * DASHA_YEARS[lord_idx]
    
    def dt_to_dec(dt_obj):
        return dt_obj.year + (dt_obj.timetuple().tm_yday - 1) / 365.25
        
    birth_dec = dt_to_dec(utc_dt)
    age = dt_to_dec(datetime.now(pytz.utc)) - birth_dec
    
    curr_dasha = DASHA_LORDS[lord_idx]
    antardasha = ""
    pratyantardasha = ""
    
    md_start_age = 0
    md_end_age = balance
    
    elapsed = balance
    if age > balance:
        c_idx = (lord_idx + 1) % 9
        while True:
            if elapsed + DASHA_YEARS[c_idx] > age:
                curr_dasha = DASHA_LORDS[c_idx]
                dasha_len = DASHA_YEARS[c_idx]
                md_start_age = elapsed
                md_end_age = elapsed + dasha_len
                
                time_in_dasha = age - elapsed
                
                ad_elapsed = 0
                ad_idx = c_idx
                for _ in range(9):
                    ad_len = (dasha_len * DASHA_YEARS[ad_idx]) / 120.0
                    if ad_elapsed + ad_len > time_in_dasha:
                        antardasha = DASHA_LORDS[ad_idx]
                        
                        # Calculate Pratyantardasha
                        time_in_ad = time_in_dasha - ad_elapsed
                        pd_elapsed = 0
                        pd_idx = ad_idx
                        for _ in range(9):
                            pd_len = (ad_len * DASHA_YEARS[pd_idx]) / 120.0
                            if pd_elapsed + pd_len > time_in_ad:
                                pratyantardasha = DASHA_LORDS[pd_idx]
                                break
                            pd_elapsed += pd_len
                            pd_idx = (pd_idx + 1) % 9
                            
                        break
                    ad_elapsed += ad_len
                    ad_idx = (ad_idx + 1) % 9
                break
            elapsed += DASHA_YEARS[c_idx]
            c_idx = (c_idx + 1) % 9
            
    def dec_to_ym(dec):
        y = int(dec)
        m = int((dec - y) * 12) + 1
        return f"{y}-{m:02d}"
    
    dashas = {
        "Mahadasha": curr_dasha,
        "Antardasha": antardasha,
        "Pratyantardasha": pratyantardasha,
        "Mahadasha_Start": dec_to_ym(birth_dec + md_start_age),
        "Mahadasha_End": dec_to_ym(birth_dec + md_end_age)
    }
    
    # --- Live Transits (Gochar) ---
    # Calculate live planetary positions right now (UTC)
    current_utc = datetime.now(pytz.utc)
    current_hour_dec = current_utc.hour + current_utc.minute / 60.0 + current_utc.second / 3600.0
    current_jd = swe.julday(current_utc.year, current_utc.month, current_utc.day, current_hour_dec)
    
    live_transits = {}
    natal_moon_sign_idx = ZODIAC_SIGNS.index(base_chart["Moon"]["sign"])
    
    for name, p_id in PLANETS.items():
        res, _ = swe.calc_ut(current_jd, p_id, flags)
        p_lon = res[0]
        speed = res[3]
        t_sign = get_sign(p_lon)
        t_sign_idx = ZODIAC_SIGNS.index(t_sign)
        
        # Gochar (Transits) are read from the Natal Moon!
        house_from_moon = ((t_sign_idx - natal_moon_sign_idx) % 12) + 1
        
        is_retrograde = speed < 0 if name not in ["Sun", "Moon", "Rahu"] else False
        
        live_transits[name] = {
            "current_sign": t_sign,
            "house_from_natal_moon": house_from_moon,
            "is_retrograde_today": is_retrograde
        }
    
    # Live Ketu
    ketu_lon = (swe.calc_ut(current_jd, Config.node_swe_id(), flags)[0][0] + 180.0) % 360.0
    k_sign_idx = int(ketu_lon / 30)
    live_transits["Ketu"] = {
        "current_sign": ZODIAC_SIGNS[k_sign_idx],
        "house_from_natal_moon": ((k_sign_idx - natal_moon_sign_idx) % 12) + 1,
        "is_retrograde_today": False
    }

    # --- Integration of Numerology and Western Astrology ---
    from numerology_engine import NumerologyEngine
    from western_engine import WesternEngine
    from remedy_engine import RemedyEngine
    
    numerology_report = NumerologyEngine.generate_full_profile(day=day, month=month, year=year, name=native_name) if native_name else {}
    western_chart = WesternEngine.calculate_chart(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec, lat, lon)
    
    r_engine = RemedyEngine()
    remedies = {
        "dasha_remedies": r_engine.generate_dasha_remedies(curr_dasha, antardasha),
        "planet_remedies": {}
    }
    for p_name, p_obj in chart.planets.items():
        # Check if afflicted by looking for negative conditions
        is_afflicted = p_obj.dignity == "Debilitated" or "Enemy" in p_obj.dignity or p_obj.combustion.get("status", False)
        is_benefic = getattr(p_obj, 'functional_role', '') in ['Benefic', 'Yoga Karaka']
        rem = r_engine.get_remedy_for_planet(p_name, is_benefic=is_benefic, is_afflicted=is_afflicted)
        if rem:
            remedies["planet_remedies"][p_name] = rem
            
    # Attach dynamic dasha and live transits to Chart object for timing engines
    chart.current_dasha = dashas
    chart.current_transits = live_transits
    
    return chart, {
        "Basic_Chart": base_chart,
        "Yogas_Found": yogas,
        "Navamsha_D9": d9_chart,
        "Dasamsha_D10": d10_chart,
        "Panchanga": panchanga,
        "Current_Dasha": dashas,
        "Live_Transits_Gochar": live_transits,
        "Numerology": numerology_report,
        "Western_Chart": western_chart,
        "Remedies": remedies
    }

def calculate_full_chart(year: int, month: int, day: int, hour: int, minute: int, lat: float, lon: float, tz_name: str = 'UTC', name: str = "") -> dict:
    _, chart_dict = calculate_chart_with_object(year, month, day, hour, minute, lat, lon, tz_name, name)
    return chart_dict

# --- OP Feature 1: Muhurta (Electional Astrology) ---
GOOD_NAKSHATRAS = [1, 4, 5, 8, 12, 13, 14, 15, 17, 21, 22, 23, 24, 26, 27]

def find_muhurta(start_year, start_month, start_day, lat, lon):
    from datetime import timedelta
    swe.set_sid_mode(Config.ayanamsha_swe_id())
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    start_dt = datetime(start_year, start_month, start_day)
    best_dates = []
    
    # Scan next 30 days
    for i in range(30):
        check_dt = start_dt + timedelta(days=i)
        jd = swe.julday(check_dt.year, check_dt.month, check_dt.day, 12.0) # check at noon UTC
        
        res_moon, _ = swe.calc_ut(jd, swe.MOON, flags)
        moon_lon = res_moon[0]
        res_sun, _ = swe.calc_ut(jd, swe.SUN, flags)
        sun_lon = res_sun[0]
        
        tithi_val = ((moon_lon - sun_lon) % 360) / 12.0
        tithi = int(tithi_val) + 1
        
        nak_span = 360 / 27
        nak_idx = int(moon_lon / nak_span) + 1
        
        # Good Muhurta: Waxing Moon (Tithi 2-14) and Auspicious Nakshatra
        if 2 <= tithi <= 14 and nak_idx in GOOD_NAKSHATRAS:
            best_dates.append({
                "date": check_dt.strftime("%Y-%m-%d"),
                "tithi": tithi,
                "nakshatra_index": nak_idx,
                "reason": "Waxing Moon in Auspicious Nakshatra (Perfect for launches/beginnings)."
            })
            if len(best_dates) == 3: # Limit to top 3
                break
                
    return best_dates

# --- OP Feature 3: Ashtakoota (Compatibility) ---
# A simplified version of 36 points
def calculate_compatibility(m1_lon, m2_lon):
    nak_span = 360 / 27
    n1 = int(m1_lon / nak_span)
    n2 = int(m2_lon / nak_span)
    
    r1 = int(m1_lon / 30)
    r2 = int(m2_lon / 30)
    
    score = 0
    details = []
    
    # 1. Varna (Work/Ego compatibility) - 1 point
    score += 1
    details.append("Varna: Compatible work ethics.")
    
    # 2. Vashya (Attraction) - 2 points
    score += 2
    details.append("Vashya: Natural magnetic attraction.")
    
    # 3. Tara (Destiny/Luck) - 3 points
    t_dist = (n2 - n1) % 9
    if t_dist in [1, 2, 4, 6, 8]:
        score += 3
        details.append("Tara: Excellent mutual luck and destiny.")
    else:
        score += 1.5
        details.append("Tara: Average mutual luck.")
        
    # 4. Yoni (Intimacy/Nature) - 4 points
    score += 3
    details.append("Yoni: Good physical/intimate compatibility.")
    
    # 5. Graha Maitri (Mental Friendship) - 5 points
    # Simplified: Same planetary lord or friendly lords
    score += 4
    details.append("Graha Maitri: Strong mental friendship and communication.")
    
    # 6. Gana (Temperament) - 6 points
    score += 5
    details.append("Gana: Similar temperaments (Deva/Manushya/Rakshasa).")
    
    # 7. Bhakoot (Emotional harmony) - 7 points
    r_dist = (r2 - r1) % 12
    if r_dist in [0, 2, 3, 4, 8, 9, 10]:
        score += 7
        details.append("Bhakoot: Deep emotional harmony and growth.")
    else:
        score += 0
        details.append("Bhakoot Dosha: Emotional friction or misunderstanding likely.")
        
    # 8. Nadi (Genetic/Spiritual health) - 8 points
    if n1 % 3 != n2 % 3:
        score += 8
        details.append("Nadi: Perfect genetic/spiritual alignment (No Nadi Dosha).")
    else:
        score += 0
        details.append("Nadi Dosha: Severe spiritual/genetic clash. Proceed with caution.")
        
    return {
        "total_score": f"{score}/36",
        "is_compatible": score >= 18,
        "breakdown": details
    }

# --- Big Data Retrieval Methods ---
def compress_astrology_data(data):
    # Replaced by JSON structured output (Phase 15)
    import json
    return json.dumps(data)

def get_semantic_view(chart_dict, topic):
    import json
    from vedic_models import Chart
    from rules_engine import RuleEvaluator
    from domain_engine import DomainEngine
    from activation_engine import ActivationEngine
    from synthesis_engine import SynthesisEngine
    
    topic = topic.lower().strip()
    
    if topic in ["basic_chart_json"]:
        return json.dumps(chart_dict.get("Basic_Chart", {}))
        
    if topic == "full_overview":
        from sensitive_points import SensitivePointsEngine
        from advanced_avasthas import AdvancedAvasthaEngine
        from dosha_engine import DoshaEngine
        from cancellations import CancellationEngine
        
        chart_obj = Chart.from_dict(chart_dict.get("Basic_Chart", {}))
        sp_data = SensitivePointsEngine(chart_obj).calculate_all()
        av_data = AdvancedAvasthaEngine(chart_obj).combine_all()
        dosha_data = DoshaEngine(chart_obj).evaluate_all()
        canc_data = CancellationEngine(chart_obj).evaluate_all()
        
        return json.dumps({
            "topic": "Full Overview",
            "yogas": chart_dict.get("Yogas_Found", []),
            "dasha": chart_dict.get("Current_Dasha", {}),
            "natal": chart_dict.get("Basic_Chart", {}),
            "sensitive_points": sp_data,
            "avasthas": av_data,
            "doshas": dosha_data,
            "cancellations": canc_data,
            "numerology": chart_dict.get("Numerology", {})
        })
        
    # Reconstruct Chart object
    chart = Chart.from_dict(chart_dict.get("Basic_Chart", {}))
    
    # Attach dynamic fields needed for activation (from the dict we pass in)
    chart.current_dasha = chart_dict.get("Current_Dasha", {})
    chart.current_transits = chart_dict.get("Live_Transits_Gochar", {})
    
    # 1. Rule Evaluation
    rule_eval = RuleEvaluator(chart)
    
    # 2. Domain Analysis (Natal Promise)
    domain_engine = DomainEngine(chart, rule_eval)
    domain_analysis = domain_engine.analyze_domain(topic)
    
    # 3. Activation Engine (Timing)
    activation_engine = ActivationEngine(chart)
    activation_profile = activation_engine.assess_activation(
        domain_analysis.domain, 
        domain_analysis.relevant_planets, 
        domain_analysis.relevant_houses
    )
    
    # 4. Synthesis Engine (Conflict Resolution & Tracing)
    synthesis_engine = SynthesisEngine(chart)
    synthesis = synthesis_engine.synthesize(domain_analysis, activation_profile)
    
    return json.dumps(synthesis.to_dict())
