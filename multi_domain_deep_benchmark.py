"""
Multi-Domain Deep Astrological Benchmark Suite (Comprehensive 10-Node Suite)
Tests the complete range of consultation nodes:
1. Progeny / Children
2. Money & Wealth Milestones
3. Technical Breakthroughs & Career Zenith
4. Marriage & Partnerships
5. Real Estate & Property
6. Foreign Relocation & International Travel
7. Academic & Higher Education Milestones
8. Litigation & Legal Battles
9. Fame, Elections & Sovereign Command
10. Acute Crisis & Accidents
Across verified historical ground-truth life events.
"""

from typing import Dict, List, Any
import datetime
import pytz

from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner

MULTI_DOMAIN_CASES = [
    # 1. PROGENY & CHILDREN
    {
        "name": "PRINCESS_DIANA",
        "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
        "event": {"date": "1982-06-21", "domain": "CHILDREN", "label": "Birth of Prince William (Firstborn Son)"}
    },
    {
        "name": "ELON_MUSK",
        "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
        "event": {"date": "2004-04-15", "domain": "CHILDREN", "label": "Birth of Twins (Griffin & Vivian)"}
    },
    {
        "name": "ANGELINA_JOLIE",
        "birth": {"year": 1975, "month": 6, "day": 4, "hour": 9, "minute": 9, "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "event": {"date": "2006-05-27", "domain": "CHILDREN", "label": "Birth of Daughter Shiloh"}
    },

    # 2. WEALTH & MULTI-MILLION / BILLIONAIRE WINDFALLS
    {
        "name": "ELON_MUSK",
        "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
        "event": {"date": "1999-02-01", "domain": "WEALTH", "label": "Zip2 Sold for $307M (First Liquidity)"}
    },
    {
        "name": "ELON_MUSK",
        "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
        "event": {"date": "2002-10-03", "domain": "WEALTH", "label": "PayPal Sold to eBay for $1.5B"}
    },
    {
        "name": "STEVE_JOBS",
        "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
        "event": {"date": "2006-01-24", "domain": "WEALTH", "label": "Pixar Sold to Disney for $7.4B"}
    },
    {
        "name": "OPRAH_WINFREY",
        "birth": {"year": 1954, "month": 1, "day": 29, "hour": 4, "minute": 30, "lat": 33.4735, "lon": -89.0776, "tz": "America/Chicago"},
        "event": {"date": "2003-02-27", "domain": "WEALTH", "label": "Becomes First Black Female Billionaire"}
    },

    # 3. TECHNICAL BREAKTHROUGHS & CAREER ZENITH
    {
        "name": "STEVE_JOBS",
        "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
        "event": {"date": "1976-04-01", "domain": "CAREER", "label": "Apple Computer Incorporated"}
    },
    {
        "name": "STEVE_JOBS",
        "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
        "event": {"date": "2007-01-09", "domain": "CAREER", "label": "Original iPhone Unveiled"}
    },
    {
        "name": "ELON_MUSK",
        "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg"},
        "event": {"date": "2008-09-28", "domain": "CAREER", "label": "SpaceX Falcon 1 Reaches Orbit (Saves Company)"}
    },
    {
        "name": "ALBERT_EINSTEIN",
        "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
        "event": {"date": "1905-09-26", "domain": "CAREER", "label": "Special Relativity Paper (Annus Mirabilis)"}
    },
    {
        "name": "ALBERT_EINSTEIN",
        "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
        "event": {"date": "1922-11-09", "domain": "CAREER", "label": "Awarded Nobel Prize in Physics"}
    },

    # 4. MARRIAGE & SACRED UNION
    {
        "name": "PRINCESS_DIANA",
        "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
        "event": {"date": "1981-07-29", "domain": "MARRIAGE", "label": "Royal Wedding to Prince Charles"}
    },
    {
        "name": "MARILYN_MONROE",
        "birth": {"year": 1926, "month": 6, "day": 1, "hour": 9, "minute": 30, "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "event": {"date": "1954-01-14", "domain": "MARRIAGE", "label": "Wedding to Joe DiMaggio"}
    },
    {
        "name": "BARACK_OBAMA",
        "birth": {"year": 1961, "month": 8, "day": 4, "hour": 19, "minute": 24, "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu"},
        "event": {"date": "1992-10-03", "domain": "MARRIAGE", "label": "Wedding to Michelle Robinson"}
    },

    # 5. REAL ESTATE & PERMANENT ASSETS
    {
        "name": "WALT_DISNEY",
        "birth": {"year": 1901, "month": 12, "day": 5, "hour": 0, "minute": 35, "lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago"},
        "event": {"date": "1955-07-17", "domain": "PROPERTY", "label": "Disneyland Anaheim Grand Opening"}
    },

    # 6. FOREIGN RELOCATION & INTERNATIONAL TRAVEL
    {
        "name": "ALBERT_EINSTEIN",
        "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
        "event": {"date": "1933-10-17", "domain": "RELOCATION", "label": "Emigration from Nazi Germany to US (Princeton)"}
    },
    {
        "name": "STEVE_JOBS",
        "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
        "event": {"date": "1974-04-15", "domain": "RELOCATION", "label": "7-Month India Spiritual Pilgrimage"}
    },

    # 7. ACADEMIC & HIGHER EDUCATION
    {
        "name": "ALBERT_EINSTEIN",
        "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin"},
        "event": {"date": "1900-07-28", "domain": "EDUCATION", "label": "Graduation from Zurich Federal Polytechnic"}
    },
    {
        "name": "BARACK_OBAMA",
        "birth": {"year": 1961, "month": 8, "day": 4, "hour": 19, "minute": 24, "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu"},
        "event": {"date": "1990-02-05", "domain": "EDUCATION", "label": "Elected First Black President of Harvard Law Review"}
    },

    # 8. LITIGATION & MAJOR LEGAL BATTLES
    {
        "name": "ANGELINA_JOLIE",
        "birth": {"year": 1975, "month": 6, "day": 4, "hour": 9, "minute": 9, "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
        "event": {"date": "2016-09-19", "domain": "LITIGATION", "label": "Files for High-Stakes Divorce & Custody Battle vs Brad Pitt"}
    },
    {
        "name": "DONALD_TRUMP",
        "birth": {"year": 1946, "month": 6, "day": 14, "hour": 10, "minute": 54, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York"},
        "event": {"date": "2024-05-30", "domain": "LITIGATION", "label": "New York Criminal Trial Jury Verdict"}
    },

    # 9. FAME, ELECTIONS & SOVEREIGN POWER
    {
        "name": "BARACK_OBAMA",
        "birth": {"year": 1961, "month": 8, "day": 4, "hour": 19, "minute": 24, "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu"},
        "event": {"date": "2008-11-04", "domain": "FAME", "label": "Elected 44th US President"}
    },
    {
        "name": "DONALD_TRUMP",
        "birth": {"year": 1946, "month": 6, "day": 14, "hour": 10, "minute": 54, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York"},
        "event": {"date": "2016-11-08", "domain": "FAME", "label": "Elected 45th US President"}
    },
    {
        "name": "DONALD_TRUMP",
        "birth": {"year": 1946, "month": 6, "day": 14, "hour": 10, "minute": 54, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York"},
        "event": {"date": "2024-11-05", "domain": "FAME", "label": "Elected 47th US President (Historic Comeback)"}
    }
]

def run_multi_domain_benchmarks():
    print("==========================================================================================")
    print("      MULTI-DOMAIN DEEP BENCHMARK (10 ESSENTIAL CONSULTATION NODES)                       ")
    print("==========================================================================================\n")

    hits = 0
    total = len(MULTI_DOMAIN_CASES)

    for item in MULTI_DOMAIN_CASES:
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

        domain_tag = f"[{ev['domain']}]"
        if match:
            hits += 1
            print(f"🎯 [HIT] {domain_tag:14s} {name:18s} | {ev['label']} ({ev['date']})")
            print(f"     • Macro Window: {match['macro_window_start']} to {match['macro_window_end']}")
            print(f"     • Peak Trigger: {match['peak_trigger_dates']}")
            print(f"     • Dasha Triad : {match['dasha_hierarchy']}")
            print(f"     • Details     : {match.get('micro_trigger_details')}\n")
        else:
            print(f"⚠️ [MISS] {domain_tag:14s} {name:18s} | {ev['label']} ({ev['date']})\n")

    print("==========================================================================================")
    print(f"📊 FINAL 10-NODE WINDOW-CONTAINMENT: {hits} / {total} events covered ({hits/total*100:.1f}%)")
    print("   NOTE: containment-only; random-date base rate is ~82% (see negative")
    print("   control in playground_70_node_benchmark.py). Containment is NOT accuracy.")
    print("==========================================================================================")

if __name__ == "__main__":
    run_multi_domain_benchmarks()
