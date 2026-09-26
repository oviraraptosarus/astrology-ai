"""
Desha-Kala-Patra (Contextual Reality Binding) & Orthogonal Contradiction Engine
================================================================================
1. Contextual Reality Binding: Automatically binds chart interpretations to lived reality.
   - Auto-loads known chart profiles (User, Partner, Sajal) without redundant questioning.
   - Provides non-demographic 5-point behavioral intake for new unknown charts.
2. Orthogonal Vector Decomposition: Resolves simultaneous Raja and Daridra yogas
   into independent axes (V_power vs V_friction) instead of naive scalar cancellation.
3. Temporal Circuit-Breakers: Maps when friction fault-lines proc during macro expansion eras.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

class DeshaKalaPatraEngine:
    
    # ── PERSISTENT REGISTRY OF KNOWN PROFILES (DO NOT RE-ASK) ───────────────────
    KNOWN_PROFILES = {
        "user_aug2008": {
            "name": "User (August 1, 2008)",
            "dob": "2008-08-01",
            "age": 18,
            "desha": {
                "jurisdiction": "India",
                "target_market": "US / EU / Global (100% Cross-Border Arbitrage)",
                "macro_environment": "High-velocity AI automation / B2B technology growth"
            },
            "kala": {
                "macro_era": "Ketu Mahadasha (2024-2031) -> Infrastructure & Scale",
                "financial_runway": "Bootstrap agency cashflow with high reinvestment rate",
                "phase_status": "Founding Sprint -> Multi-Crore Scale Window (June 2027)"
            },
            "patra": {
                "archetype": "The Sovereign Alchemist (Mars-AK, Leo 8th H, Rahu 1st H)",
                "institutional_reach_index": 85.0,
                "runway_weeks": 26,
                "resource_constraint_score": 35.0,
                "crisis_vector": "Vata_Spike (Hyper-focus building / strategic quarantine)",
                "action_velocity_hours": 4.0,
                "somatic_constitution": "Vata Primary (Nervous system sensitivity, dry/fast pacing)"
            }
        },
        "sajal_mar2006": {
            "name": "Sajal Kumar Mishra (March 3, 2006)",
            "dob": "2006-03-03",
            "age": 20,
            "desha": {
                "jurisdiction": "Hyderabad, India",
                "target_market": "SaaS / Developer Tooling / Omniroute proxy infrastructure",
                "macro_environment": "Global developer AI / API infrastructure"
            },
            "kala": {
                "macro_era": "Venus Mahadasha (2009-2029) -> Mercury Antardasha (2025-2028)",
                "financial_runway": "Micro-SaaS cashflow",
                "phase_status": "Active commercial monetization window"
            },
            "patra": {
                "archetype": "The Mercury Software Merchant (Bhagyank 5, Neechabhanga Raja)",
                "institutional_reach_index": 80.0,
                "runway_weeks": 20,
                "resource_constraint_score": 30.0,
                "crisis_vector": "Mercury_Adapt (Fast code pivots)",
                "action_velocity_hours": 6.0,
                "somatic_constitution": "Mercury / Pitta-Vata"
            }
        },
        "dad_may1975": {
            "name": "Dad (May 6, 1975)",
            "dob": "1975-05-06",
            "age": 51,
            "desha": {
                "jurisdiction": "Mandapeta, East Godavari, AP, India",
                "target_market": "Local/Regional stability",
                "macro_environment": "Established conventional infrastructure"
            },
            "kala": {
                "macro_era": "Jupiter Mahadasha -> Saturn Antardasha (Current)",
                "financial_runway": "Established structural foundation",
                "phase_status": "Mature operational stability"
            },
            "patra": {
                "archetype": "The Taurian Stabilizer (Mars-AK, Taurus Lagna)",
                "institutional_reach_index": 60.0,
                "runway_weeks": 52,
                "resource_constraint_score": 25.0,
                "crisis_vector": "Endurance_Grip (Steady, non-reactive processing)",
                "action_velocity_hours": 48.0,
                "somatic_constitution": "Kapha Dominant (Water/Tissue, structural density)"
            }
        },
        "mom_oct1980": {
            "name": "Mom (October 1, 1980)",
            "dob": "1980-10-01",
            "age": 46,
            "desha": {
                "jurisdiction": "Mandapeta, East Godavari, AP, India",
                "target_market": "Family and internal structural alignment",
                "macro_environment": "Domestic/Internal management"
            },
            "kala": {
                "macro_era": "Rahu Mahadasha -> Venus Antardasha (Current)",
                "financial_runway": "Dependent on/supporting family structure",
                "phase_status": "High-intensity developmental node"
            },
            "patra": {
                "archetype": "The Gemini Navigator (Mars-AK, Taurus Lagna, Moon-AmK)",
                "institutional_reach_index": 50.0,
                "runway_weeks": 52,
                "resource_constraint_score": 30.0,
                "crisis_vector": "Vocal_Process (Externalizing stress socially)",
                "action_velocity_hours": 12.0,
                "somatic_constitution": "Kapha Dominant"
            }
        },
        "bro_jun2003": {
            "name": "Brother (June 5, 2003)",
            "dob": "2003-06-05",
            "age": 23,
            "desha": {
                "jurisdiction": "Visakhapatnam, AP, India",
                "target_market": "Early career / skill acquisition",
                "macro_environment": "Transitioning to professional independence"
            },
            "kala": {
                "macro_era": "Moon Mahadasha -> Sun Antardasha (Current)",
                "financial_runway": "Building initial capital phase",
                "phase_status": "Visibility and authority establishment"
            },
            "patra": {
                "archetype": "The Scorpio Executor (Mercury-AK, Scorpio Lagna, Malavya Yoga)",
                "institutional_reach_index": 60.0,
                "runway_weeks": 12,
                "resource_constraint_score": 40.0,
                "crisis_vector": "Pitta_Strike (Aggressive correction/action)",
                "action_velocity_hours": 8.0,
                "somatic_constitution": "Pitta Dominant (Fire/Blood, high metabolic burn)"
            }
        },
        "jayendra_nov2007": {
            "name": "Jayendra (November 16, 2007)",
            "dob": "2007-11-16",
            "age": 18,
            "desha": {
                "jurisdiction": "Visakhapatnam, AP, India",
                "target_market": "Education / Early developmental trajectory",
                "macro_environment": "Pre-professional foundation"
            },
            "kala": {
                "macro_era": "Venus Mahadasha -> Saturn Antardasha (Current)",
                "financial_runway": "Pre-professional / Family backed",
                "phase_status": "Strict structural learning phase"
            },
            "patra": {
                "archetype": "The Leonine Strategist (Sun-AK, Leo Lagna, Budhaditya Yoga)",
                "institutional_reach_index": 40.0,
                "runway_weeks": 8,
                "resource_constraint_score": 45.0,
                "crisis_vector": "Pitta_Command (Attempting to enforce order)",
                "action_velocity_hours": 18.0,
                "somatic_constitution": "Pitta Dominant"
            }
        }
    }

    @classmethod
    def get_context_for_chart(cls, chart_name: str = "", dob: str = "", chart_obj = None) -> Dict[str, Any]:
        """
        Retrieves context:
        1. Checks known pre-verified profiles (User, Partner, Sajal) -> Returns immediately without asking.
        2. If unknown, checks local cache/database.
        3. If completely new, derives structural baseline from chart metrics with clean auto-defaults.
        """
        # Match by name or dob key
        search_key = f"{chart_name} {dob}".lower()
        
        if any(k in search_key for k in ["august", "2008-08-01", "user", "vamsi", "founder"]):
            return {"status": "PRE_VERIFIED_KNOWN_PROFILE", "source": "PERSISTENT_MEMORY", "context": cls.KNOWN_PROFILES["user_aug2008"]}
            
        if any(k in search_key for k in ["sajal", "2006-03-03", "mishra", "hyderabad"]):
            return {"status": "PRE_VERIFIED_KNOWN_PROFILE", "source": "PERSISTENT_MEMORY", "context": cls.KNOWN_PROFILES["sajal_mar2006"]}
            
        if any(k in search_key for k in ["dad", "father", "1975-05-06"]):
            return {"status": "PRE_VERIFIED_KNOWN_PROFILE", "source": "PERSISTENT_MEMORY", "context": cls.KNOWN_PROFILES["dad_may1975"]}
            
        if any(k in search_key for k in ["mom", "mother", "1980-10-01"]):
            return {"status": "PRE_VERIFIED_KNOWN_PROFILE", "source": "PERSISTENT_MEMORY", "context": cls.KNOWN_PROFILES["mom_oct1980"]}
            
        if any(k in search_key for k in ["bro", "brother", "2003-06-05"]):
            return {"status": "PRE_VERIFIED_KNOWN_PROFILE", "source": "PERSISTENT_MEMORY", "context": cls.KNOWN_PROFILES["bro_jun2003"]}
            
        if any(k in search_key for k in ["jayendra", "2007-11-16"]):
            return {"status": "PRE_VERIFIED_KNOWN_PROFILE", "source": "PERSISTENT_MEMORY", "context": cls.KNOWN_PROFILES["jayendra_nov2007"]}

        # Auto-derived defaults for unknown native
        birth_year = 2000
        if chart_obj and hasattr(chart_obj, "birth_time") and chart_obj.birth_time:
            birth_year = chart_obj.birth_time.year
        elif dob and len(dob) >= 4 and dob[:4].isdigit():
            birth_year = int(dob[:4])
            
        approx_age = datetime.now().year - birth_year

        auto_context = {
            "name": chart_name or "Unknown Native",
            "dob": dob or f"{birth_year}-01-01",
            "age": approx_age,
            "desha": {
                "jurisdiction": "Global / Digital",
                "target_market": "Modern Digital Economy",
                "macro_environment": "21st Century Technological Era"
            },
            "kala": {
                "macro_era": f"Age {approx_age} Life Cycle Stage",
                "financial_runway": "Standard Modern Baseline",
                "phase_status": "Active Career & Life Development"
            },
            "patra": {
                "archetype": "Modern Professional / Founder",
                "institutional_reach_index": 50.0,
                "runway_weeks": 12,
                "resource_constraint_score": 50.0,
                "crisis_vector": "Balanced_Response",
                "action_velocity_hours": 24.0,
                "somatic_constitution": "Tridosha Standard"
            }
        }
        return {"status": "AUTO_DERIVED_DEFAULT", "source": "STRUCTURAL_ESTIMATE", "context": auto_context}

    @staticmethod
    def decompose_orthogonal_yogas(chart_obj, yogas_found: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Orthogonal Vector Decomposition:
        Separates simultaneous Raja Yogas and Daridra/Arishta Yogas into distinct dimensions:
        - V_power: Institutional reach, gross asset capacity, authority, high-ticket scale.
        - V_friction: Liability, cash-burn, volatility, contractual turbulence.
        Never averages them to a flat median.
        """
        v_power_score = 0.0
        v_power_factors = []
        
        v_friction_score = 0.0
        v_friction_factors = []

        for y in yogas_found:
            name = y.get("name", "")
            reason = y.get("reason", "")
            fired = y.get("fired", True)
            if not fired:
                continue

            # Power Vector (Raja, Dhana, Vimala, Chamara, Yogada)
            if any(k in name.lower() for k in ["raja", "dhana", "vimala", "chaamara", "yogada", "budhaditya", "sambandha"]):
                weight = 2.5
                if "raja" in name.lower() or "dhana" in name.lower():
                    weight = 3.5
                v_power_score += weight
                v_power_factors.append(f"{name}: {reason[:80]}")

            # Friction Vector (Daridra, Kemadruma, Shakata, Dusthana lords, Combustion)
            if any(k in name.lower() for k in ["daridra", "kemadruma", "shakata", "curse", "dosha", "grahan"]):
                weight = 3.0
                v_friction_score += weight
                v_friction_factors.append(f"{name}: {reason[:80]}")

        # Add structural chart friction factors
        if hasattr(chart_obj, "planets"):
            for p_name, p in chart_obj.planets.items():
                if getattr(getattr(p, "combustion", None), "status", False):
                    v_friction_score += 1.5
                    v_friction_factors.append(f"{p_name} is Combust (Astangata)")
                if p.house in [6, 8, 12] and p_name in ["Mars", "Saturn", "Rahu"]:
                    v_friction_score += 1.0
                    v_friction_factors.append(f"Malefic {p_name} in House {p.house}")

        # Normalize to 0-10 scale
        v_power = min(10.0, round(v_power_score, 1))
        v_friction = min(10.0, round(v_friction_score, 1))

        # Assign Archetype
        if v_power >= 6.0 and v_friction >= 5.0:
            archetype = "The Leveraged Tycoon / High-Stakes Operator (Massive Reach paired with High Operational Friction & Volatility)"
        elif v_power >= 6.0 and v_friction < 5.0:
            archetype = "The Sovereign Monarch (Clean Unhindered Structural Authority)"
        elif v_power < 6.0 and v_friction >= 5.0:
            archetype = "The Besieged Operator (High Structural Friction requiring Radical Defense & Lean Restructuring)"
        else:
            archetype = "The Stable Practitioner (Balanced Low-Volatility Trajectory)"

        return {
            "v_power_capacity": v_power,
            "v_power_factors": v_power_factors,
            "v_friction_volatility": v_friction,
            "v_friction_factors": v_friction_factors,
            "synthesis_archetype": archetype,
            "mathematical_verdict": f"Orthogonal Non-Zero-Sum Tension: Power={v_power}/10 vs Friction={v_friction}/10"
        }

    @staticmethod
    def calculate_temporal_circuit_breakers(dasha_triad: str, orthogonal_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines if the active Dasha triad triggers the Power Expansion vector
        or activates a dormant Friction/Daridra circuit-breaker.
        """
        triad_lower = dasha_triad.lower()
        is_friction_proc = False
        friction_trigger_reason = None
        
        # Friction triggers on 8th/6th/12th lords, combust nodes, or Mars/Saturn friction triads
        if any(k in triad_lower for k in ["sun", "mars"]) and "8" in str(orthogonal_profile.get("v_friction_factors", [])):
            is_friction_proc = True
            friction_trigger_reason = "Sub-period activates 8th-house Mars/Sun tension: acute liquidity demands or fulfillment bottlenecks."
        elif "moon" in triad_lower and "combust" in str(orthogonal_profile.get("v_friction_factors", [])):
            is_friction_proc = True
            friction_trigger_reason = "Sub-period activates Combust 7th Moon: high client volume mixed with acute emotional friction and churn."

        return {
            "dasha_triad": dasha_triad,
            "is_power_expanding": orthogonal_profile.get("v_power_capacity", 0) >= 6.0,
            "is_friction_circuit_breaker_active": is_friction_proc,
            "operational_status": "HIGH_TENSION_EXPANSION" if (orthogonal_profile.get("v_power_capacity", 0) >= 6.0 and is_friction_proc) else "STEADY_GROWTH",
            "trigger_reason": friction_trigger_reason
        }
