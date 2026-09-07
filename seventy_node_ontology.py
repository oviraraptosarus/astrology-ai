"""
70-Node Unified Astrological Taxonomy & Life Dimension Ontology
===============================================================
Maps all 70 classical & modern life nodes across:
1. Houses & Multi-House Constellations
2. Primary & Secondary Karakas (Planetary Significators)
3. Specialized Divisional Charts (D1 to D60)
4. Special Lagnas & Padas (AL, UL, GL, HL, SL, Indu Lagna)
5. Sensitive Vulnerability Points (22D, 64N, Mrityu Bhagas, Gandantas)
6. Event Action Labels & Prediction Mechanics
"""

from typing import Dict, Any, List

SEVENTY_LIFE_NODES = {
    # ---------------------------------------------------------
    # I. WEALTH, CAPITAL & FINANCIAL ASYMMETRY (Nodes 1–8)
    # ---------------------------------------------------------
    "WEALTH_LIQUID_WINDFALL": {
        "node_id": 1,
        "houses": [2, 11, 9, 5],
        "karakas": ["Jupiter", "Venus", "Mercury"],
        "vargas": ["D2", "D10", "D60"],
        "special_lagnas": ["Indu_Lagna", "Hora_Lagna"],
        "label": "Major Liquid Capital Gain / Financial Windfall / Cash Event"
    },
    "WEALTH_MULTI_MILLION_EXIT": {
        "node_id": 2,
        "houses": [2, 11, 5, 9, 8],
        "karakas": ["Jupiter", "Venus", "Sun", "Mars"],
        "vargas": ["D10", "D2", "D60"],
        "special_lagnas": ["Indu_Lagna", "Shree_Lagna", "Ghatika_Lagna"],
        "label": "Multi-Million / Billionaire Company Sale / IPO / Equity Liquidity"
    },
    "WEALTH_STEADY_SAVINGS": {
        "node_id": 3,
        "houses": [2, 4, 11],
        "karakas": ["Jupiter", "Mercury", "Saturn"],
        "vargas": ["D2", "D9"],
        "special_lagnas": ["Dhana_Pada_A2", "Hora_Lagna"],
        "label": "Steady Capital Reserves / Cash Flow Compounding"
    },
    "WEALTH_DEBT_OR_CRISIS": {
        "node_id": 4,
        "houses": [6, 8, 12, 2],
        "karakas": ["Mars", "Saturn", "Rahu"],
        "vargas": ["D30", "D8"],
        "special_lagnas": ["A6", "A8"],
        "label": "Financial Drain / Debt Crisis / Capital Impairment"
    },
    "WEALTH_PASSIVE_ROYALTIES_IP": {
        "node_id": 5,
        "houses": [5, 9, 11, 2],
        "karakas": ["Mercury", "Venus", "Jupiter"],
        "vargas": ["D24", "D10"],
        "special_lagnas": ["A5", "Indu_Lagna"],
        "label": "Software Licensing / Royalty Income / Intellectual Property Cashflow"
    },
    "WEALTH_UNEARNED_INHERITANCE": {
        "node_id": 6,
        "houses": [8, 4, 2, 11],
        "karakas": ["Saturn", "Jupiter", "Mars"],
        "vargas": ["D12", "D8"],
        "special_lagnas": ["A8", "Matri_Pada_A4"],
        "label": "Inheritance / Paternal Asset Transfer / Estate Acquisition"
    },
    "WEALTH_SPECULATIVE_GAINS": {
        "node_id": 7,
        "houses": [5, 11, 8],
        "karakas": ["Rahu", "Jupiter", "Mercury"],
        "vargas": ["D5", "D9"],
        "special_lagnas": ["A5", "Labha_Pada_A11"],
        "label": "Speculative Trading / High-Beta Windfall / Crypto / Venture Returns"
    },
    "WEALTH_FOREIGN_CURRENCY": {
        "node_id": 8,
        "houses": [12, 7, 9, 11, 2],
        "karakas": ["Jupiter", "Rahu", "Moon"],
        "vargas": ["D10", "D9"],
        "special_lagnas": ["Indu_Lagna", "A12"],
        "label": "International Inflow / USD & Foreign Currency Retainers"
    },

    # ---------------------------------------------------------
    # II. CAREER, BUSINESS, TECH & EXECUTIVE POWER (Nodes 9–18)
    # ---------------------------------------------------------
    "CAREER_BREAKTHROUGH": {
        "node_id": 9,
        "houses": [10, 11, 1],
        "karakas": ["Sun", "Saturn", "Mars", "Jupiter"],
        "vargas": ["D10", "D9", "D60"],
        "special_lagnas": ["Rajya_Pada_A10", "Ghatika_Lagna"],
        "label": "Major Career Breakthrough / Executive Title Upgrade / Status Leap"
    },
    "CAREER_FOUNDING_ENTERPRISE": {
        "node_id": 10,
        "houses": [7, 10, 1, 3],
        "karakas": ["Mercury", "Mars", "Sun"],
        "vargas": ["D10", "D9"],
        "special_lagnas": ["A10", "A7"],
        "label": "Company Incorporation / Founding Startup or Agency"
    },
    "CAREER_TECH_PRODUCT_LAUNCH": {
        "node_id": 11,
        "houses": [10, 5, 3, 11],
        "karakas": ["Mercury", "Mars", "Rahu"],
        "vargas": ["D10", "D24"],
        "special_lagnas": ["A10", "A5"],
        "label": "Major Technical Deployment / Product Launch (Software, Hardware, AI)"
    },
    "CAREER_OUSTER_OR_RESIGNATION": {
        "node_id": 12,
        "houses": [8, 12, 10, 6],
        "karakas": ["Saturn", "Ketu", "Mars", "Sun"],
        "vargas": ["D10", "D30"],
        "special_lagnas": ["A8", "A10"],
        "label": "Corporate Ouster / Board Conflict / Sudden Resignation"
    },
    "CAREER_HISTORIC_COMEBACK": {
        "node_id": 13,
        "houses": [10, 1, 11, 8],
        "karakas": ["Sun", "Saturn", "Jupiter"],
        "vargas": ["D10", "D60"],
        "special_lagnas": ["Ghatika_Lagna", "A10"],
        "label": "Historic Comeback / Renaissance & Re-Elevation to Supreme Leadership"
    },
    "CAREER_PUBLIC_GOVERNANCE_ELECTION": {
        "node_id": 14,
        "houses": [10, 1, 11, 5, 9],
        "karakas": ["Sun", "Jupiter", "Mars", "Saturn"],
        "vargas": ["D10", "D5", "D60"],
        "special_lagnas": ["Ghatika_Lagna", "Rajya_Pada_A10"],
        "label": "Sovereign Election Victory / State Power / National Leadership"
    },
    "CAREER_SCIENTIFIC_DISCOVERY": {
        "node_id": 15,
        "houses": [5, 9, 10, 8],
        "karakas": ["Mercury", "Jupiter", "Ketu"],
        "vargas": ["D24", "D10"],
        "special_lagnas": ["A5", "Ghatika_Lagna"],
        "label": "Groundbreaking Scientific Discovery / Theory Formulation / Patent"
    },
    "CAREER_GLOBAL_AWARD_NOBEL": {
        "node_id": 16,
        "houses": [10, 11, 1, 9, 5],
        "karakas": ["Sun", "Jupiter", "Venus"],
        "vargas": ["D10", "D20", "D60"],
        "special_lagnas": ["Ghatika_Lagna", "Shree_Lagna"],
        "label": "Nobel Prize / Oscar / Global Prestige & Lifetime Honor"
    },
    "CAREER_CORPORATE_MERGER": {
        "node_id": 17,
        "houses": [7, 10, 11, 3],
        "karakas": ["Mercury", "Venus", "Jupiter"],
        "vargas": ["D10", "D9"],
        "special_lagnas": ["A7", "A10"],
        "label": "Corporate Acquisition / Cross-Enterprise Strategic Merger"
    },
    "CAREER_EMPLOYMENT_DISPUTE": {
        "node_id": 18,
        "houses": [6, 10, 8],
        "karakas": ["Mars", "Saturn", "Rahu"],
        "vargas": ["D10", "D6"],
        "special_lagnas": ["A6", "A10"],
        "label": "Workplace Conflict / Labor Dispute / Regulatory Friction"
    },

    # ---------------------------------------------------------
    # III. RELATIONSHIPS, MARRIAGE & DIVORCE (Nodes 19–26)
    # ---------------------------------------------------------
    "MARRIAGE_SACRED_UNION": {
        "node_id": 19,
        "houses": [7, 11, 2, 5],
        "karakas": ["Venus", "Jupiter", "Moon"],
        "vargas": ["D9", "D1"],
        "special_lagnas": ["Upapada_Lagna_UL", "Dara_Pada_A7"],
        "label": "Formal Marriage / Sacred Union / Wedding Ceremony"
    },
    "MARRIAGE_DIVORCE_FINALIZED": {
        "node_id": 20,
        "houses": [6, 8, 12, 7],
        "karakas": ["Mars", "Ketu", "Saturn", "Sun"],
        "vargas": ["D9", "D30"],
        "special_lagnas": ["A6", "A8", "UL"],
        "label": "Legal Divorce Finalized / Permanent Marital Dissolution"
    },
    "MARRIAGE_SEPARATION_ANNOUNCED": {
        "node_id": 21,
        "houses": [12, 6, 7],
        "karakas": ["Ketu", "Sun", "Saturn"],
        "vargas": ["D9"],
        "special_lagnas": ["UL", "A12"],
        "label": "Marital Separation / Physical Living Apart"
    },
    "MARRIAGE_SECOND_UNION": {
        "node_id": 22,
        "houses": [9, 2, 11, 7],
        "karakas": ["Venus", "Jupiter", "Rahu"],
        "vargas": ["D9"],
        "special_lagnas": ["UL", "A9"],
        "label": "Second Marriage / Remarriage / Subsequent Life Partner"
    },
    "ROMANCE_FIRST_FALLING_IN_LOVE": {
        "node_id": 23,
        "houses": [5, 7, 11],
        "karakas": ["Venus", "Moon", "Mercury"],
        "vargas": ["D9", "D5"],
        "special_lagnas": ["A5", "A7"],
        "label": "Deep Romance / Relationship Inception / Courtship"
    },
    "RELATIONSHIP_LONG_DISTANCE_BOND": {
        "node_id": 24,
        "houses": [7, 12, 9, 3],
        "karakas": ["Rahu", "Ketu", "Moon", "Venus"],
        "vargas": ["D9", "D12"],
        "special_lagnas": ["UL", "A12"],
        "label": "Long-Distance Romantic Partnership / Foreign Connection"
    },
    "MARRIAGE_SPOUSE_ELEVATION": {
        "node_id": 25,
        "houses": [7, 10, 11],
        "karakas": ["Jupiter", "Sun", "Venus"],
        "vargas": ["D9", "D10"],
        "special_lagnas": ["UL", "A7"],
        "label": "Spouse Major Career Breakthrough / Public Elevation"
    },
    "RELATIONSHIP_SCANDAL_EXPOSURE": {
        "node_id": 26,
        "houses": [8, 6, 7, 12],
        "karakas": ["Rahu", "Mars", "Venus"],
        "vargas": ["D9", "D30"],
        "special_lagnas": ["A8", "A6"],
        "label": "Public Relationship Scandal / Infidelity Exposure"
    },

    # ---------------------------------------------------------
    # IV. PROGENY & CHILDREN (Nodes 27–32)
    # ---------------------------------------------------------
    "PROGENY_FIRST_CHILDBIRTH": {
        "node_id": 27,
        "houses": [5, 2, 11],
        "karakas": ["Jupiter", "Moon"],
        "vargas": ["D7", "D1"],
        "special_lagnas": ["Putra_Pada_A5"],
        "label": "Birth of First Child / Progeny Initiation"
    },
    "PROGENY_TWIN_BIRTH": {
        "node_id": 28,
        "houses": [5, 11, 3],
        "karakas": ["Mercury", "Jupiter", "Rahu"],
        "vargas": ["D7"],
        "special_lagnas": ["A5", "A3"],
        "label": "Birth of Multiple Progeny (Twins / Multiples)"
    },
    "PROGENY_DAUGHTER_BORN": {
        "node_id": 29,
        "houses": [5, 2, 11],
        "karakas": ["Venus", "Moon", "Mercury"],
        "vargas": ["D7"],
        "special_lagnas": ["A5"],
        "label": "Birth of Daughter (Female Progeny)"
    },
    "PROGENY_SON_BORN": {
        "node_id": 30,
        "houses": [5, 2, 11],
        "karakas": ["Sun", "Mars", "Jupiter"],
        "vargas": ["D7"],
        "special_lagnas": ["A5"],
        "label": "Birth of Son (Male Progeny)"
    },
    "PROGENY_ADOPTION": {
        "node_id": 31,
        "houses": [5, 12, 8, 9],
        "karakas": ["Saturn", "Ketu", "Rahu"],
        "vargas": ["D7", "D12"],
        "special_lagnas": ["A5", "A12"],
        "label": "Legal Adoption of Child"
    },
    "PROGENY_CHILD_SUCCESS_MILESTONE": {
        "node_id": 32,
        "houses": [5, 10, 11, 9],
        "karakas": ["Jupiter", "Sun"],
        "vargas": ["D7", "D10"],
        "special_lagnas": ["A5"],
        "label": "Child's Major Educational or Career Breakthrough"
    },

    # ---------------------------------------------------------
    # V. HEALTH, ACCIDENTS, SURGERY & CRISIS (Nodes 33–42)
    # ---------------------------------------------------------
    "HEALTH_ACUTE_SURGICAL_INTERVENTION": {
        "node_id": 33,
        "houses": [8, 6, 12, 1],
        "karakas": ["Mars", "Ketu", "Saturn"],
        "vargas": ["D30", "D8"],
        "special_lagnas": ["A8", "A6"],
        "label": "Major Surgical Operation / Hospitalization / Trauma Recovery"
    },
    "HEALTH_AUTOMOTIVE_CAR_CRASH": {
        "node_id": 34,
        "houses": [4, 8, 6, 1, 2, 7],
        "karakas": ["Mars", "Rahu", "Saturn", "Sun"],
        "vargas": ["D30", "D16"],
        "special_lagnas": ["A4", "A8"],
        "label": "Automotive Car Crash / Severe Road Trauma"
    },
    "HEALTH_AVIATION_PLANE_CRASH": {
        "node_id": 35,
        "houses": [8, 12, 1, 9],
        "karakas": ["Rahu", "Mars", "Ketu", "Mercury"],
        "vargas": ["D30", "D16"],
        "special_lagnas": ["A8", "A12"],
        "label": "Aviation Accident / Fatal Plane Crash"
    },
    "HEALTH_VIOLENT_ATTACK_ASSASSINATION": {
        "node_id": 36,
        "houses": [8, 1, 7, 2],
        "karakas": ["Mars", "Rahu", "Saturn", "Sun"],
        "vargas": ["D30", "D60"],
        "special_lagnas": ["A8", "A1"],
        "label": "Violent Physical Assault / Gunshot Trauma / Assassination"
    },
    "HEALTH_INFECTIOUS_DISEASE_ICU": {
        "node_id": 37,
        "houses": [6, 8, 12],
        "karakas": ["Rahu", "Moon", "Mercury", "Saturn"],
        "vargas": ["D30"],
        "special_lagnas": ["A6", "A12"],
        "label": "Acute Infectious Disease / ICU Admission / Malaria / Viral Crisis"
    },
    "HEALTH_CHRONIC_PATHOLOGY_DISCOVERY": {
        "node_id": 38,
        "houses": [6, 8, 12],
        "karakas": ["Saturn", "Ketu", "Sun"],
        "vargas": ["D30"],
        "special_lagnas": ["A6", "A8"],
        "label": "Chronic Pathology Diagnosis (Endocrine, Pancreatic, Neurological)"
    },
    "HEALTH_ORGAN_TRANSPLANT": {
        "node_id": 39,
        "houses": [8, 12, 1, 6],
        "karakas": ["Mars", "Jupiter", "Ketu"],
        "vargas": ["D30", "D8"],
        "special_lagnas": ["A8", "A12"],
        "label": "Major Organ Transplant Surgery (Liver, Kidney, Heart)"
    },
    "HEALTH_CARDIAC_ARREST_CRISIS": {
        "node_id": 40,
        "houses": [4, 8, 1, 5],
        "karakas": ["Sun", "Mars", "Saturn"],
        "vargas": ["D30"],
        "special_lagnas": ["A4", "A8"],
        "label": "Cardiac Arrest / Aortic Pathology / Cardiovascular Surgery"
    },
    "HEALTH_NEUROLOGICAL_PARKINSONS": {
        "node_id": 41,
        "houses": [6, 8, 1, 3],
        "karakas": ["Saturn", "Mercury", "Rahu"],
        "vargas": ["D30"],
        "special_lagnas": ["A6", "A8"],
        "label": "Neurological Degeneration / Motor-Neuron / Parkinson's Diagnosis"
    },
    "HEALTH_NATURAL_LIFESPAN_CESSATION": {
        "node_id": 42,
        "houses": [8, 12, 2, 7, 1],
        "karakas": ["Saturn", "Sun", "Moon", "Ketu"],
        "vargas": ["D30", "D60"],
        "special_lagnas": ["A8", "A12"],
        "label": "Final Lifespan Termination / Physical Passing (Ayurdaya Completion)"
    },

    # ---------------------------------------------------------
    # VI. REAL ESTATE, ASSETS & VEHICLES (Nodes 43–48)
    # ---------------------------------------------------------
    "PROPERTY_LAND_ACQUISITION": {
        "node_id": 43,
        "houses": [4, 11, 1],
        "karakas": ["Mars", "Venus"],
        "vargas": ["D4", "D1"],
        "special_lagnas": ["Matri_Pada_A4"],
        "label": "Land Purchase / Real Estate Investment / Estate Expansion"
    },
    "PROPERTY_HOME_CONSTRUCTION_MOVE": {
        "node_id": 44,
        "houses": [4, 1, 11],
        "karakas": ["Mars", "Saturn", "Moon"],
        "vargas": ["D4"],
        "special_lagnas": ["A4"],
        "label": "New House Move-in / Home Construction Completion"
    },
    "PROPERTY_THEME_PARK_COMMERCIAL": {
        "node_id": 45,
        "houses": [4, 10, 11, 5],
        "karakas": ["Venus", "Saturn", "Mars"],
        "vargas": ["D4", "D10"],
        "special_lagnas": ["A4", "A10"],
        "label": "Commercial Property Launch / Theme Park / Studio Opening"
    },
    "PROPERTY_LUXURY_VEHICLE_PURCHASE": {
        "node_id": 46,
        "houses": [4, 11, 2],
        "karakas": ["Venus", "Mars"],
        "vargas": ["D16"],
        "special_lagnas": ["A4", "Vahana_Pada"],
        "label": "Luxury Automobile Acquisition / Fleet Expansion"
    },
    "PROPERTY_FIRE_OR_DAMAGE": {
        "node_id": 47,
        "houses": [4, 8, 6],
        "karakas": ["Mars", "Ketu", "Rahu"],
        "vargas": ["D4", "D30"],
        "special_lagnas": ["A4", "A8"],
        "label": "Domestic Property Structural Damage / Fire / Water Damage"
    },
    "PROPERTY_SALE_OR_DIVESTMENT": {
        "node_id": 48,
        "houses": [4, 3, 12, 11],
        "karakas": ["Mercury", "Mars", "Venus"],
        "vargas": ["D4", "D2"],
        "special_lagnas": ["A4", "A2"],
        "label": "Real Estate Sale / Capital Gain Liquidation"
    },

    # ---------------------------------------------------------
    # VII. RELOCATION, FOREIGN SETTLEMENT & TRAVEL (Nodes 49–54)
    # ---------------------------------------------------------
    "RELOCATION_PERMANENT_EMIGRATION": {
        "node_id": 49,
        "houses": [9, 12, 4, 3],
        "karakas": ["Rahu", "Moon", "Saturn"],
        "vargas": ["D12", "D9"],
        "special_lagnas": ["A12", "A9"],
        "label": "Permanent Emigration / Citizenship Change / Foreign Settlement"
    },
    "RELOCATION_CROSS_BORDER_MOVE": {
        "node_id": 50,
        "houses": [12, 3, 9],
        "karakas": ["Rahu", "Moon"],
        "vargas": ["D12"],
        "special_lagnas": ["A12"],
        "label": "International Job Relocation / Cross-Country Move"
    },
    "TRAVEL_SPIRITUAL_PILGRIMAGE": {
        "node_id": 51,
        "houses": [9, 12, 5],
        "karakas": ["Ketu", "Jupiter", "Sun"],
        "vargas": ["D20", "D9"],
        "special_lagnas": ["A9", "A12"],
        "label": "Long-Distance Sacred Pilgrimage / India Journey / Ashram Retreat"
    },
    "RELOCATION_RETURN_TO_HOMELAND": {
        "node_id": 52,
        "houses": [4, 1, 9],
        "karakas": ["Moon", "Jupiter"],
        "vargas": ["D4"],
        "special_lagnas": ["A4"],
        "label": "Repatriation / Returning Home from Foreign Lands"
    },
    "TRAVEL_HIGH_FREQUENCY_BUSINESS": {
        "node_id": 53,
        "houses": [3, 9, 10],
        "karakas": ["Mercury", "Moon"],
        "vargas": ["D10"],
        "special_lagnas": ["A3", "A10"],
        "label": "Intense Global Business Travel / Multi-Country Deal Tours"
    },
    "TRAVEL_VISA_OR_BORDER_FRICTION": {
        "node_id": 54,
        "houses": [12, 6, 8],
        "karakas": ["Rahu", "Saturn", "Ketu"],
        "vargas": ["D30"],
        "special_lagnas": ["A12", "A6"],
        "label": "Immigration Delay / Visa Audit / Border Friction"
    },

    # ---------------------------------------------------------
    # VIII. PARENTS & LINEAGE (BHAVAT BHAVAM) (Nodes 55–60)
    # ---------------------------------------------------------
    "FATHER_ACUTE_ACCIDENT_TRAUMA": {
        "node_id": 55,
        "houses": [4, 9, 8],
        "karakas": ["Sun", "Mars", "Saturn", "Mercury"],
        "vargas": ["D12", "D30"],
        "special_lagnas": ["A9", "A4"],
        "label": "Father Acute Automotive / Physical Trauma / Sudden Crisis"
    },
    "FATHER_NATURAL_LIFESPAN_PASSING": {
        "node_id": 56,
        "houses": [4, 9, 3, 10],
        "karakas": ["Sun", "Saturn", "Jupiter"],
        "vargas": ["D12", "D60"],
        "special_lagnas": ["A9", "A4"],
        "label": "Father Full Lifespan Completion / Paternal Passing"
    },
    "MOTHER_HEALTH_CRISIS": {
        "node_id": 57,
        "houses": [4, 11, 8, 10],
        "karakas": ["Moon", "Mars", "Saturn"],
        "vargas": ["D12", "D30"],
        "special_lagnas": ["A4", "A8"],
        "label": "Mother Acute Medical Crisis / Health Vulnerability"
    },
    "MOTHER_NATURAL_PASSING": {
        "node_id": 58,
        "houses": [11, 4, 8],
        "karakas": ["Moon", "Saturn", "Venus"],
        "vargas": ["D12"],
        "special_lagnas": ["A4", "A11"],
        "label": "Mother Full Lifespan Completion / Maternal Passing"
    },
    "FATHER_MAJOR_HONOR_OR_CAREER": {
        "node_id": 59,
        "houses": [9, 6, 1, 10],
        "karakas": ["Sun", "Jupiter"],
        "vargas": ["D12", "D10"],
        "special_lagnas": ["A9"],
        "label": "Father Career Triumph / Public Acclaim / Literary Achievement"
    },
    "PARENTAL_ADOPTION_SEVERANCE": {
        "node_id": 60,
        "houses": [4, 9, 12, 8],
        "karakas": ["Ketu", "Mars", "Moon"],
        "vargas": ["D12"],
        "special_lagnas": ["A12", "A4"],
        "label": "Severance from Biological Parents / Legal Adoption at Birth"
    },

    # ---------------------------------------------------------
    # IX. ACADEMICS, INTELLECT & COMPETITIVE EXAMS (Nodes 61–65)
    # ---------------------------------------------------------
    "EDUCATION_UNIVERSITY_GRADUATION": {
        "node_id": 61,
        "houses": [4, 5, 9],
        "karakas": ["Mercury", "Jupiter"],
        "vargas": ["D24", "D1"],
        "special_lagnas": ["A5", "A4"],
        "label": "Prestigious University Degree / Graduation Milestone"
    },
    "EDUCATION_LAW_REVIEW_OR_TOP_HONOR": {
        "node_id": 62,
        "houses": [5, 10, 1, 9],
        "karakas": ["Mercury", "Sun", "Jupiter"],
        "vargas": ["D24", "D10"],
        "special_lagnas": ["Ghatika_Lagna", "A5"],
        "label": "Election to Law Review / Academic Valedictorian / Highest Honor"
    },
    "EDUCATION_COLLEGE_DROPOUT_AUTONOMY": {
        "node_id": 63,
        "houses": [4, 9, 12, 8],
        "karakas": ["Ketu", "Mars", "Rahu"],
        "vargas": ["D24"],
        "special_lagnas": ["A12", "A4"],
        "label": "Dropping out of Formal Academia to Pursue Independent Innovation"
    },
    "EDUCATION_COMPETITIVE_EXAM_TOP_RANK": {
        "node_id": 64,
        "houses": [6, 5, 10, 11],
        "karakas": ["Mars", "Mercury", "Sun"],
        "vargas": ["D24", "D10"],
        "special_lagnas": ["A5", "A6"],
        "label": "Top Rank in National Competitive Entrance / Olympiad Win"
    },
    "INTELLECT_POLYGLOT_LANGUAGE_MASTERY": {
        "node_id": 65,
        "houses": [2, 5, 9, 3],
        "karakas": ["Mercury", "Jupiter", "Venus"],
        "vargas": ["D24"],
        "special_lagnas": ["A2", "A5"],
        "label": "Polyglot Language Fluency / Multi-Disciplinary Synthesis"
    },

    # ---------------------------------------------------------
    # X. SPIRITUALITY, OCCULT, DHARMA & MOKSHA (Nodes 66–70)
    # ---------------------------------------------------------
    "SPIRITUAL_MANTRA_SIDDHI_INITIATION": {
        "node_id": 66,
        "houses": [5, 9, 12],
        "karakas": ["Jupiter", "Ketu", "Sun"],
        "vargas": ["D20", "D9"],
        "special_lagnas": ["A5", "A9"],
        "label": "Sacred Mantra Deeksha / Guru Initiation / Sadhana Realization"
    },
    "SPIRITUAL_KUNDALINI_AWAKENING": {
        "node_id": 67,
        "houses": [8, 12, 1, 9],
        "karakas": ["Ketu", "Mars", "Moon"],
        "vargas": ["D20", "D60"],
        "special_lagnas": ["A8", "A12"],
        "label": "Spontaneous Kundalini Awakening / Mystical Transformation"
    },
    "SPIRITUAL_ZEN_ORDINATION_MOKSHA": {
        "node_id": 68,
        "houses": [12, 9, 7],
        "karakas": ["Ketu", "Saturn", "Jupiter"],
        "vargas": ["D20", "D9"],
        "special_lagnas": ["A12", "A9"],
        "label": "Zen Monastic Ordination / Renunciation / Lifelong Dharma Practice"
    },
    "OCCULT_DEEP_JYOTISHA_MASTERY": {
        "node_id": 69,
        "houses": [8, 5, 9, 2],
        "karakas": ["Mercury", "Ketu", "Jupiter"],
        "vargas": ["D20", "D24", "D60"],
        "special_lagnas": ["A8", "A5"],
        "label": "Mastery of Jyotisha, Esoteric Hermeticism & Occult Algorithms"
    },
    "SPIRITUAL_PHILANTHROPIC_ENDOWMENT": {
        "node_id": 70,
        "houses": [12, 9, 4, 11],
        "karakas": ["Jupiter", "Moon", "Sun"],
        "vargas": ["D20", "D9"],
        "special_lagnas": ["A12", "Shree_Lagna"],
        "label": "Creation of Multi-Billion Philanthropic Foundation / Global Endowment"
    }
}

class SeventyNodeOntology:
    @staticmethod
    def get_node(node_name_or_id) -> Dict[str, Any]:
        if isinstance(node_name_or_id, int):
            for k, v in SEVENTY_LIFE_NODES.items():
                if v["node_id"] == node_name_or_id:
                    return {"node_key": k, **v}
        return SEVENTY_LIFE_NODES.get(str(node_name_or_id).upper(), {})

    @staticmethod
    def list_all_nodes() -> List[Dict[str, Any]]:
        return [{"node_key": k, **v} for k, v in SEVENTY_LIFE_NODES.items()]
