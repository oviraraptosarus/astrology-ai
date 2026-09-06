import re
"""
Dynamic Contextual Memory & Desha-Kala-Patra Calibration Engine
Grounds astrological archetypes into age, culture, life stage, and user context.
"""
import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

DB_PATH = os.path.join(os.path.dirname(__file__), "user_context_memory.db")

@dataclass
class UserContextProfile:
    user_id: str
    birth_date: str
    current_age: float
    marital_status: str = "unknown" # "single", "married", "divorced", "widowed"
    marriage_year: Optional[int] = None
    has_children: Optional[bool] = None
    children_count: int = 0
    career_type: str = "unknown" # "student", "employed", "business_owner", "retired"
    business_domain: Optional[str] = None
    location_country: str = "India"
    known_life_events: List[Dict[str, Any]] = field(default_factory=list)
    user_corrections: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ContextMemoryEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    profile_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    correction_type TEXT,
                    raw_statement TEXT,
                    extracted_fact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get_or_create_profile(self, user_id: str, birth_date_str: str) -> UserContextProfile:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT profile_json FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                # Re-calculate age dynamically
                try:
                    b_date = datetime.strptime(data["birth_date"], "%Y-%m-%d")
                    data["current_age"] = round((datetime.now() - b_date).days / 365.25, 1)
                except Exception:
                    pass
                return UserContextProfile(**data)
            
            # Create fresh profile
            try:
                b_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
                age = round((datetime.now() - b_date).days / 365.25, 1)
            except Exception:
                age = 30.0

            profile = UserContextProfile(
                user_id=user_id,
                birth_date=birth_date_str,
                current_age=age
            )
            self.save_profile(profile)
            return profile

    def save_profile(self, profile: UserContextProfile):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_profiles (user_id, profile_json, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    profile_json = excluded.profile_json,
                    updated_at = CURRENT_TIMESTAMP
            """, (profile.user_id, json.dumps(profile.to_dict())))
            conn.commit()

    def record_user_correction(self, user_id: str, raw_statement: str, profile: UserContextProfile) -> Dict[str, Any]:
        """
        Extracts life facts from user statements like:
        - "I am 18 years old"
        - "I am already married since 2001"
        - "I run an independent business"
        - "I don't have children"
        """
        stmt_lower = raw_statement.lower()
        extracted = {}

        if "18" in stmt_lower or "student" in stmt_lower or "college" in stmt_lower:
            if "student" in stmt_lower or "college" in stmt_lower:
                profile.career_type = "student"
                extracted["career_type"] = "student"

        # Flexible Regex Extraction
        # Marital Status
        if re.search(r'\b(divorced|separated|ex-wife|ex-husband)\b', stmt_lower):
            profile.marital_status = "divorced"
            extracted["marital_status"] = "divorced"
        elif re.search(r'\b(widow|widowed|late husband|late wife)\b', stmt_lower):
            profile.marital_status = "widowed"
            extracted["marital_status"] = "widowed"
        elif re.search(r'\b(already married|married in|married on|married since|got married|my wife|my husband)\b', stmt_lower):
            if not re.search(r'\b(not married|single|unmarried|bachelor)\b', stmt_lower):
                profile.marital_status = "married"
                extracted["marital_status"] = "married"
        elif re.search(r'\b(not married|single|unmarried|bachelor)\b', stmt_lower):
            profile.marital_status = "single"
            extracted["marital_status"] = "single"

        # Career Type
        if re.search(r'\b(retired|pensioner)\b', stmt_lower):
            profile.career_type = "retired"
            extracted["career_type"] = "retired"
        elif re.search(r'\b(business|startup|company|firm|enterprise|founder|owner|actor|artist|director|freelancer)\b', stmt_lower):
            profile.career_type = "business_owner" if not re.search(r'\b(student|college)\b', stmt_lower) else "student"
            extracted["career_type"] = profile.career_type
        elif re.search(r'\b(work at|working at|employee|job|hired|office)\b', stmt_lower):
            profile.career_type = "employed"
            extracted["career_type"] = "employed"

        if re.search(r'\b(kid|kids|child|children|son|daughter)\b', stmt_lower):
            if re.search(r"\b(no kids|don\'t have|no child|no children|without kids)\b", stmt_lower):
                profile.has_children = False
                extracted["has_children"] = False
            else:
                profile.has_children = True
                extracted["has_children"] = True

        profile.user_corrections.append({
            "timestamp": str(datetime.now()),
            "raw": raw_statement,
            "extracted": extracted
        })
        self.save_profile(profile)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_corrections (user_id, correction_type, raw_statement, extracted_fact)
                VALUES (?, ?, ?, ?)
            """, (user_id, "user_statement", raw_statement, json.dumps(extracted)))
            conn.commit()

        return extracted

    @staticmethod
    def calibrate_domain_prediction(domain: str, raw_activation: Dict[str, Any], profile: UserContextProfile) -> Dict[str, Any]:
        """
        Calibrates the raw astrological archetype using the Desha-Kala-Patra profile.
        """
        calibrated = {
            "original_domain": domain,
            "age": profile.current_age,
            "marital_status": profile.marital_status,
            "career_type": profile.career_type,
            "calibrated_archetype": domain,
            "guidance_note": ""
        }

        # 1. 7th House / Marriage Archetype Calibration
        if domain.upper() in ["MARRIAGE", "RELATIONSHIP"]:
            if profile.current_age < 21:
                calibrated["calibrated_archetype"] = "ROMANCE_AND_SOCIAL_CONNECTIONS"
                calibrated["guidance_note"] = (
                    f"User is {profile.current_age} years old (Student/Youth stage). "
                    "7th house activation manifests as dating, social popularity, or group projects, NOT formal marriage."
                )
            elif profile.marital_status == "married":
                calibrated["calibrated_archetype"] = "MARITAL_HARMONY_OR_B2B_PARTNERSHIP"
                calibrated["guidance_note"] = (
                    "User is already married. 7th house activation manifests as spouse's personal elevation, "
                    "joint financial decisions, or business partnerships, NOT a new marriage."
                )
            else:
                calibrated["calibrated_archetype"] = "MARRIAGE_AND_COMMITMENT"
                calibrated["guidance_note"] = "User is in prime marriageable age and single. 7th house indicates marriage timing."

        # 2. 5th House / Children Archetype Calibration
        elif domain.upper() in ["CHILDREN", "PROGENY"]:
            if profile.current_age < 20:
                calibrated["calibrated_archetype"] = "HIGHER_INTELLECT_AND_CREATIVE_STUDIES"
                calibrated["guidance_note"] = (
                    f"User is {profile.current_age} years old. 5th house activation represents competitive exams, "
                    "intellectual development, and artistic skills, NOT childbirth."
                )
            elif profile.current_age > 50:
                calibrated["calibrated_archetype"] = "CHILDREN_MILESTONES_AND_LEGACY"
                calibrated["guidance_note"] = (
                    "User is mature age. 5th house activation represents achievements and career milestones of grown children."
                )
            else:
                calibrated["calibrated_archetype"] = "CHILDBIRTH_AND_FAMILY_EXPANSION"
                calibrated["guidance_note"] = "Prime age for childbirth or expanding family."

        # 3. 10th House / Career vs Business Calibration
        elif domain.upper() in ["CAREER", "BUSINESS"]:
            if profile.career_type == "business_owner":
                calibrated["calibrated_archetype"] = "BUSINESS_REVENUE_EXPANSION"
                calibrated["guidance_note"] = (
                    "User is an independent business owner. 10H activation relates to commercial deals, "
                    "brand authority, and scaling enterprise, NOT corporate salary promotions."
                )
            elif profile.career_type == "student":
                calibrated["calibrated_archetype"] = "FIRST_CAREER_BREAKTHROUGH_OR_INTERNSHIP"
                calibrated["guidance_note"] = "User is a student. 10H activation indicates campus placements or starting career."
            else:
                calibrated["calibrated_archetype"] = "PROFESSIONAL_PROMOTION_OR_ROLE_CHANGE"
                calibrated["guidance_note"] = "Standard corporate career elevation."

        return calibrated
