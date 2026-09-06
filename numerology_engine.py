"""
Native Deterministic Numerology Engine
Implements:
1. Ank Jyotish (Indian Numerology based on Navagraha mappings)
2. Chaldean System (Cheiro method for Namank/Name Number)
3. Katapayadi System (Classical Sanskrit mapping for Nakshatras & Mantras)
"""

from typing import Dict, Any

# ==========================================
# 1. Core Reference Tables
# ==========================================

PLANET_NUMBERS = {
    1: "Sun", 
    2: "Moon", 
    3: "Jupiter", 
    4: "Rahu",
    5: "Mercury", 
    6: "Venus", 
    7: "Ketu", 
    8: "Saturn", 
    9: "Mars"
}

# The Chaldean (Cheiro) mapping (1-8 only, 9 is considered sacred/immaterial for lettering)
CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

# Katapayadi Sankhya
# Maps Sanskrit consonant groups to digits (0-9)
# vowels have 0 value unless they start a word (often effectively dropped in numerology sums).
# We implement a simplified direct transliteration map for Romanized input here.
KATAPAYADI_MAP = {
    'K': 1, 'T': 1, 'P': 1, 'Y': 1,
    'KH': 2, 'TH': 2, 'PH': 2, 'R': 2,
    'G': 3, 'D': 3, 'B': 3, 'L': 3,
    'GH': 4, 'DH': 4, 'BH': 4, 'V': 4,
    'NG': 5, 'N': 5, 'M': 5, 'SH': 5,
    'CH': 6, 'S': 6,  # S can be 7 depending on regional variation
    'CHH': 7, 'H': 8,
    'J': 8,
    'JH': 9, 'NY': 0
}

# ==========================================
# 2. Core Calculators
# ==========================================

def reduce_to_single_digit(n: int) -> int:
    """Reduces a number to a single digit (1-9)."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

class NumerologyEngine:
    
    @staticmethod
    def calculate_moolank(day: int) -> Dict[str, Any]:
        """
        Birth Day Number (1-31 -> 1-9)
        Rules the native's youth, nature, and day-to-day choices.
        """
        num = reduce_to_single_digit(day)
        return {
            "compound": day,
            "single": num,
            "ruler": PLANET_NUMBERS[num]
        }

    @staticmethod
    def calculate_bhagyank(day: int, month: int, year: int) -> Dict[str, Any]:
        """
        Destiny / Life Path Number (Full DOB sum -> 1-9)
        Rules the native's destiny, maturity, and unalterable karma.
        """
        total = sum(int(d) for d in f"{day:02d}{month:02d}{year:04d}")
        num = reduce_to_single_digit(total)
        return {
            "compound": total,
            "single": num,
            "ruler": PLANET_NUMBERS[num]
        }

    @staticmethod
    def calculate_namank_chaldean(name: str) -> Dict[str, Any]:
        """
        Chaldean Name Number.
        Provides the energetic frequency of the native's public identity.
        """
        clean_name = "".join([c for c in str(name).upper() if c in CHALDEAN_MAP])
        if not clean_name:
            return {"compound": 0, "single": 0, "ruler": "None"}
            
        compound = sum(CHALDEAN_MAP[c] for c in clean_name)
        single = reduce_to_single_digit(compound)
        return {
            "compound": compound,
            "single": single,
            "ruler": PLANET_NUMBERS[single]
        }

    @staticmethod
    def calculate_katapayadi_sum(name: str) -> int:
        """
        Basic Katapayadi sum for a romanized Sanskrit/Indian name.
        """
        total = 0
        name = name.upper()
        # Simplified parser
        for i in range(len(name)):
            char = name[i]
            # Try 2 chars
            if i < len(name) - 1 and name[i:i+2] in KATAPAYADI_MAP:
                total += KATAPAYADI_MAP[name[i:i+2]]
            elif char in KATAPAYADI_MAP:
                total += KATAPAYADI_MAP[char]
        return reduce_to_single_digit(total) if total > 0 else 0

    @staticmethod
    def generate_full_profile(day: int, month: int, year: int, name: str = "") -> Dict[str, Any]:
        moolank = NumerologyEngine.calculate_moolank(day)
        bhagyank = NumerologyEngine.calculate_bhagyank(day, month, year)
        
        # Check compatibility between Moolank and Bhagyank
        friendly_pairs = {
            1: [1, 2, 3, 5, 9],
            2: [1, 2, 3, 5],
            3: [1, 2, 3, 5, 7, 9],
            4: [1, 4, 5, 6, 7, 8],
            5: [1, 2, 3, 5, 6],
            6: [1, 4, 5, 6, 7, 8],
            7: [1, 3, 4, 5, 6, 7],
            8: [3, 4, 5, 6, 8],
            9: [1, 2, 3, 9]
        }
        
        m_num = moolank["single"]
        b_num = bhagyank["single"]
        is_friendly = b_num in friendly_pairs.get(m_num, [])
        
        profile = {
            "moolank": moolank,
            "bhagyank": bhagyank,
            "core_harmony": "FRIENDLY (Smooth destiny)" if is_friendly else "CONFLICTING (Friction/Struggle)",
        }
        
        if name:
            namank = NumerologyEngine.calculate_namank_chaldean(name)
            n_num = namank["single"]
            name_friendly = n_num in friendly_pairs.get(m_num, []) and n_num in friendly_pairs.get(b_num, [])
            
            profile["namank"] = namank
            profile["katapayadi_nama"] = NumerologyEngine.calculate_katapayadi_sum(name)
            profile["name_harmony"] = "ALIGNED" if name_friendly else "MISALIGNED (Consider Name Correction)"
            
        return profile
