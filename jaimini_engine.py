from typing import Dict, List, Tuple
from vedic_models import Chart, Planet

class JaiminiEngine:
    """
    Dedicated engine for Jaimini Jyotisha concepts:
    Chara Karakas, Arudhas, Jaimini Drishti, and Chara Dasha.
    """
    
    ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    @staticmethod
    def _get_sign_index(sign: str) -> int:
        return JaiminiEngine.ZODIAC_SIGNS.index(sign)

    @staticmethod
    def calculate_chara_karakas(chart: Chart, use_8_karakas: bool = False) -> Dict[str, str]:
        """
        Determines the Chara Karakas ranked by ABSOLUTE longitude (not degree-in-sign).
        If use_8_karakas is False, uses 7 karakas (AK, AmK, BK, MK, PK, GK, DK) excluding Rahu.
        If use_8_karakas is True, uses 8 karakas (AK, AmK, BK, MK, PiK, PK, GK, DK) including Rahu
        (Rahu's effective longitude is measured in reverse: sign_start + (30 - degree_in_sign)).
        Returns a mapping of karaka name -> planet name, and tags chart.planets[name].chara_karaka.
        """
        ZOD = JaiminiEngine.ZODIAC_SIGNS

        def abs_lon(p: Planet, name: str) -> float:
            sign_start = ZOD.index(p.sign) * 30.0 if p.sign in ZOD else 0.0
            return sign_start + (30.0 - p.degree if name == "Rahu" else p.degree)

        if use_8_karakas:
            candidates = [(name, abs_lon(p, name)) for name, p in chart.planets.items()
                          if name not in ["Ketu", "Ascendant"]]
            karaka_names = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
        else:
            candidates = [(name, abs_lon(p, name)) for name, p in chart.planets.items()
                          if name not in ["Rahu", "Ketu", "Ascendant"]]
            karaka_names = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]

        # Sort by absolute longitude DESCENDING (highest = AK)
        candidates.sort(key=lambda x: x[1], reverse=True)

        mapping = {}
        for karaka, (planet_name, lon) in zip(karaka_names, candidates):
            mapping[karaka] = planet_name
            if planet_name in chart.planets:
                setattr(chart.planets[planet_name], "chara_karaka", karaka)
        return mapping

    @staticmethod
    def calculate_arudha_lagna(ascendant_sign: str, lord_sign: str) -> str:
        """
        Calculates AL (Arudha Lagna).
        Distance from Ascendant to Lord. Then same distance from Lord.
        Exceptions:
        - If AL falls in 1st house, it moves to 10th house.
        - If AL falls in 7th house, it moves to 4th house.
        """
        asc_idx = JaiminiEngine._get_sign_index(ascendant_sign)
        lord_idx = JaiminiEngine._get_sign_index(lord_sign)
        
        distance = (lord_idx - asc_idx) % 12
        al_idx = (lord_idx + distance) % 12
        
        # Jaimini Exceptions
        if al_idx == asc_idx:
            al_idx = (al_idx + 9) % 12  # Move to 10th
        elif al_idx == (asc_idx + 6) % 12:
            al_idx = (al_idx + 3) % 12  # Move to 4th
            
        return JaiminiEngine.ZODIAC_SIGNS[al_idx]

    @staticmethod
    def _get_stronger_co_lord(chart: Chart, sign: str, lord1: str, lord2: str) -> str:
        """
        Sanjay Rath's rules for dual lordship (Scorpio: Mars/Ketu, Aquarius: Saturn/Rahu):
        1. If one is in its own sign (the sign in question), take the OTHER lord.
        2. If both are elsewhere, the one with more planets in its sign is stronger.
        3. If equal, the one with higher longitude (degree) is stronger.
        """
        p1 = chart.planets[lord1]
        p2 = chart.planets[lord2]
        
        # Rule 1: If a lord is in the sign itself, it is ignored in favor of the other
        if p1.sign == sign and p2.sign != sign:
            return lord2
        if p2.sign == sign and p1.sign != sign:
            return lord1
            
        # Rule 2: Co-tenants (number of planets in the sign occupied by the lord)
        p1_occupants = sum(1 for p in chart.planets.values() if p.sign == p1.sign)
        p2_occupants = sum(1 for p in chart.planets.values() if p.sign == p2.sign)
        if p1_occupants > p2_occupants:
            return lord1
        if p2_occupants > p1_occupants:
            return lord2
            
        # Rule 3: Advanced degree (higher longitude)
        if p1.degree > p2.degree:
            return lord1
        return lord2

    @staticmethod
    def calculate_all_arudhas(chart: Chart) -> Dict[str, str]:
        """
        Calculates Arudha Padas for all 12 houses.
        Handles dual lordships for Scorpio (Mars/Ketu) and Aquarius (Saturn/Rahu).
        """
        arudhas = {}
        asc_idx = JaiminiEngine._get_sign_index(chart.ascendant_sign)
        
        for i in range(12):
            house_sign = JaiminiEngine.ZODIAC_SIGNS[(asc_idx + i) % 12]
            
            if house_sign == "Scorpio":
                lord_name = JaiminiEngine._get_stronger_co_lord(chart, house_sign, "Mars", "Ketu")
            elif house_sign == "Aquarius":
                lord_name = JaiminiEngine._get_stronger_co_lord(chart, house_sign, "Saturn", "Rahu")
            else:
                lord_name = chart.SIGN_LORDS[house_sign]
                
            lord_sign = chart.planets[lord_name].sign
            
            # Using the same formula for all Arudhas
            h_idx = JaiminiEngine._get_sign_index(house_sign)
            l_idx = JaiminiEngine._get_sign_index(lord_sign)
            
            dist = (l_idx - h_idx) % 12
            arudha_idx = (l_idx + dist) % 12
            
            if arudha_idx == h_idx:
                arudha_idx = (arudha_idx + 9) % 12
            elif arudha_idx == (h_idx + 6) % 12:
                arudha_idx = (arudha_idx + 3) % 12
                
            arudha_name = "AL" if i == 0 else "UL" if i == 11 else f"A{i+1}"
            arudhas[arudha_name] = JaiminiEngine.ZODIAC_SIGNS[arudha_idx]
            
        return arudhas

    @staticmethod
    def get_jaimini_drishti(sign: str) -> List[str]:
        """
        Returns list of signs that 'sign' aspects via Jaimini Rashi Drishti.
        Movable (0,3,6,9) aspects all Fixed (1,4,7,10) except adjacent.
        Fixed aspects all Movable except adjacent.
        Dual (2,5,8,11) aspects all other Dual.
        """
        idx = JaiminiEngine._get_sign_index(sign)
        modality = idx % 3 # 0=Movable, 1=Fixed, 2=Dual
        
        aspects = []
        if modality == 0:
            # Movable aspects Fixed (1, 4, 7, 10). Exclude adjacent (idx+1).
            fixed_idxs = [1, 4, 7, 10]
            adjacent = (idx + 1) % 12
            aspects = [i for i in fixed_idxs if i != adjacent]
        elif modality == 1:
            # Fixed aspects Movable (0, 3, 6, 9). Exclude adjacent (idx-1).
            movable_idxs = [0, 3, 6, 9]
            adjacent = (idx - 1) % 12
            aspects = [i for i in movable_idxs if i != adjacent]
        elif modality == 2:
            # Dual aspects all other Dual (2, 5, 8, 11)
            dual_idxs = [2, 5, 8, 11]
            aspects = [i for i in dual_idxs if i != idx]
            
        return [JaiminiEngine.ZODIAC_SIGNS[i] for i in aspects]

    @staticmethod
    def calculate_chara_dasha(chart: Chart) -> List[Dict]:
        """
        Calculates Chara Dasha duration according to standard K.N. Rao Jaimini rules.
        Signs 1,2,3 and 7,8,9 count Forward.
        Signs 4,5,6 and 10,11,12 count Backward.
        Exception: If lord is in the same sign, duration is 12 years.
        (Scorpio and Aquarius dual-lordship resolution omitted for brevity here, assuming primary lord)
        """
        dashas = []
        
        # 1,2,3 and 7,8,9 (0-indexed: 0,1,2 and 6,7,8)
        forward_signs = [0, 1, 2, 6, 7, 8]
        
        for sign in JaiminiEngine.ZODIAC_SIGNS:
            lord = chart.SIGN_LORDS[sign]
            # Simplification: if Scorpio, should evaluate Mars vs Ketu. If Aquarius, Saturn vs Rahu.
            # Using primary lord for now.
            lord_sign = chart.planets[lord].sign
            
            s_idx = JaiminiEngine._get_sign_index(sign)
            l_idx = JaiminiEngine._get_sign_index(lord_sign)
            
            if s_idx == l_idx:
                duration = 12
            elif s_idx in forward_signs:
                # Forward count
                dist = (l_idx - s_idx) % 12
                duration = dist
            else:
                # Backward count
                dist = (s_idx - l_idx) % 12
                duration = dist
                
            dashas.append({
                "sign": sign,
                "duration_years": duration
            })
            
        return dashas

    @staticmethod
    def analyze_domain_jaimini(chart: Chart, domain: str) -> Dict:
        """
        Independently evaluates an event using Jaimini methodology.
        """
        domain_lower = domain.lower()
        supporting = []
        contradicting = []
        
        # Helper to find planet by Chara Karaka
        def get_karaka(ck_label):
            return next((p for p in chart.planets.values() if p.chara_karaka == ck_label), None)
            
        if domain_lower in ["career", "job", "business"]:
            amk = get_karaka("AmK")
            ak = get_karaka("AK")
            al = chart.arudhas.get("AL")
            
            if amk:
                if amk.dignity in ["Exalted", "Own House", "Moolatrikona", "Friendly Sign", "Great Friend Sign"]:
                    supporting.append(f"Amatyakaraka (AmK) {amk.name} is well placed in {amk.dignity}, supporting career.")
                else:
                    contradicting.append(f"Amatyakaraka (AmK) {amk.name} is weak in {amk.dignity}, causing career friction.")
                    
                if ak:
                    # AmK conjunct or aspecting AK is a Jaimini Raja Yoga
                    if amk.house == ak.house:
                        supporting.append(f"AK ({ak.name}) and AmK ({amk.name}) are conjunct, forming a strong Jaimini Raja Yoga.")
                    else:
                        amk_aspects = JaiminiEngine.get_jaimini_drishti(amk.sign)
                        if ak.sign in amk_aspects:
                            supporting.append(f"AmK ({amk.name}) aspects AK ({ak.name}) via Rashi Drishti, forming a Jaimini Raja Yoga.")
                            
            if al and amk:
                if amk.sign == al or amk.sign in JaiminiEngine.get_jaimini_drishti(al):
                    supporting.append("AmK aspects Arudha Lagna (AL), boosting status.")
                    
        elif domain_lower in ["marriage", "relationship"]:
            dk = get_karaka("DK")
            ul = chart.arudhas.get("UL")
            
            if dk:
                if dk.dignity in ["Exalted", "Own House", "Moolatrikona", "Friendly Sign", "Great Friend Sign"]:
                    supporting.append(f"Darakaraka (DK) {dk.name} is well placed in {dk.dignity}, supporting relationships.")
                else:
                    contradicting.append(f"Darakaraka (DK) {dk.name} is weak in {dk.dignity}, causing relationship friction.")
                    
            if ul:
                # Find planets in or aspecting UL
                ul_idx = JaiminiEngine._get_sign_index(ul)
                for p in chart.planets.values():
                    p_idx = JaiminiEngine._get_sign_index(p.sign)
                    if p.sign == ul:
                        if p.name in ["Jupiter", "Venus", "Mercury", "Moon"]:
                            supporting.append(f"Benefic {p.name} is placed in Upapada Lagna (UL).")
                        elif p.name in ["Saturn", "Mars", "Sun", "Rahu", "Ketu"]:
                            contradicting.append(f"Malefic {p.name} is placed in Upapada Lagna (UL).")
                    elif ul in JaiminiEngine.get_jaimini_drishti(p.sign):
                        if p.name in ["Jupiter", "Venus", "Mercury", "Moon"]:
                            supporting.append(f"Benefic {p.name} aspects Upapada Lagna (UL) via Rashi Drishti.")
                        elif p.name in ["Saturn", "Mars", "Sun", "Rahu", "Ketu"]:
                            contradicting.append(f"Malefic {p.name} aspects Upapada Lagna (UL) via Rashi Drishti.")

        score = len(supporting) - len(contradicting)
        if len(supporting) > 1 and score > 0:
            confidence = "STRONG"
        elif len(contradicting) > 1 and score < 0:
            confidence = "WEAK"
        elif len(supporting) > 0 and len(contradicting) > 0:
            confidence = "MIXED"
        elif not supporting and not contradicting:
            confidence = "INSUFFICIENT"
        else:
            confidence = "MODERATE"
            
        return {
            "methodology": "JAIMINI",
            "supporting_evidence": supporting,
            "contradicting_evidence": contradicting,
            "confidence": confidence
        }
