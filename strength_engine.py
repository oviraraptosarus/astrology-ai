from vedic_models import Chart, Planet

class StrengthEngine:
    @staticmethod
    def calculate_shadbala(chart: Chart):
        StrengthEngine._calc_naisargika_bala(chart)
        StrengthEngine._calc_sthana_bala(chart)
        StrengthEngine._calc_dig_bala(chart)
        StrengthEngine._calc_kala_bala(chart)
        StrengthEngine._calc_cheshta_bala(chart)
        StrengthEngine._calc_drik_bala(chart)
        
        for p in chart.planets.values():
            if p.name in ["Rahu", "Ketu", "Ascendant"]:
                continue
                
            p.shadbala["total"] = round(sum([
                p.shadbala["sthana_bala"], p.shadbala["dig_bala"], 
                p.shadbala["kala_bala"], p.shadbala["cheshta_bala"],
                p.shadbala["naisargika_bala"], p.shadbala["drik_bala"]
            ]), 2)

    @staticmethod
    def _calc_naisargika_bala(chart: Chart):
        """
        Natural strength of planets. Always constant.
        Sun > Moon > Venus > Jupiter > Mercury > Mars > Saturn.
        Measured in Virupas (60 Virupas = 1 Rupa).
        """
        NAISARGIKA_VALUES = {
            "Sun": 60.00,
            "Moon": 51.43,
            "Venus": 42.85,
            "Jupiter": 34.28,
            "Mercury": 25.71,
            "Mars": 17.14,
            "Saturn": 8.57
        }
        for p_name, p in chart.planets.items():
            if p_name in NAISARGIKA_VALUES:
                p.shadbala["naisargika_bala"] = NAISARGIKA_VALUES[p_name]

    @staticmethod
    def _calc_sthana_bala(chart: Chart):
        """
        Positional Strength (Sthana Bala).
        Implementing Uchcha Bala (Exaltation strength), Ojayugmarasyamsa Bala, and Kendradi Bala.
        """
        # 1. Uchcha Bala (Max 60 virupas at exact exaltation, 0 at exact debilitation)
        EXALTATION_DEGREES = {
            "Sun": 10, "Moon": 33, "Mars": 298, 
            "Mercury": 165, "Jupiter": 95, "Venus": 357, "Saturn": 200
        }
        
        for p_name, p in chart.planets.items():
            if p_name not in EXALTATION_DEGREES:
                continue
                
            p_long = p.degree + (chart.get_sign_index(p.sign) * 30)
            exalt_deg = EXALTATION_DEGREES[p_name]
            debil_deg = (exalt_deg + 180) % 360
            
            # Distance from debilitation point / 3
            dist_from_debil = abs(p_long - debil_deg)
            dist_from_debil = min(dist_from_debil, 360 - dist_from_debil)
            uchcha_bala = dist_from_debil / 3.0
            
            # 2. Kendradi Bala
            if p.house in [1, 4, 7, 10]:
                kendradi_bala = 60.0
            elif p.house in [2, 5, 8, 11]:
                kendradi_bala = 30.0
            else:
                kendradi_bala = 15.0
                
            # 3. Ojayugmarasyamsa Bala (Odd/Even signs)
            # Venus and Moon get 15 Virupas in Even signs
            # Sun, Mars, Jupiter, Mercury, Saturn get 15 Virupas in Odd signs
            # Sign index: Aries (0) is Odd, Taurus (1) is Even, etc.
            is_odd_sign = (chart.get_sign_index(p.sign) % 2 == 0)
            
            oja_bala = 0.0
            if p_name in ["Moon", "Venus"]:
                if not is_odd_sign:
                    oja_bala = 15.0
            elif p_name in ["Sun", "Mars", "Jupiter", "Mercury", "Saturn"]:
                if is_odd_sign:
                    oja_bala = 15.0
                
            p.shadbala["sthana_bala"] = round(uchcha_bala + kendradi_bala + oja_bala, 2)

    @staticmethod
    def _calc_kala_bala(chart: Chart):
        """
        Temporal Strength (Kala Bala) - FULL Implementation.
        Nathonnatha Bala (Day/Night strength) + Tribhaga Bala + Paksha Bala + Dina Bala + Yuddha Bala.
        """
        if "Sun" not in chart.planets:
            return
            
        is_day_birth = 7 <= chart.planets["Sun"].house <= 12
        
        # Determine Paksha (fortnight): Moon waxing (Shukla) or waning (Krishna)
        sun_long = chart.planets["Sun"].degree + (chart.get_sign_index(chart.planets["Sun"].sign) * 30)
        moon_long = chart.planets["Moon"].degree + (chart.get_sign_index(chart.planets["Moon"].sign) * 30)
        moon_sun_dist = (moon_long - sun_long) % 360
        is_shukla_paksha = moon_sun_dist < 180  # Waxing
        
        for p_name, p in chart.planets.items():
            nathonnatha = 0.0
            if p_name == "Mercury":
                nathonnatha = 60.0
            elif p_name in ["Sun", "Jupiter", "Venus"]:
                nathonnatha = 60.0 if is_day_birth else 0.0
            elif p_name in ["Moon", "Mars", "Saturn"]:
                nathonnatha = 60.0 if not is_day_birth else 0.0
                
            # Tribhaga Bala
            tribhaga = 0.0
            if p_name == "Jupiter":
                tribhaga = 60.0
            else:
                sun_h = chart.planets["Sun"].house
                part = 1
                if sun_h in [11, 12, 1, 2]: part = 1
                elif sun_h in [9, 10, 3, 4]: part = 2
                elif sun_h in [7, 8, 5, 6]: part = 3
                
                if is_day_birth:
                    if part == 1 and p_name == "Mercury": tribhaga = 60.0
                    elif part == 2 and p_name == "Sun": tribhaga = 60.0
                    elif part == 3 and p_name == "Saturn": tribhaga = 60.0
                else:
                    if part == 1 and p_name == "Moon": tribhaga = 60.0
                    elif part == 2 and p_name == "Venus": tribhaga = 60.0
                    elif part == 3 and p_name == "Mars": tribhaga = 60.0
            
            # Paksha Bala (Fortnight Strength, max 60 virupas)
            # Benefics (Moon, Mercury, Jupiter, Venus) gain in Shukla Paksha
            # Malefics (Sun, Mars, Saturn) gain in Krishna Paksha
            paksha = 0.0
            moon_dist_from_full = abs(moon_sun_dist - 180)  # 0 at new moon, 180 at full moon
            waxing_phase = moon_sun_dist / 180.0  # 0..1 (new to full)
            
            benefics = ["Moon", "Mercury", "Jupiter", "Venus"]
            if p_name in benefics:
                if is_shukla_paksha:
                    paksha = 60.0 * waxing_phase  # Gains with waxing
            elif p_name in ["Sun", "Mars", "Saturn"]:
                if not is_shukla_paksha:
                    paksha = 60.0 * (1.0 - waxing_phase)  # Gains with waning
            
            # NOTE: no "Dina Bala" — not a BPHS component; the day/night rule is
            # already fully covered by Nathonnatha Bala above. Adding it double-counted
            # 60 virupas for Moon (night) / Saturn (day).

            # Yuddha Bala (Planetary War strength, max 60 virupas)
            yuddha = 0.0
            if p.planetary_war and p.planetary_war.get("in_war", False):
                if p.planetary_war.get("is_winner", False):
                    yuddha = 60.0
                else:
                    yuddha = 0.0
                    
            p.shadbala["kala_bala"] = round(nathonnatha + tribhaga + paksha + yuddha, 2)

    @staticmethod
    def _calc_cheshta_bala(chart: Chart):
        """
        Motional Strength (Cheshta Bala).
        Calculated using Cheshta Kendra.
        For outer planets (Mars, Jupiter, Saturn), Seeghrocca is the Sun.
        For inner planets (Mercury, Venus), Seeghrocca is also closely proxied by the Sun's longitude.
        Cheshta Kendra = Longitude of Sun - Longitude of Planet.
        """
        if "Sun" not in chart.planets:
            return
            
        sun_long = chart.planets["Sun"].degree + (chart.get_sign_index(chart.planets["Sun"].sign) * 30)
        
        for p_name, p in chart.planets.items():
            if p_name in ["Rahu", "Ketu", "Ascendant"]:
                continue
                
            if p_name in ["Sun", "Moon"]:
                # Sun and Moon do not have Cheshta Bala in the strict motional sense.
                # Ayana Bala (solstitial declination strength) serves as their Cheshta equivalent.
                import math
                obliquity = 23.4392911
                lon = p.degree + (chart.get_sign_index(p.sign) * 30)
                decl = math.degrees(math.asin(math.sin(math.radians(obliquity)) * math.sin(math.radians(lon))))
                ayana = abs(decl) / 23.4392911 * 60.0
                p.shadbala["cheshta_bala"] = round(ayana, 2)
                continue

            # Need planetary position and heliocentric position if Mercury or Venus
            # To get heliocentric, we need ephemeris or re-run calculation
            import swisseph as swe
            jd = swe.julday(chart.birth_time.year, chart.birth_time.month, chart.birth_time.day, chart.birth_time.hour + chart.birth_time.minute/60.0)
            
            p_lon = p.degree + (chart.get_sign_index(p.sign) * 30)
            
            # Determine Seeghrocca based on planet type
            if p_name in ["Mars", "Jupiter", "Saturn"]:
                # Outer planets: Seeghrocca is Sun (geocentric)
                res_sun, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
                seeghrocca = res_sun[0]
            else:
                # Inner planets: Seeghrocca is Heliocentric Longitude
                p_id = {"Mercury": swe.MERCURY, "Venus": swe.VENUS}[p_name]
                res_hel, _ = swe.calc_ut(jd, p_id, swe.FLG_SWIEPH | swe.FLG_HELCTR)
                seeghrocca = res_hel[0]
            
            # Cheshta Kendra = Seeghrocca - Planet_Geocentric
            ck = seeghrocca - p_lon
            if ck < 0:
                ck += 360.0
            if ck > 180.0:
                ck = 360.0 - ck
                
            # Cheshta Bala = Cheshta Kendra / 3
            p.shadbala["cheshta_bala"] = round(ck / 3.0, 2)

    @staticmethod
    def _calc_dig_bala(chart: Chart):
        """
        Directional Strength (Dig Bala).
        Sun & Mars: Max in 10th, Min in 4th.
        Jupiter & Mercury: Max in 1st, Min in 7th.
        Venus & Moon: Max in 4th, Min in 10th.
        Saturn: Max in 7th, Min in 1st.
        Exact calculation based on house cusps (simplified to Ascendant degree offsets for Whole Sign).
        """
        from config import Config
        
        DIG_BALA_MAX_HOUSES = {
            "Sun": 10, "Mars": 10,
            "Jupiter": 1, "Mercury": 1,
            "Venus": 4, "Moon": 4,
            "Saturn": 7
        }
        
        asc_deg_absolute = chart.ascendant_degree + (chart.get_sign_index(chart.ascendant_sign) * 30)
        
        for p_name, p in chart.planets.items():
            if p_name not in DIG_BALA_MAX_HOUSES:
                continue
                
            max_house = DIG_BALA_MAX_HOUSES[p_name]
            
            # Calculate the absolute degree of the max house cusp
            # 1st house cusp = asc_deg_absolute
            # each subsequent house is roughly +30 degrees
            max_cusp_deg = (asc_deg_absolute + ((max_house - 1) * 30)) % 360
            p_long = p.degree + (chart.get_sign_index(p.sign) * 30)
            
            # Angular distance between planet and its max power cusp
            dist = abs(p_long - max_cusp_deg)
            dist = min(dist, 360 - dist)
            
            # At min_dist = 0 (exactly on cusp), bala = 60
            # At min_dist = 180 (exactly opposite), bala = 0
            bala = ((180 - dist) / 180.0) * 60.0
            
            p.shadbala["dig_bala"] = round(bala, 2)

    @staticmethod
    def _calc_drik_bala(chart: Chart):
        """
        Aspectual Strength (Drik Bala).
        Standard Vedic partial aspect algorithm.
        """
        for p_name, p in chart.planets.items():
            if p_name in ["Rahu", "Ketu", "Ascendant"]:
                continue
                
            p_long = p.degree + (chart.get_sign_index(p.sign) * 30)
            total_drik_bala = 0.0
            
            for asp_name, asp_p in chart.planets.items():
                if asp_name in ["Rahu", "Ketu", "Ascendant"] or asp_name == p_name:
                    continue
                    
                asp_long = asp_p.degree + (chart.get_sign_index(asp_p.sign) * 30)
                d = p_long - asp_long
                if d < 0: d += 360
                
                aspect_virupas = 0.0
                if 30 <= d < 60:
                    aspect_virupas = (d - 30) / 2.0
                elif 60 <= d < 90:
                    aspect_virupas = (90 - d) + 15.0
                elif 90 <= d < 120:
                    aspect_virupas = (d - 90) / 2.0
                elif 120 <= d < 150:
                    aspect_virupas = (150 - d) * 2.0
                elif 150 <= d <= 180:
                    aspect_virupas = (d - 150) * 2.0
                
                # Special Additions for Outer Planets
                if asp_name == "Saturn" and (60 <= d < 90 or 270 <= d < 300):
                    aspect_virupas += 45.0
                elif asp_name == "Jupiter" and (120 <= d < 150 or 240 <= d < 270):
                    aspect_virupas += 30.0
                elif asp_name == "Mars" and (90 <= d < 120 or 210 <= d < 240):
                    aspect_virupas += 15.0
                    
                aspect_virupas = min(60.0, aspect_virupas)
                
                # Malefics give negative drik bala, benefics give positive
                if asp_name in ["Sun", "Mars", "Saturn"]:
                    aspect_virupas = -aspect_virupas
                    
                total_drik_bala += aspect_virupas
                
            # Drik bala is traditionally divided by 4 for the final Shadbala value
            p.shadbala["drik_bala"] = round(total_drik_bala / 4.0, 2)

    @staticmethod
    def calculate_vimsopaka_bala(chart: Chart):
        """
        Vimsopaka Bala (20-point strength system based on Shodashavarga).
        Calculates out of 20 points using BPHS weights.
        """
        # BPHS Shodashavarga weights summing to 20
        weights = {
            "D1": 3.5, "D2": 1.0, "D3": 1.0, "D4": 0.5,
            "D7": 0.5, "D9": 3.0, "D10": 0.5, "D12": 0.5,
            "D16": 2.0, "D20": 0.5, "D24": 0.5, "D27": 0.5,
            "D30": 1.0, "D40": 0.5, "D45": 0.5, "D60": 4.0
        }
        
        for p_name, p in chart.planets.items():
            if p_name in ["Rahu", "Ketu", "Ascendant"]:
                continue
                
            total_vimsopaka = 0.0
            for varga, weight in weights.items():
                if varga in p.vargas:
                    varga_sign = p.vargas[varga]
                    # Determine dignity in this varga
                    # Simplified for now: Own sign = 20 (x weight), Friend = 15, Neutral = 10, Enemy = 7
                    lord = chart.SIGN_LORDS.get(varga_sign)
                    
                    if lord == p_name:
                        pts = 20.0
                    elif lord in p.friendships.get("natural_friends", []):
                        pts = 15.0
                    elif lord in p.friendships.get("natural_neutrals", []):
                        pts = 10.0
                    elif lord in p.friendships.get("natural_enemies", []):
                        pts = 7.0
                    else:
                        pts = 10.0 # Default fallback
                        
                    total_vimsopaka += (pts / 20.0) * weight
            
            p.vimsopaka_bala = round(total_vimsopaka, 2)
            
            # Set Vargottama flag: true if D1 sign == D9 sign
            p.is_vargottama = (p.vargas.get("D1") == p.vargas.get("D9"))

    @staticmethod
    def calculate_bhava_bala(chart: Chart):
        """
        Bhava Bala (House Strength).
        1. Bhavadhipati Bala: Shadbala of the house lord.
        2. Bhava Dig Bala: Directional strength of the house.
        3. Bhava Drishti Bala: Aspectual strength on the house.
        """
        # Calculate Dig Bala for houses
        # 1st: Human signs, 4th: Water signs, 7th: Biped/Keeta, 10th: Quadruped
        human_signs = ["Gemini", "Virgo", "Libra", "Aquarius", "Sagittarius"] # Sagittarius 1st half is human, simplifying to whole sign for now
        water_signs = ["Cancer", "Pisces", "Capricorn"]
        quadruped_signs = ["Aries", "Taurus", "Leo"]
        keeta_signs = ["Scorpio"]
        
        asc_deg_absolute = chart.ascendant_degree + (chart.get_sign_index(chart.ascendant_sign) * 30)
        
        for i in range(1, 13):
            bhava_sign_idx = (chart.get_sign_index(chart.ascendant_sign) + i - 1) % 12
            bhava_sign = chart.ZODIAC_SIGNS[bhava_sign_idx]
            bhava_lord_str = chart.SIGN_LORDS.get(bhava_sign)
            lord_bala = chart.planets[bhava_lord_str].shadbala["total"] if bhava_lord_str in chart.planets else 0.0
            
            # Exact Bhava Dig Bala
            # Find the house of maximum power based on sign type
            if bhava_sign in human_signs:
                max_house = 1
            elif bhava_sign in water_signs:
                max_house = 4
            elif bhava_sign in keeta_signs:
                max_house = 7
            elif bhava_sign in quadruped_signs:
                max_house = 10
            else:
                max_house = 1 # Fallback
                
            max_cusp_deg = (asc_deg_absolute + ((max_house - 1) * 30)) % 360
            bhava_cusp_deg = (asc_deg_absolute + ((i - 1) * 30)) % 360
            
            dist = abs(bhava_cusp_deg - max_cusp_deg)
            dist = min(dist, 360 - dist)
            dig_bala = ((180 - dist) / 180.0) * 60.0
            
            # Bhava Drishti Bala (Exact Aspectual Strength to the House Cusp)
            total_drishti_bala = 0.0
            for asp_name, asp_p in chart.planets.items():
                if asp_name in ["Rahu", "Ketu", "Ascendant"]:
                    continue
                    
                asp_long = asp_p.degree + (chart.get_sign_index(asp_p.sign) * 30)
                d = bhava_cusp_deg - asp_long
                if d < 0: d += 360
                
                aspect_virupas = 0.0
                if 30 <= d < 60: aspect_virupas = (d - 30) / 2.0
                elif 60 <= d < 90: aspect_virupas = (90 - d) + 15.0
                elif 90 <= d < 120: aspect_virupas = (d - 90) / 2.0
                elif 120 <= d < 150: aspect_virupas = (150 - d) * 2.0
                elif 150 <= d <= 180: aspect_virupas = (d - 150) * 2.0
                
                # Special Additions for Outer Planets
                if asp_name == "Saturn" and (60 <= d < 90 or 270 <= d < 300): aspect_virupas += 45.0
                elif asp_name == "Jupiter" and (120 <= d < 150 or 240 <= d < 270): aspect_virupas += 30.0
                elif asp_name == "Mars" and (90 <= d < 120 or 210 <= d < 240): aspect_virupas += 15.0
                
                aspect_virupas = min(60.0, aspect_virupas)
                
                if asp_name in ["Sun", "Mars", "Saturn"]:
                    aspect_virupas = -aspect_virupas
                    
                total_drishti_bala += aspect_virupas
                
            drishti_bala = total_drishti_bala / 4.0
            
            # Bhava Bala = Bhavadhipati Bala + Bhava Dig Bala + Bhava Drishti Bala
            chart.bhava_bala[i] = round(lord_bala + dig_bala + drishti_bala, 2)
