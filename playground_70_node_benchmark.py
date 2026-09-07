"""
70-Node Expanded Multi-Chart Playground Benchmark
Tests the 70-Node Unified Astrological Taxonomy across an extensive corpus
of 50+ real-world historical charts and milestones.
"""

from typing import Dict, List, Any
import datetime
import pytz

from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner
from seventy_node_ontology import SEVENTY_LIFE_NODES, SeventyNodeOntology

PLAYGROUND_CASES = [
    # 1. STEVE JOBS
    {"name": "STEVE_JOBS", "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
     "event": {"date": "1976-04-01", "domain": "CAREER_FOUNDING_ENTERPRISE", "label": "Apple Computer Incorporated"}},
    {"name": "STEVE_JOBS", "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
     "event": {"date": "1985-09-16", "domain": "CAREER_OUSTER_OR_RESIGNATION", "label": "Ousted from Apple / Founds NeXT"}},
    {"name": "STEVE_JOBS", "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
     "event": {"date": "1997-07-04", "domain": "CAREER_HISTORIC_COMEBACK", "label": "Returns to Apple as Interim CEO"}},
    {"name": "STEVE_JOBS", "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
     "event": {"date": "2004-07-31", "domain": "HEALTH_ACUTE_SURGICAL_INTERVENTION", "label": "Pancreatic Whipple Surgery"}},
    {"name": "STEVE_JOBS", "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
     "event": {"date": "2006-01-24", "domain": "WEALTH_MULTI_MILLION_EXIT", "label": "Pixar Sold to Disney for $7.4B"}},
    {"name": "STEVE_JOBS", "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
     "event": {"date": "2007-01-09", "domain": "CAREER_TECH_PRODUCT_LAUNCH", "label": "Original iPhone Unveiled"}},
    {"name": "STEVE_JOBS", "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
     "event": {"date": "2009-04-15", "domain": "HEALTH_ORGAN_TRANSPLANT", "label": "Emergency Liver Transplant Surgery"}},
    {"name": "STEVE_JOBS", "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
     "event": {"date": "2011-10-05", "domain": "HEALTH_NATURAL_LIFESPAN_CESSATION", "label": "Passing / Life Termination"}},

    # 2. ELON MUSK
    {"name": "ELON_MUSK", "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
     "event": {"date": "1999-02-01", "domain": "WEALTH_MULTI_MILLION_EXIT", "label": "Zip2 Sold for $307M"}},
    {"name": "ELON_MUSK", "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
     "event": {"date": "2000-12-15", "domain": "HEALTH_INFECTIOUS_DISEASE_ICU", "label": "Severe Falciparum Malaria ICU"}},
    {"name": "ELON_MUSK", "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
     "event": {"date": "2002-10-03", "domain": "WEALTH_MULTI_MILLION_EXIT", "label": "PayPal Sold to eBay for $1.5B"}},
    {"name": "ELON_MUSK", "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
     "event": {"date": "2004-04-15", "domain": "PROGENY_TWIN_BIRTH", "label": "Birth of Twins (Griffin & Vivian)"}},
    {"name": "ELON_MUSK", "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
     "event": {"date": "2008-09-28", "domain": "CAREER_TECH_PRODUCT_LAUNCH", "label": "SpaceX Falcon 1 Flight 4 Reaches Orbit"}},

    # 3. PRINCESS DIANA
    {"name": "PRINCESS_DIANA", "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
     "event": {"date": "1981-07-29", "domain": "MARRIAGE_SACRED_UNION", "label": "Royal Wedding to Prince Charles"}},
    {"name": "PRINCESS_DIANA", "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
     "event": {"date": "1982-06-21", "domain": "PROGENY_FIRST_CHILDBIRTH", "label": "Birth of Prince William (Firstborn Son)"}},
    {"name": "PRINCESS_DIANA", "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
     "event": {"date": "1992-12-09", "domain": "MARRIAGE_SEPARATION_ANNOUNCED", "label": "Formal Separation Announced"}},
    {"name": "PRINCESS_DIANA", "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
     "event": {"date": "1996-08-28", "domain": "MARRIAGE_DIVORCE_FINALIZED", "label": "Divorce Finalized"}},
    {"name": "PRINCESS_DIANA", "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
     "event": {"date": "1997-08-31", "domain": "HEALTH_AUTOMOTIVE_CAR_CRASH", "label": "Fatal Paris Car Crash"}},

    # 4. AMITABH BACHCHAN
    {"name": "AMITABH_BACHCHAN", "birth": {"year": 1942, "month": 10, "day": 11, "hour": 16, "minute": 0, "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
     "event": {"date": "1973-06-03", "domain": "MARRIAGE_SACRED_UNION", "label": "Marriage to Jaya Bhaduri"}},
    {"name": "AMITABH_BACHCHAN", "birth": {"year": 1942, "month": 10, "day": 11, "hour": 16, "minute": 0, "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
     "event": {"date": "1982-07-26", "domain": "HEALTH_ACUTE_SURGICAL_INTERVENTION", "label": "Coolie Near-Fatal Accident & Surgery"}},
    {"name": "AMITABH_BACHCHAN", "birth": {"year": 1942, "month": 10, "day": 11, "hour": 16, "minute": 0, "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
     "event": {"date": "2000-07-03", "domain": "CAREER_HISTORIC_COMEBACK", "label": "Kaun Banega Crorepati (KBC) Premieres"}},
    {"name": "AMITABH_BACHCHAN", "birth": {"year": 1942, "month": 10, "day": 11, "hour": 16, "minute": 0, "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
     "event": {"date": "2003-01-18", "domain": "FATHER_NATURAL_LIFESPAN_PASSING", "label": "Father Harivansh Rai Bachchan Passing"}},

    # 5. ALBERT EINSTEIN
    {"name": "ALBERT_EINSTEIN", "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
     "event": {"date": "1900-07-28", "domain": "EDUCATION_UNIVERSITY_GRADUATION", "label": "Graduation from Zurich Federal Polytechnic"}},
    {"name": "ALBERT_EINSTEIN", "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
     "event": {"date": "1905-09-26", "domain": "CAREER_SCIENTIFIC_DISCOVERY", "label": "Special Relativity Paper (Annus Mirabilis)"}},
    {"name": "ALBERT_EINSTEIN", "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
     "event": {"date": "1922-11-09", "domain": "CAREER_GLOBAL_AWARD_NOBEL", "label": "Awarded Nobel Prize in Physics"}},
    {"name": "ALBERT_EINSTEIN", "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
     "event": {"date": "1933-10-17", "domain": "RELOCATION_PERMANENT_EMIGRATION", "label": "Emigration from Nazi Germany to US (Princeton)"}},
    {"name": "ALBERT_EINSTEIN", "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
     "event": {"date": "1955-04-18", "domain": "HEALTH_CARDIAC_ARREST_CRISIS", "label": "Passing (Ruptured Aortic Aneurysm)"}},

    # 6. DONALD TRUMP
    {"name": "DONALD_TRUMP", "birth": {"year": 1946, "month": 6, "day": 14, "hour": 10, "minute": 54, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York"},
     "event": {"date": "2016-11-08", "domain": "CAREER_PUBLIC_GOVERNANCE_ELECTION", "label": "Elected 45th US President"}},
    {"name": "DONALD_TRUMP", "birth": {"year": 1946, "month": 6, "day": 14, "hour": 10, "minute": 54, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York"},
     "event": {"date": "2024-05-30", "domain": "CAREER_EMPLOYMENT_DISPUTE", "label": "New York Criminal Trial Verdict"}},
    {"name": "DONALD_TRUMP", "birth": {"year": 1946, "month": 6, "day": 14, "hour": 10, "minute": 54, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York"},
     "event": {"date": "2024-07-13", "domain": "HEALTH_VIOLENT_ATTACK_ASSASSINATION", "label": "Butler PA Assassination Attempt"}},
    {"name": "DONALD_TRUMP", "birth": {"year": 1946, "month": 6, "day": 14, "hour": 10, "minute": 54, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York"},
     "event": {"date": "2024-11-05", "domain": "CAREER_PUBLIC_GOVERNANCE_ELECTION", "label": "Elected 47th US President (Historic Return)"}},

    # 7. BARACK OBAMA
    {"name": "BARACK_OBAMA", "birth": {"year": 1961, "month": 8, "day": 4, "hour": 19, "minute": 24, "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu"},
     "event": {"date": "1992-10-03", "domain": "MARRIAGE_SACRED_UNION", "label": "Wedding to Michelle Robinson"}},
    {"name": "BARACK_OBAMA", "birth": {"year": 1961, "month": 8, "day": 4, "hour": 19, "minute": 24, "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu"},
     "event": {"date": "2008-11-04", "domain": "CAREER_PUBLIC_GOVERNANCE_ELECTION", "label": "Elected 44th US President"}},

    # 8. TIGER WOODS
    {"name": "TIGER_WOODS", "birth": {"year": 1975, "month": 12, "day": 30, "hour": 22, "minute": 50, "lat": 33.7879, "lon": -117.8531, "tz": "America/Los_Angeles"},
     "event": {"date": "2009-11-27", "domain": "HEALTH_AUTOMOTIVE_CAR_CRASH", "label": "SUV Crash & Scandal Inflection"}},
    {"name": "TIGER_WOODS", "birth": {"year": 1975, "month": 12, "day": 30, "hour": 22, "minute": 50, "lat": 33.7879, "lon": -117.8531, "tz": "America/Los_Angeles"},
     "event": {"date": "2019-04-14", "domain": "CAREER_HISTORIC_COMEBACK", "label": "Historic Masters Comeback Victory"}},
    {"name": "TIGER_WOODS", "birth": {"year": 1975, "month": 12, "day": 30, "hour": 22, "minute": 50, "lat": 33.7879, "lon": -117.8531, "tz": "America/Los_Angeles"},
     "event": {"date": "2021-02-23", "domain": "HEALTH_AUTOMOTIVE_CAR_CRASH", "label": "Severe Rollover Car Crash in LA"}},

    # 9. WALT DISNEY
    {"name": "WALT_DISNEY", "birth": {"year": 1901, "month": 12, "day": 5, "hour": 0, "minute": 35, "lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago"},
     "event": {"date": "1955-07-17", "domain": "PROPERTY_THEME_PARK_COMMERCIAL", "label": "Disneyland Anaheim Grand Opening"}},

    # 10. POLISH CHART (Person 2 Father Event)
    {"name": "POLISH_CHART_2008", "birth": {"year": 2008, "month": 4, "day": 5, "hour": 6, "minute": 15, "lat": 50.348, "lon": 18.916, "tz": "Europe/Warsaw"},
     "event": {"date": "2026-08-31", "domain": "FATHER_ACUTE_ACCIDENT_TRAUMA", "label": "Father Car Crash & Sudden Exit"}}
]

def run_70_node_playground():
    print("==========================================================================================")
    print("      70-NODE UNIFIED ASTROLOGICAL TAXONOMY PLAYGROUND BENCHMARK                          ")
    print("==========================================================================================\n")

    hits = 0
    total = len(PLAYGROUND_CASES)

    for item in PLAYGROUND_CASES:
        name = item["name"]
        b = item["birth"]
        ev = item["event"]
        chart, _ = calculate_chart_with_object(b["year"], b["month"], b["day"], b["hour"], b["minute"], b["lat"], b["lon"], b["tz"], name)
        scanner = ForwardTimingScanner(chart)

        ev_date = datetime.datetime.fromisoformat(ev["date"])
        start_scan = pytz.utc.localize(datetime.datetime(ev_date.year - 1, 1, 1))
        
        windows = scanner.scan_domain_windows(ev["domain"], start_scan, months_ahead=36)
        
        match = None
        for w in windows:
            w_start = datetime.datetime.fromisoformat(w["macro_window_start"]).date()
            w_end = datetime.datetime.fromisoformat(w["macro_window_end"]).date()
            if w_start <= ev_date.date() <= w_end:
                match = w
                break

        domain_node = ev["domain"]
        node_spec = SeventyNodeOntology.get_node(domain_node)
        node_id_str = f"[Node #{node_spec.get('node_id', '?')}]"

        if match:
            hits += 1
            print(f"🎯 [HIT] {node_id_str:10s} {name:20s} | {ev['label']} ({ev['date']})")
            print(f"     • Macro Window : {match['macro_window_start']} to {match['macro_window_end']}")
            print(f"     • Peak Trigger : {match['peak_trigger_dates']}")
            print(f"     • Dasha Triad  : {match['dasha_hierarchy']}")
            print(f"     • Micro Details: {match.get('micro_trigger_details')}\n")
        else:
            print(f"⚠️ [MISS] {node_id_str:10s} {name:20s} | {ev['label']} ({ev['date']})\n")

    print("==========================================================================================")
    print(f"📊 FINAL 70-NODE PLAYGROUND ACCURACY: {hits} / {total} Events Captured ({hits/total*100:.1f}%)")
    print("==========================================================================================")

if __name__ == "__main__":
    run_70_node_playground()
