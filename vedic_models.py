from typing import List, Dict, Optional
import json

class Planet:
    def __init__(self, name: str, sign: str, degree: float, retrograde: bool):
        self.name = name
        self.sign = sign
        self.degree = round(degree, 2)
        self.retrograde = retrograde
        
        # Will be populated during relational mapping
        self.house: int = 0
        self.chalit_house: int = 0
        self.dignity: str = "Neutral"
        self.owns_houses: List[int] = []
        self.friendships: Dict[str, List[str]] = {}
        self.compound_friendships: Dict[str, List[str]] = {}
        self.functional_role: str = "" # Benefic, Malefic, Neutral, Yoga Karaka
        self.detailed_functional_roles: List[str] = [] # e.g. ["Maraka", "Badhaka"]
        self.dispositor: Optional[str] = None
        self.aspects_houses: List[int] = []
        self.aspected_by: List[str] = []
        self.conjunct_with: List[str] = []
        
        # Phase 8 Additions (Nakshatras)
        self.nakshatra: str = ""
        self.nakshatra_pada: int = 1
        self.nakshatra_lord: str = ""
        
        # Vargas
        self.vargas: Dict[str, str] = {}
        
        # Phase 1 Additions (Conditions & Strength)
        self.combustion: Dict = {"status": False, "sun_distance": None, "threshold": None}
        self.planetary_war: Dict = {"in_war": False, "with_planet": None, "is_winner": False}
        self.avasthas: Dict = {"balaadi": "Unknown"}
        self.friendships: Dict = {"natural_friends": [], "natural_enemies": [], "natural_neutrals": []}
        self.shadbala: Dict = {
            "sthana_bala": 0.0,
            "dig_bala": 0.0,
            "kala_bala": 0.0,
            "cheshta_bala": 0.0,
            "naisargika_bala": 0.0,
            "drik_bala": 0.0,
            "total": 0.0,
            "is_partial": False
        }
        self.vimsopaka_bala: float = 0.0
        
        # Phase 6 Additions (Karakas)
        self.natural_karakas: List[str] = []
        self.chara_karaka: Optional[str] = None
        
        # Phase 7 Additions (Dispositors)
        self.dispositor_chain: List[str] = []
        self.is_parivartana: bool = False

    @property
    def longitude(self) -> float:
        zodiac = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        sign_idx = zodiac.index(self.sign) if self.sign in zodiac else 0
        return (sign_idx * 30.0) + self.degree

    def to_dict(self):
        return {
            "planet": self.name,
            "sign": self.sign,
            "degree": self.degree,
            "house": self.house,
            "chalit_house": self.chalit_house,
            "retrograde": self.retrograde,
            "dignity": self.dignity,
            "owns_houses": self.owns_houses,
            "dispositor": self.dispositor,
            "aspects_houses": self.aspects_houses,
            "aspected_by": self.aspected_by,
            "conjunct_with": self.conjunct_with,
            "nakshatra": self.nakshatra,
            "nakshatra_pada": self.nakshatra_pada,
            "nakshatra_lord": self.nakshatra_lord,
            "combustion": self.combustion,
            "planetary_war": self.planetary_war,
            "avasthas": self.avasthas,
            "friendships": self.friendships,
            "compound_friendships": getattr(self, "compound_friendships", {}),
            "functional_role": getattr(self, "functional_role", ""),
            "detailed_functional_roles": getattr(self, "detailed_functional_roles", []),
            "shadbala": self.shadbala,
            "natural_karakas": self.natural_karakas,
            "chara_karaka": self.chara_karaka,
            "dispositor_chain": self.dispositor_chain,
            "is_parivartana": self.is_parivartana,
            "vimsopaka_bala": self.vimsopaka_bala,
            "vargas": self.vargas
        }

class Chart:
    def __init__(self, ascendant_sign: str, ascendant_degree: float):
        self.ascendant_sign = ascendant_sign
        self.ascendant_degree = round(ascendant_degree, 2)
        self.ascendant_vargas: Dict[str, str] = {}
        self.planets: Dict[str, Planet] = {}
        
        # Ashtakavarga structures
        self.sarvashtakavarga: Dict[int, int] = {} # House/Sign index -> Bindus
        self.bhinna_ashtakavarga: Dict[str, Dict[int, int]] = {} # Planet -> House/Sign -> Bindus
        
        # Strength structures
        self.bhava_bala: Dict[int, float] = {} # House index (1-12) -> Total Virupas
        
        # Jaimini structures
        self.arudhas: Dict[str, str] = {} # "AL", "UL", "A2", etc. -> Sign
        
        self.ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
                             
        self.SIGN_LORDS = {
            "Aries": "Mars", "Scorpio": "Mars",
            "Taurus": "Venus", "Libra": "Venus",
            "Gemini": "Mercury", "Virgo": "Mercury",
            "Cancer": "Moon",
            "Leo": "Sun",
            "Sagittarius": "Jupiter", "Pisces": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn"
        }

    @classmethod
    def from_dict(cls, basic_chart_dict: dict):
        asc = basic_chart_dict.get("Ascendant", {})
        c = cls(asc.get("sign", "Aries"), asc.get("degree", 0.0))
        c.ascendant_vargas = asc.get("vargas", {})
        c.arudhas = basic_chart_dict.get("arudhas", {})
        
        # Sarvashtakavarga might have string keys because JSON converts int keys to string
        sav = basic_chart_dict.get("sarvashtakavarga", {})
        c.sarvashtakavarga = {int(k): v for k, v in sav.items()} if sav else {}
        
        bb = basic_chart_dict.get("bhava_bala", {})
        c.bhava_bala = {int(k): v for k, v in bb.items()} if bb else {i: 0.0 for i in range(1, 13)}
        
        for p_name, p_data in basic_chart_dict.get("planets", basic_chart_dict).items():
            if p_name in ["Ascendant", "sarvashtakavarga", "bhava_bala"]:
                continue
            p = Planet(p_name, p_data.get("sign"), p_data.get("degree", 0.0), p_data.get("retrograde", False))
            p.house = p_data.get("house", 0)
            p.chalit_house = p_data.get("chalit_house", p.house)
            p.dignity = p_data.get("dignity", "Neutral")
            p.owns_houses = p_data.get("owns_houses", [])
            p.dispositor = p_data.get("dispositor")
            p.aspects_houses = p_data.get("aspects_houses", [])
            p.aspected_by = p_data.get("aspected_by", [])
            p.conjunct_with = p_data.get("conjunct_with", [])
            
            p.nakshatra = p_data.get("nakshatra", "")
            p.nakshatra_pada = p_data.get("nakshatra_pada", 1)
            p.nakshatra_lord = p_data.get("nakshatra_lord", "")
            
            p.combustion = p_data.get("combustion", {"status": False, "sun_distance": None, "threshold": None})
            p.planetary_war = p_data.get("planetary_war", {"in_war": False, "with_planet": None, "is_winner": False})
            p.avasthas = p_data.get("avasthas", {"balaadi": "Unknown"})
            p.friendships = p_data.get("friendships", {"natural_friends": [], "natural_enemies": [], "natural_neutrals": []})
            p.compound_friendships = p_data.get("compound_friendships", {})
            p.functional_role = p_data.get("functional_role", "")
            p.shadbala = p_data.get("shadbala", {
                "sthana_bala": 0.0, "dig_bala": 0.0, "kala_bala": 0.0,
                "cheshta_bala": 0.0, "naisargika_bala": 0.0, "drik_bala": 0.0,
                "total": 0.0, "is_partial": False
            })
            p.natural_karakas = p_data.get("natural_karakas", [])
            p.chara_karaka = p_data.get("chara_karaka")
            p.dispositor_chain = p_data.get("dispositor_chain", [])
            p.is_parivartana = p_data.get("is_parivartana", False)
            p.vimsopaka_bala = p_data.get("vimsopaka_bala", 0.0)
            p.vargas = p_data.get("vargas", {})
            
            c.add_planet(p)
        return c

    def add_planet(self, planet: Planet):
        self.planets[planet.name] = planet
        
    def get_sign_index(self, sign: str) -> int:
        return self.ZODIAC_SIGNS.index(sign)
        
    def build_relational_graph(self):
        asc_idx = self.get_sign_index(self.ascendant_sign)
        
        # 1. House placements & Dispositors
        for p_name, p in self.planets.items():
            p_idx = self.get_sign_index(p.sign)
            p.house = ((p_idx - asc_idx) % 12) + 1
            
            if p.sign in self.SIGN_LORDS:
                p.dispositor = self.SIGN_LORDS[p.sign]
                
        # 2. House Lordships
        for sign, lord in self.SIGN_LORDS.items():
            sign_idx = self.get_sign_index(sign)
            house = ((sign_idx - asc_idx) % 12) + 1
            if lord in self.planets:
                self.planets[lord].owns_houses.append(house)
                
        for p in self.planets.values():
            p.owns_houses.sort()
                
        # 3. Conjunctions
        for p1_name, p1 in self.planets.items():
            for p2_name, p2 in self.planets.items():
                if p1_name != p2_name and p1.house == p2.house:
                    p1.conjunct_with.append(p2_name)
                    
        # 4. Aspects (Drishti)
        from config import Config
        
        for p_name, p in self.planets.items():
            aspect_offsets = [7] 
            
            if p_name == "Mars":
                aspect_offsets = [4, 7, 8]
            elif p_name == "Jupiter":
                aspect_offsets = [5, 7, 9]
            elif p_name in ["Rahu", "Ketu"]:
                if Config.NODES_CAST_ASPECTS:
                    aspect_offsets = [5, 7, 9]
                else:
                    aspect_offsets = []
            elif p_name == "Saturn":
                aspect_offsets = [3, 7, 10]
                
            for offset in aspect_offsets:
                target_house = ((p.house - 1 + offset - 1) % 12) + 1
                p.aspects_houses.append(target_house)
                
        # Register aspect receivers
        for p_name, p in self.planets.items():
            for target_p_name, target_p in self.planets.items():
                if p_name != target_p_name:
                    if target_p.house in p.aspects_houses:
                        target_p.aspected_by.append(p_name)
                        
        # 5. Assign Natural and Chara Karakas
        from config import Config
        
        NATURAL_KARAKAS = {
            "Sun": ["Father", "Soul", "Authority", "Health"],
            "Moon": ["Mother", "Mind", "Emotions"],
            "Mars": ["Siblings", "Courage", "Enemies", "Property"],
            "Mercury": ["Intellect", "Speech", "Business", "Education"],
            "Jupiter": ["Children", "Wealth", "Wisdom", "Guru"],
            "Venus": ["Marriage", "Spouse", "Relationships", "Luxuries"],
            "Saturn": ["Sorrows", "Delays", "Longevity", "Career"],
            "Rahu": ["Obsessions", "Foreign", "Illusions"],
            "Ketu": ["Moksha", "Spirituality"]
        }
        
        for p_name, p in self.planets.items():
            if p_name in NATURAL_KARAKAS:
                p.natural_karakas = NATURAL_KARAKAS[p_name]
                
        if Config.USE_CHARA_KARAKAS:
            valid_planets = [p for name, p in self.planets.items() if name not in ["Ascendant", "Ketu"]]
            if Config.CHARA_KARAKA_SCHEME == 7:
                valid_planets = [p for p in valid_planets if p.name != "Rahu"]
                
            sorted_planets = sorted(valid_planets, key=lambda p: p.degree % 30, reverse=True)
            
            CHARA_LABELS_7 = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
            CHARA_LABELS_8 = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
            labels = CHARA_LABELS_7 if Config.CHARA_KARAKA_SCHEME == 7 else CHARA_LABELS_8
            
            for i, p in enumerate(sorted_planets):
                if i < len(labels):
                    p.chara_karaka = labels[i]

        # 6. Traverse Dispositor Chains
        for p_name, p in self.planets.items():
            chain = []
            current_dispositor = p.dispositor
            
            while current_dispositor and current_dispositor not in chain:
                chain.append(current_dispositor)
                if current_dispositor in self.planets:
                    current_dispositor = self.planets[current_dispositor].dispositor
                else:
                    break
                    
            p.dispositor_chain = chain
            
            # Detect Parivartana (Mutual Exchange): if A is in B's sign and B is in A's sign.
            # This means the chain of A starts with B, and B's chain starts with A.
            # Or simpler: length 2 loop (A -> B -> A).
            if len(chain) >= 2 and chain[-1] == p_name and chain[-1] != chain[0]:
                # If the loop comes back to itself
                p.is_parivartana = True
            elif len(chain) > 0 and self.planets.get(chain[0]) and chain[0] != p_name:
                # Specifically mutual exchange (Parivartana Yoga)
                first_disp = chain[0]
                if self.planets[first_disp].dispositor == p_name:
                    p.is_parivartana = True

    def to_dict(self):
        return {
            "ascendant": {
                "sign": self.ascendant_sign,
                "degree": self.ascendant_degree,
                "vargas": self.ascendant_vargas
            },
            "arudhas": self.arudhas,
            "planets": {name: p.to_dict() for name, p in self.planets.items()},
            "sarvashtakavarga": self.sarvashtakavarga,
            "bhava_bala": self.bhava_bala
        }
