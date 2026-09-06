from typing import Dict, Any

class Config:
    # Methodology Variants
    # ====================
    
    # HOUSE SYSTEM
    # "whole_sign": 1st house is the entire sign of the Ascendant.
    # "sripati": Exact degree-based cusps (Bhava Chalit).
    HOUSE_SYSTEM: str = "whole_sign"
    
    # TOPOCENTRIC VS GEOCENTRIC
    # Historically, Vedic astrology is Geocentric. The engine uses geocentric
    # coordinates by default. Do not change this unless required for specialized
    # astronomical research or localized moon transits.
    USE_TOPOCENTRIC: bool = False
    
    # RAHU/KETU ASPECTS
    # True: Rahu and Ketu aspect the 5th, 7th, and 9th houses from their position (Parashari variant).
    # False: Nodes do not cast aspects, they only amplify conjunctions and dispositors.
    NODES_CAST_ASPECTS: bool = True

    # NODE TYPE (Rahu/Ketu ephemeris model) -- CANONICAL for the Parashari/Lahiri stack.
    # "true": osculating True Node (swe.TRUE_NODE). This is the declared convention of
    #         the canonical chart engine (astrology_engine.calculate_chart_with_object),
    #         so every Parashari-context engine (transits, gochara, realtime, chakras)
    #         MUST use the same model or Rahu/Ketu longitudes disagree by up to ~1.6 deg,
    #         which can flip a nakshatra/pada near a boundary.
    # "mean": Mean Node (swe.MEAN_NODE).
    # NOTE: KP is a SEPARATE methodology and traditionally uses the Mean Node; kp_engine
    #       intentionally does NOT read this and is not affected by changing it.
    NODE_TYPE: str = "true"

    # AYANAMSHA (Zodiacal Precession Offset)
    # The canonical global setting for the classical Parashari/Jaimini stack.
    # Note: The system was previously documented as "True Chitra", but the code explicitly
    # uses SIDM_LAHIRI (True Chitra Paksha). We continue using Lahiri as the default.
    # KP uses Krishnamurti Ayanamsha independently.
    AYANAMSHA: str = "lahiri"
    
    @classmethod
    def ayanamsha_swe_id(cls):
        """Return the Swiss Ephemeris ayanamsha constant for the canonical stack."""
        import swisseph as swe
        mapping = {
            "lahiri": swe.SIDM_LAHIRI,
            "raman": swe.SIDM_RAMAN,
            "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
            "yukteshwar": getattr(swe, "SIDM_YUKTESHWAR", swe.SIDM_LAHIRI), 
            "true_chitra": getattr(swe, "SIDM_TRUE_CHITRA", swe.SIDM_LAHIRI)
        }
        return mapping.get(cls.AYANAMSHA.lower(), swe.SIDM_LAHIRI)

    @classmethod
    def node_swe_id(cls):
        """Return the Swiss Ephemeris node constant for the canonical Parashari stack."""
        import swisseph as swe
        return swe.TRUE_NODE if cls.NODE_TYPE == "true" else swe.MEAN_NODE
    
    # COMBUSTION THRESHOLDS
    # The distance from the Sun within which a planet is considered combust.
    COMBUSTION_THRESHOLDS: Dict[str, float] = {
        "Moon": 12.0,
        "Mars": 17.0,
        "Mercury": 14.0,
        "Jupiter": 11.0,
        "Venus": 10.0,
        "Saturn": 15.0
    }
    
    # CHARA KARAKAS
    # Parashari defaults to 7 (Sun to Saturn).
    # Jaimini uses either 7 or 8 (including Rahu). 
    USE_CHARA_KARAKAS: bool = False
    CHARA_KARAKA_SCHEME: int = 7 # 7 or 8
    
    @classmethod
    def get_combustion_threshold(cls, planet_name: str, is_retrograde: bool) -> float:
        base_threshold = cls.COMBUSTION_THRESHOLDS.get(planet_name, 0.0)
        # Retrograde planets often have a tighter orb of combustion (usually reduced by 2 degrees in classic texts)
        if is_retrograde and planet_name in ["Mercury", "Venus"]:
            return base_threshold - 2.0
        return base_threshold

    # EXECUTION MODES & GUARDRAILS
    # "client_safe": Bounded client-facing framing with disclaimers & crisis safety.
    # "unconstrained": Raw Grandmaster execution without boundaries or disclaimers.
    @classmethod
    def get_mode(cls) -> str:
        from modes import get_active_mode
        return get_active_mode()

    @classmethod
    def set_mode(cls, mode_name: str) -> str:
        from modes import set_active_mode
        return set_active_mode(mode_name)

