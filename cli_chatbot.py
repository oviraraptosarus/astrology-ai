#!/usr/bin/env python3
"""
Astrology AI — Standalone Interactive CLI Chatbot
Direct interface for deterministic Kundli Math (2.1), Classical RAG (2.2),
Kundli Persistence (2.3), and Ideology Reconciliation (2.4).
"""

import os
import sys
import json
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Suppress noisy logs for a clean CLI experience
logging.basicConfig(level=logging.WARNING)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()

from astrology_engine import calculate_chart_with_object
from event_analysis import EventPredictionEngine
from realtime_engine import RealtimeEngine
from llm_provider import LLMProvider
from langchain_core.messages import HumanMessage, SystemMessage

def extract_text(content) -> str:
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                parts.append(p.get("text", ""))
            elif hasattr(p, "text"):
                parts.append(str(p.text))
        return "\n".join(parts).strip()
    return str(content).strip()

# ANSI Color codes for clean terminal presentation
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    BG_BLUE = "\033[44m"

# Standard Presets for testing
PRESETS = {
    "1": {
        "name": "India Independence",
        "year": 1947, "month": 8, "day": 15, "hour": 0, "minute": 0,
        "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata", "city": "New Delhi, India"
    },
    "2": {
        "name": "Steve Jobs",
        "year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15,
        "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles", "city": "San Francisco, CA"
    },
    "3": {
        "name": "Albert Einstein",
        "year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30,
        "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin", "city": "Ulm, Germany"
    }
}

class AstrologyCLI:
    def __init__(self):
        self.active_provider = os.getenv("DEFAULT_PROVIDER", "auto")
        self.active_mode = "grandmaster"  # grandmaster | react | raw
        self.active_profile = PRESETS["1"]
        self.chart_obj = None
        self.chart_dict = None
        self._rag = None
        
        self.calculate_active_chart()

    def get_rag(self):
        if self._rag is None:
            try:
                print(f"{C.DIM}Loading Classical RAG Engine (ChromaDB + BM25)...{C.RESET}")
                from advanced_rag import AdvancedRAG
                self._rag = AdvancedRAG()
                print(f"{C.GREEN}✓ RAG Engine Ready.{C.RESET}")
            except Exception as e:
                print(f"{C.YELLOW}⚠️ RAG initialization warning: {e}{C.RESET}")
                self._rag = None
        return self._rag

    def calculate_active_chart(self):
        p = self.active_profile
        try:
            self.chart_obj, self.chart_dict = calculate_chart_with_object(
                p["year"], p["month"], p["day"], p["hour"], p["minute"],
                p["lat"], p["lon"], p["tz"], p["name"]
            )
        except Exception as e:
            print(f"{C.RED}Error calculating chart for {p['name']}: {e}{C.RESET}")

    def banner(self):
        p = self.active_profile
        print(f"\n{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗")
        print(f"║                     🌌 ASTROLOGY AI — BACKEND CLI CHATBOT                    ║")
        print(f"╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
        print(f" {C.BOLD}Profile:{C.RESET}  {C.GREEN}{p['name']}{C.RESET} ({p['year']}-{p['month']:02d}-{p['day']:02d} {p['hour']:02d}:{p['minute']:02d} | {p['city']})")
        if self.chart_obj:
            asc = self.chart_obj.ascendant_sign
            moon = self.chart_dict.get('Basic_Chart', {}).get('Moon', {}).get('sign', 'Unknown')
            dasha = self.chart_dict.get('Current_Dasha', {})
            md = dasha.get('Mahadasha') or dasha.get('mahadasha', 'N/A')
            ad = dasha.get('Antardasha') or dasha.get('antardasha', 'N/A')
            print(f" {C.BOLD}Kundli:{C.RESET}   Lagna: {C.MAGENTA}{asc}{C.RESET} | Moon: {C.MAGENTA}{moon}{C.RESET} | Dasha: {C.YELLOW}{md}-{ad}{C.RESET} | Yogas: {len(self.chart_dict.get('Yogas_Found', []))}")
        print(f" {C.BOLD}Engine:{C.RESET}   Provider: {C.CYAN}{self.active_provider}{C.RESET} | Mode: {C.CYAN}{self.active_mode.upper()}{C.RESET}")
        print(f"{C.DIM}────────────────────────────────────────────────────────────────────────────────{C.RESET}")
        print(f" {C.DIM}Commands: /help, /chart, /preset <1|2|3>, /birth, /rag <q>, /reconcile <q>, /provider <name>, /mode <name>, /exit{C.RESET}\n")

    def show_varga_chart(self, varga_name: str):
        varga_name = varga_name.upper().strip()
        from varga_engine import VargaEngine
        
        valid_vargas = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
        if varga_name not in valid_vargas:
            print(f"{C.RED}Invalid Varga '{varga_name}'. Valid options: {', '.join(valid_vargas)}{C.RESET}")
            return
            
        p = self.active_profile
        print(f"\n{C.BOLD}{C.CYAN}═══ DIVISIONAL CHART: {varga_name} ({p['name']}) ═══{C.RESET}")
        print(f" {'Planet':<12} {'Sign in ' + varga_name:<16} {'Dignity in ' + varga_name}")
        print(f" {'─'*45}")
        
        # Ascendant
        asc_vargas = VargaEngine.calculate_all_vargas(self.chart_obj.ascendant_sign, self.chart_obj.ascendant_degree)
        print(f" {'Ascendant':<12} {asc_vargas.get(varga_name, 'N/A'):<16} {'Lagna'}")
        
        for name, planet in self.chart_obj.planets.items():
            if name == "Ascendant":
                continue
            p_vargas = VargaEngine.calculate_all_vargas(planet.sign, planet.degree)
            v_sign = p_vargas.get(varga_name, 'N/A')
            dignity = VargaEngine.assess_dignity(self.chart_obj, varga_name, [name]).get(name, "Neutral")
            print(f" {name:<12} {v_sign:<16} {dignity}")
        print()

    def show_chart_summary(self):
        if not self.chart_dict or not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return

        p = self.active_profile
        print(f"\n{C.BOLD}{C.CYAN}═══ KUNDLI OVERVIEW: {p['name']} ═══{C.RESET}")
        print(f"Birth: {p['year']}-{p['month']:02d}-{p['day']:02d} {p['hour']:02d}:{p['minute']:02d} ({p['tz']}) | Coordinates: {p['lat']:.4f}, {p['lon']:.4f}")
        
        # Ascendant & Planets
        print(f"\n{C.BOLD}--- Planetary Positions (D1 Rasi & Bhava Chalit) ---{C.RESET}")
        print(f" {'Planet':<10} {'Sign':<12} {'Degree':<8} {'House':<7} {'Chalit':<8} {'Dignity':<14} {'Nakshatra':<16} {'Lord'}")
        print(f" {'─'*80}")
        
        # Ascendant row
        asc = self.chart_dict.get("Basic_Chart", {}).get("Ascendant", {})
        print(f" {'Ascendant':<10} {asc.get('sign',''):<12} {asc.get('degree',0):<8.2f} {1:<7} {1:<8} {'Self':<14} {asc.get('nakshatra',''):<16} {asc.get('nakshatra_lord','')}")
        
        for name, planet in self.chart_obj.planets.items():
            if name == "Ascendant":
                continue
            ret = "(R)" if planet.retrograde else ""
            comb = " [Combust]" if planet.combustion.get("status") else ""
            p_name = f"{name}{ret}"
            dignity_str = f"{planet.dignity}{comb}"
            print(f" {p_name:<10} {planet.sign:<12} {planet.degree:<8.2f} {planet.house:<7} {planet.chalit_house:<8} {dignity_str:<14} {planet.nakshatra:<16} {planet.nakshatra_lord}")

        # Divisional Charts
        print(f"\n{C.BOLD}--- Divisional Charts (Vargas) ---{C.RESET}")
        d9 = self.chart_dict.get("Navamsha_D9", {})
        d10 = self.chart_dict.get("Dasamsha_D10", {})
        print(f" D9 Navamsha:  Lagna={d9.get('Ascendant')}, Sun={d9.get('Sun')}, Moon={d9.get('Moon')}, Mars={d9.get('Mars')}, Venus={d9.get('Venus')}, Jupiter={d9.get('Jupiter')}")
        print(f" D10 Dasamsha: Lagna={d10.get('Ascendant')}, Sun={d10.get('Sun')}, Moon={d10.get('Moon')}, Saturn={d10.get('Saturn')}, Mercury={d10.get('Mercury')}")

        # Yogas
        yogas = self.chart_dict.get("Yogas_Found", [])
        print(f"\n{C.BOLD}--- Formed Classical Yogas ({len(yogas)}) ---{C.RESET}")
        for y in yogas:
            print(f" • {C.GREEN}{y.get('name')}{C.RESET}: {y.get('reason')}")

        # Dasha Timeline
        dasha = self.chart_dict.get("Current_Dasha", {})
        md = dasha.get('Mahadasha') or dasha.get('mahadasha', 'N/A')
        ad = dasha.get('Antardasha') or dasha.get('antardasha', 'N/A')
        pd = dasha.get('Pratyantardasha') or dasha.get('pratyantardasha', 'N/A')
        print(f"\n{C.BOLD}--- Current Vimshottari Dasha ---{C.RESET}")
        print(f" Mahadasha: {C.YELLOW}{md}{C.RESET} | Antardasha: {C.YELLOW}{ad}{C.RESET} | Pratyantardasha: {C.YELLOW}{pd}{C.RESET}")
        print()

    def run_rag_search(self, query: str, tradition: str = None):
        rag = self.get_rag()
        if not rag:
            print(f"{C.RED}RAG Engine is not loaded.{C.RESET}")
            return
        
        use_hyde = "--hyde" in query
        clean_query = query.replace("--hyde", "").strip()
        print(f"\n{C.CYAN}Searching Classical Texts for:{C.RESET} '{clean_query}' (HyDE: {'ON' if use_hyde else 'OFF'})")
        try:
            raw_res = rag.retrieve_with_filters(clean_query, tradition=tradition, num_results=4, use_hyde=use_hyde, use_reranker=True)
            res_data = json.loads(raw_res)
            
            if use_hyde:
                print(f"{C.DIM}HyDE Expanded Query:{C.RESET} {res_data.get('hyde_query', 'N/A')}\n")
            print(f"{C.BOLD}--- Retrieved Classical Excerpts ({len(res_data.get('results', []))}) ---{C.RESET}")
            for idx, doc in enumerate(res_data.get('results', []), 1):
                meta = doc.get("metadata", {})
                print(f"\n{C.GREEN}[{idx}] {meta.get('title', 'Classical Text')} — Author: {meta.get('author', 'Unknown')} ({meta.get('tradition', 'Vedic')}){C.RESET}")
                print(f"{C.DIM}Chapter: {meta.get('chapter', 'N/A')} | Topic: {meta.get('topic', 'N/A')}{C.RESET}")
                print(f"{doc.get('text')}")
            print()
        except Exception as e:
            print(f"{C.RED}RAG search failed: {e}{C.RESET}")

    def learn_document(self, path_str: str):
        from ingest_book import BookIngestionEngine
        engine = BookIngestionEngine()
        target = path_str.strip()
        print(f"\n{C.CYAN}Learning and indexing knowledge from:{C.RESET} {target}")
        try:
            if os.path.isdir(target):
                results = engine.ingest_directory(target)
                print(f"{C.GREEN}✓ Ingested directory: {len(results)} items processed.{C.RESET}\n")
            else:
                res = engine.ingest_file(target)
                if res.get("status") == "SUCCESS":
                    print(f"{C.GREEN}✓ Successfully ingested '{res.get('title')}' ({res.get('total_chunks')} chunks, Tradition: {res.get('tradition')}){C.RESET}\n")
                elif res.get("status") == "SKIPPED":
                    print(f"{C.YELLOW}ℹ {res.get('message')}{C.RESET}\n")
                else:
                    print(f"{C.YELLOW}Result: {res.get('message', res.get('status'))}{C.RESET}\n")
        except Exception as e:
            print(f"{C.RED}Failed to learn document: {e}{C.RESET}\n")

    def show_sources(self):
        from ingest_book import BookIngestionEngine
        sources = BookIngestionEngine.get_ingested_sources()
        print(f"\n{C.BOLD}{C.CYAN}═══ INGESTED KNOWLEDGE BASE SOURCES ({len(sources)}) ═══{C.RESET}")
        if not sources:
            print(" No custom sources ingested yet. (Use /learn <path> to add classical books)")
        else:
            print(f" {'Title':<35} {'Tradition':<14} {'Chunks':<8} {'Ingested Date'}")
            print(f" {'─'*72}")
            for s in sources:
                print(f" {s.get('title','Unknown')[:34]:<35} {s.get('tradition','Vedic'):<14} {s.get('total_chunks',0):<8} {s.get('ingested_at','')}")
        print()

    def show_drik_panchang(self, city_arg: str = ""):
        p = self.active_profile
        city_target = city_arg.strip()
        
        if not city_target:
            city_target = input(f"{C.CYAN}Enter City / Location for Panchangam (press Enter for '{p['city']}'): {C.RESET}").strip()
            if not city_target:
                city_target = p["city"]
                
        lat, lon, tz, city_name = p["lat"], p["lon"], p["tz"], city_target
        
        try:
            from geopy.geocoders import Nominatim
            from timezonefinder import TimezoneFinder
            geo = Nominatim(user_agent="astrology-ai")
            loc = geo.geocode(city_target)
            if loc:
                lat, lon = loc.latitude, loc.longitude
                tf = TimezoneFinder()
                tz = tf.timezone_at(lng=lon, lat=lat) or "UTC"
                city_name = loc.address
        except Exception:
            pass
                
        from panchangam_engine import PanchangamEngine
        import pytz
        pe = PanchangamEngine()
        now = datetime.now(pytz.timezone(tz))
        pan = pe.calculate_full_panchang(now, lat, lon, tz)
        
        print(f"\n{C.BOLD}{C.CYAN}═══ DRIK PANCHANGAM & MUHURTA ({p['city']}) ═══{C.RESET}")
        print(f" {C.BOLD}Local Time:{C.RESET}       {pan['datetime_local']}")
        print(f" {C.BOLD}Sunrise / Set:{C.RESET}    {C.YELLOW}{pan['sun_metrics']['sunrise']}{C.RESET} / {C.YELLOW}{pan['sun_metrics']['sunset']}{C.RESET} (Day: {pan['sun_metrics']['dinamana']})")
        print(f" {C.BOLD}Vara:{C.RESET}             {pan['panchanga']['vara']['name']} (Lord: {pan['panchanga']['vara']['lord']})")
        print(f" {C.BOLD}Tithi:{C.RESET}            {C.MAGENTA}{pan['panchanga']['tithi']['name']}{C.RESET} (Ends: {pan['panchanga']['tithi']['ends_at']})")
        print(f" {C.BOLD}Nakshatra:{C.RESET}        {C.MAGENTA}{pan['panchanga']['nakshatra']['name']}{C.RESET} Pada {pan['panchanga']['nakshatra']['pada']} (Ends: {pan['panchanga']['nakshatra']['ends_at']})")
        print(f" {C.BOLD}Yoga / Karana:{C.RESET}    {pan['panchanga']['yoga']['name']} / {pan['panchanga']['karana']['name']}")
        print(f" {C.BOLD}Active Hora:{C.RESET}      {C.GREEN}{pan['panchanga']['active_hora']}{C.RESET}")
        
        print(f"\n{C.BOLD}--- Inauspicious & Auspicious Periods ---{C.RESET}")
        print(f"  Rahu Kalam:      {C.RED}{pan['inauspicious_periods']['rahu_kalam']}{C.RESET}")
        print(f"  Gulika Kalam:    {C.YELLOW}{pan['inauspicious_periods']['gulika_kalam']}{C.RESET}")
        print(f"  Yamaganda:       {C.YELLOW}{pan['inauspicious_periods']['yamaganda']}{C.RESET}")
        print(f"  Abhijit Muhurta: {C.GREEN}{pan['auspicious_periods']['abhijit_muhurta']}{C.RESET}")
        print(f"  Brahma Muhurta:  {C.GREEN}{pan['auspicious_periods']['brahma_muhurta']}{C.RESET}")
        
        shoonya = pan.get("tithi_shoonya_rashis", [])
        if shoonya:
            print(f"  Tithi Shoonya:   {C.RED}{', '.join(shoonya)}{C.RESET} (Burnt/Dagdha Signs for this Tithi)")

        print(f"\n{C.BOLD}--- Day Choghadiyas ---{C.RESET}")
        for ch in pan["choghadiya_day"]:
            color = C.GREEN if ch["nature"] == "Auspicious" else (C.YELLOW if ch["nature"] == "Neutral" else C.RED)
            print(f"  {ch['choghadiya']:<10} [{color}{ch['nature']:<12}{C.RESET}]: {ch['start']} - {ch['end']}")
        print()

    def show_realtime_snapshot(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from realtime_engine import RealtimeEngine
        snapshot = RealtimeEngine.get_realtime_correlation_snapshot(self.chart_obj, p["lat"], p["lon"], p["tz"])

        print(f"\n{C.BOLD}{C.CYAN}═══ REAL-TIME CELESTIAL & TRANSIT SNAPSHOT ═══{C.RESET}")
        print(f" {C.BOLD}Timestamp (Local):{C.RESET}  {snapshot['timestamp_local']}")
        print(f" {C.BOLD}Timestamp (UTC):{C.RESET}    {snapshot['timestamp_utc']}")
        print(f" {C.BOLD}Live Ascendant:{C.RESET}     {snapshot['live_ascendant']['sign']} {snapshot['live_ascendant']['degree']:.2f}° (Star: {snapshot['live_ascendant']['star_lord']})")
        print(f" {C.BOLD}Active Hora:{C.RESET}        {C.GREEN}{snapshot['planetary_hora']['active_hora']}{C.RESET} (Day Lord: {snapshot['planetary_hora']['day_lord']})")
        print(f" {C.BOLD}KP Ruling Planets:{C.RESET}  {C.MAGENTA}{' -> '.join(snapshot['kp_ruling_planets']['ruling_planets_ordered'])}{C.RESET}")

        print(f"\n{C.BOLD}--- Live Planetary Sky Positions ---{C.RESET}")
        print(f" {'Planet':<10} {'Sign':<12} {'Degree':<8} {'Speed (°/d)':<12} {'Nakshatra':<16} {'Star Lord'}")
        print(f" {'─'*72}")
        for p_name, p_data in snapshot["live_planets"].items():
            ret = "(R)" if p_data.get("retrograde") else ""
            stat = " [Stationary]" if p_data.get("stationary") else ""
            print(f" {p_name+ret+stat:<10} {p_data['sign']:<12} {p_data['degree']:<8.2f} {p_data['speed']:<12.4f} {p_data['nakshatra']:<16} {p_data['star_lord']}")

        print(f"\n{C.BOLD}--- Gochara Vedha Obstruction Status ---{C.RESET}")
        for v in snapshot["gochara_vedha"]:
            st = v["effective_status"]
            color = C.GREEN if st == "UNOBSTRUCTED_FAVORABLE" else C.RED
            obs = f" [Blocked by: {', '.join(v['obstructed_by'])}]" if v["is_obstructed"] else ""
            print(f"  {v['planet']:<8} in House {v['transiting_house']:<2} from Natal Moon -> Status: {color}{st}{C.RESET}{obs}")

        aspects = snapshot.get("catalytic_aspects", [])
        if aspects:
            print(f"\n{C.BOLD}--- Tight Transit-to-Natal Aspect Hits (<= 1.2° orb) ---{C.RESET}")
            for a in aspects:
                print(f"  {C.YELLOW}Transiting {a['transiting_planet']}{C.RESET} ({a['transit_sign']}) -> {C.MAGENTA}{a['aspect_type']}{C.RESET} -> {C.CYAN}Natal {a['natal_planet']}{C.RESET} ({a['natal_sign']}) [Orb: {a['orb_degrees']:.3f}°]")
        print()

    def show_kp_analysis(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from kp_engine import KPEngine
        kp = KPEngine.calculate_kp_chart(p["year"], p["month"], p["day"], p["hour"], p["minute"], p["lat"], p["lon"], p["tz"])
        
        print(f"\n{C.BOLD}{C.CYAN}═══ KP SYSTEM: 12 PLACIDUS CUSPS & 249 SUB-LORDS ({p['name']}) ═══{C.RESET}")
        print(f" {'Cusp':<6} {'Longitude':<11} {'Sign':<12} {'Sign Lord':<11} {'Star Lord':<11} {'Sub Lord':<11} {'Sub-Sub Lord'}")
        print(f" {'─'*78}")
        for c in kp["cusps"]:
            print(f" H{c['house']:<5} {c['longitude']:<11.4f} {c['sign']:<12} {c['sign_lord']:<11} {c['star_lord']:<11} {C.YELLOW}{c['sub_lord']:<11}{C.RESET} {c['sub_sub_lord']}")

        print(f"\n{C.BOLD}--- KP Planetary Placidus Positions & Sub-Lords ---{C.RESET}")
        print(f" {'Planet':<10} {'Longitude':<11} {'House':<7} {'Sign':<12} {'Star Lord':<11} {'Sub Lord':<11} {'Sub-Sub Lord'}")
        print(f" {'─'*78}")
        for name, p_data in kp["planets"].items():
            print(f" {name:<10} {p_data['longitude']:<11.4f} H{p_data['placidus_house']:<6} {p_data['sign']:<12} {p_data['star_lord']:<11} {C.YELLOW}{p_data['sub_lord']:<11}{C.RESET} {p_data['sub_sub_lord']}")

        print(f"\n{C.BOLD}--- Cuspal Sub-Lord (CSL) Life Promises ---{C.RESET}")
        for prom_key, prom in kp["csl_analysis"].items():
            print(f" • {C.GREEN}{prom_key.replace('_', ' ').title()}{C.RESET}: Sub-Lord {C.YELLOW}{prom['sub_lord']}{C.RESET} (in Star of {prom['star_lord']}) signifies houses {prom['signified_houses']} -> {C.MAGENTA}{prom['status']}{C.RESET}")
        print()

    def show_bnn_analysis(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from nadi_engine import NadiEngine
        clusters = NadiEngine.calculate_directional_clusters(self.chart_obj)
        bnn = NadiEngine.evaluate_jeeva_and_karma(self.chart_obj)

        print(f"\n{C.BOLD}{C.CYAN}═══ BHRIGU NANDI NADI (BNN): DIRECTIONAL TRINES (1-5-9) ═══{C.RESET}")
        for dir_name, dir_planets in clusters.items():
            p_names = [f"{dp['planet']} ({dp['sign']} {dp['degree']:.1f}°)" for dp in dir_planets]
            print(f" {C.BOLD}{dir_name:<14}:{C.RESET} {', '.join(p_names) if p_names else 'Empty'}")

        print(f"\n{C.BOLD}--- BNN Core Life Axes ---{C.RESET}")
        jeeva = bnn["jeeva_karaka"]
        karma = bnn["karma_karaka"]
        print(f" • {C.GREEN}Jeeva Karaka (Jupiter / Self):{C.RESET} In {jeeva.get('sign')}, Trines: {jeeva.get('trinal_conjunctions_1_5_9')}, Front Support: {jeeva.get('front_support_2nd')}")
        print(f" • {C.GREEN}Karma Karaka (Saturn / Career):{C.RESET} In {karma.get('sign')}, Trines: {karma.get('trinal_conjunctions_1_5_9')}, Front Support: {karma.get('front_support_2nd')}")

        print(f"\n{C.BOLD}--- BNN Classical Career Patterns ---{C.RESET}")
        for pat in bnn["bnn_career_patterns"]:
            print(f" [✓] {pat}")
        print()

    def show_pakshi_analysis(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from pancha_pakshi_engine import PanchaPakshiEngine
        moon = self.chart_obj.planets.get("Moon")
        sun = self.chart_obj.planets.get("Sun")
        if not moon or not sun:
            print(f"{C.RED}Missing Moon/Sun in chart.{C.RESET}")
            return

        from varga_engine import VargaEngine
        m_lon = (VargaEngine.get_sign_index(moon.sign) * 30.0) + moon.degree
        s_lon = (VargaEngine.get_sign_index(sun.sign) * 30.0) + sun.degree

        bird_info = PanchaPakshiEngine.get_birth_bird(m_lon, s_lon)
        local_tz = pytz.timezone(p["tz"])
        now_local = datetime.now(local_tz)
        activity = PanchaPakshiEngine.calculate_current_activity(bird_info["birth_bird"], now_local)

        print(f"\n{C.BOLD}{C.CYAN}═══ PANCHA PAKSHI SHASTRA (TAMIL SIDDHA BIO-TIMING) ═══{C.RESET}")
        print(f" Native's Birth Bird: {C.MAGENTA}{C.BOLD}{bird_info['birth_bird']}{C.RESET} (Paksha: {bird_info['paksha']})")
        print(f" Timestamp:           {activity['timestamp']} ({p['tz']})")
        print(f" Active Bio-State:    {C.YELLOW}{C.BOLD}{activity['active_activity'].upper()}{C.RESET} (Potency: {activity['potency_score']}% | {activity['tactical_status']})")
        print(f" Tactical Guidance:   {activity['action_guidance']}\n")

    def show_remedy_analysis(self, planet_arg: str = ""):
        from remedy_engine import RemedyEngine
        r_engine = RemedyEngine()
        target_planet = planet_arg.strip().capitalize()

        if target_planet and target_planet in RemedyEngine.REMEDY_DATABASE:
            planets_to_show = [target_planet]
        else:
            planets_to_show = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

        print(f"\n{C.BOLD}{C.CYAN}═══ PRESCRIPTIVE REMEDIAL ENGINEERING MATRIX ═══{C.RESET}")
        for p_name in planets_to_show:
            p_obj = self.chart_obj.planets.get(p_name) if self.chart_obj else None
            is_afflicted = True
            is_benefic = False
            if p_obj:
                is_afflicted = p_obj.dignity in ["Debilitated", "Enemy Sign"] or p_obj.combustion.get("status", False) or p_obj.house in [6, 8, 12]
                is_benefic = getattr(p_obj, "functional_role", "") in ["Benefic", "Yoga Karaka"]

            rem = r_engine.get_remedy_for_planet(p_name, is_benefic=is_benefic, is_afflicted=is_afflicted)
            print(f"\n{C.BOLD}{C.MAGENTA}✦ Planet: {p_name}{C.RESET}")
            print(f"  {C.BOLD}Vedic Beeja Mantra:{C.RESET}  {C.GREEN}{rem['vedic_mantra']}{C.RESET}")
            print(f"  {C.BOLD}Japa Count:{C.RESET}          {rem['japa_count']}")
            print(f"  {C.BOLD}Astronomical Daana:{C.RESET}  {', '.join(rem['daana_charity']['items'])} on {C.YELLOW}{rem['daana_charity']['prescribed_day']}{C.RESET} ({rem['daana_charity']['astronomical_timing']})")
            print(f"  {C.BOLD}Lal Kitab Upaya:{C.RESET}     {rem['lal_kitab_upayas'][0]}")
            print(f"  {C.BOLD}Gemstone Verdict:{C.RESET}    {rem['gemstone_verdict']['recommendation']} ({rem['gemstone_verdict']['reason']})")
        print()

    def show_tajaka_analysis(self, year_arg: str = ""):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        target_year = int(year_arg.strip()) if year_arg.strip().isdigit() else (datetime.now().year + 1)
        
        local_tz = pytz.timezone(p["tz"])
        dt_local = local_tz.localize(datetime(p["year"], p["month"], p["day"], p["hour"], p["minute"]))
        dt_utc = dt_local.astimezone(pytz.utc)

        from tajaka_engine import TajakaEngine
        varsha = TajakaEngine.calculate_varshaphala(self.chart_obj, dt_utc, target_year, p["lat"], p["lon"])

        print(f"\n{C.BOLD}{C.CYAN}═══ TAJAKA VARSHAPHALA (ANNUAL SOLAR RETURN): {target_year} ({p['name']}) ═══{C.RESET}")
        print(f" Solar Return Epoch (UTC): {varsha['solar_return_epoch_utc']}")
        print(f" Varsha Lagna:            {C.MAGENTA}{varsha['varsha_ascendant']['sign']} {varsha['varsha_ascendant']['degree']}°{C.RESET} (Lord: {varsha['varsha_ascendant']['sign_lord']})")
        m = varsha['muntha']
        print(f" Progressed Muntha:       {C.YELLOW}{m['sign']}{C.RESET} (House {m['house_in_varsha']} in Varsha, House {m['house_in_natal']} in Natal) -> {C.GREEN}{m['status']}{C.RESET}")

        print(f"\n{C.BOLD}--- Key Classical Sahams (Sensitive Arabic Parts) ---{C.RESET}")
        for s_name, s_data in varsha['key_sahams'].items():
            print(f" • {s_name:<38}: {s_data['sign']:<12} {s_data['degree']:<6.2f}° (House {s_data['house']})")

        print(f"\n{C.BOLD}--- Formed Tajaka Aspect Yogas ({len(varsha['tajaka_yogas'])}) ---{C.RESET}")
        for y in varsha['tajaka_yogas']:
            nature_col = C.GREEN if "BENEFIC" in y.get('nature','') or "Ithasala" in y['yoga'] else C.YELLOW
            print(f" [✓] {nature_col}{y['yoga']}{C.RESET}: {y['faster_planet']} -> {y['slower_planet']} ({y['aspect_type']}, orb: {y['orb_diff']}°)")
        print()

    def show_chakras_analysis(self, entity_arg: str = ""):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from realtime_engine import RealtimeEngine
        from institutional_chakra_engine import InstitutionalChakraEngine

        snapshot = RealtimeEngine.get_realtime_correlation_snapshot(self.chart_obj, p["lat"], p["lon"], p["tz"])
        live_planets = snapshot["live_planets"]

        kota = InstitutionalChakraEngine.calculate_kota_chakra(self.chart_obj, live_planets)
        print(f"\n{C.BOLD}{C.CYAN}═══ KOTA CHAKRA (INSTITUTIONAL & FORTRESS DEFENSE) ═══{C.RESET}")
        print(f" Kota Lord (King / Self):      {C.MAGENTA}{kota['kota_lord_king']}{C.RESET}")
        print(f" Kota Pala (Fortress Guard):   {C.MAGENTA}{kota['kota_pala_commander']}{C.RESET}")
        siege_col = C.GREEN if "INVULNERABLE" in kota['siege_status'] or "FORTIFIED" in kota['siege_status'] else C.RED
        print(f" Siege & Defense Status:       {siege_col}{kota['siege_status']}{C.RESET}")
        print(f" Tactical Defense Verdict:     {kota['tactical_verdict']}")

        print(f"\n{C.BOLD}--- Fortress Concentric Zones ---{C.RESET}")
        zones = kota["fortress_zones"]
        print(f" 1. Stambha (Inner Sanctum):   {[p['planet'] for p in zones['1_stambha_sanctum']] or 'Empty'}")
        print(f" 2. Madhya (Castle Hall):      {[p['planet'] for p in zones['2_madhya_inner_court']] or 'Empty'}")
        print(f" 3. Prakara (Fortress Walls):  {[p['planet'] for p in zones['3_prakara_fort_wall']] or 'Empty'}")
        print(f" 4. Bahya (Outer Perimeter):   {[p['planet'] for p in zones['4_bahya_outer_gates']] or 'Empty'}")

        entity_name = entity_arg.strip() if entity_arg.strip() else p["name"]
        sbc = InstitutionalChakraEngine.evaluate_sbc_veddha(entity_name, live_planets)
        print(f"\n{C.BOLD}--- Sarvatobhadra Chakra (9x9 SBC Veddha on '{entity_name}') ---{C.RESET}")
        print(f" Net SBC Transit Climate:      {C.GREEN if sbc['net_sbc_climate']=='SUPPORTIVE' else C.YELLOW}{sbc['net_sbc_climate']}{C.RESET}")
        print()

    def show_kakshya_analysis(self, planet_arg: str = ""):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from ashtakavarga_engine import AshtakavargaEngine
        from realtime_engine import RealtimeEngine

        snapshot = RealtimeEngine.get_realtime_correlation_snapshot(self.chart_obj, p["lat"], p["lon"], p["tz"])
        live_planets = snapshot["live_planets"]

        target_planet = planet_arg.strip().capitalize() if planet_arg.strip() else "Jupiter"
        if target_planet not in live_planets:
            target_planet = "Jupiter"

        t_data = live_planets[target_planet]
        t_sign = t_data["sign"]
        t_deg = t_data["degree"]

        k_res = AshtakavargaEngine.evaluate_kakshya_transit(self.chart_obj, target_planet, t_sign, t_deg)

        print(f"\n{C.BOLD}{C.CYAN}═══ ASHTAKAVARGA: 3°45' KAKSHYA MICRO-TRANSIT WINDOW ═══{C.RESET}")
        print(f" Transiting Planet:      {C.MAGENTA}{target_planet}{C.RESET} in {t_sign} ({t_deg:.2f}°)")
        print(f" Active Kakshya Lord:    {C.YELLOW}{k_res['kakshya_lord']}{C.RESET} (Zone {k_res['kakshya_index']}/8: {k_res['kakshya_degree_range']})")
        print(f" Natal Bindu Fired:      {C.GREEN if k_res['has_bindu'] else C.RED}{'YES (1 Bindu Contributed)' if k_res['has_bindu'] else 'NO (0 Rekha - Dormant)'}{C.RESET}")
        print(f" House SAV / BAV:        House {k_res['house']} -> BAV: {k_res['total_bav']} bindus, SAV: {k_res['total_sav']} bindus")
        print(f" Micro-Timing Verdict:   {C.GREEN if k_res['has_bindu'] else C.YELLOW}{k_res['status']}{C.RESET}")
        print()

    def show_gann_analysis(self, price_str: str = ""):
        price = float(price_str.strip()) if price_str.strip().replace('.', '', 1).isdigit() else 100.0
        from realtime_engine import RealtimeEngine
        from financial_astro_engine import FinancialAstroEngine
        p = self.active_profile

        snapshot = RealtimeEngine.get_realtime_correlation_snapshot(self.chart_obj, p["lat"], p["lon"], p["tz"])
        gann = FinancialAstroEngine.calculate_gann_squaring(price, snapshot["live_planets"])

        print(f"\n{C.BOLD}{C.CYAN}═══ FINANCIAL ASTROLOGY: W.D. GANN SQUARE OF 9 (PRICE: ${price:,.2f}) ═══{C.RESET}")
        print(f" Gann Wheel Degree:      {C.YELLOW}{gann['gann_wheel_degree']:.2f}°{C.RESET}")
        print(f" Market Harmonic State:  {C.GREEN if gann['active_squarings'] else C.CYAN}{gann['market_state']}{C.RESET}")

        if gann["active_squarings"]:
            print(f"\n{C.BOLD}--- Active Price-Time Planetary Squarings ---{C.RESET}")
            for sq in gann["active_squarings"]:
                print(f" • {sq['planet']} (at {sq['planet_longitude']}°) -> {C.MAGENTA}{sq['squaring_type']}{C.RESET} [Orb: {sq['orb']}°]")

        print(f"\n{C.BOLD}--- Gann Harmonic Support & Resistance Price Levels ---{C.RESET}")
        for l_name, l_val in gann["gann_harmonic_price_levels"].items():
            col = C.RED if "Resistance" in l_name else C.GREEN
            print(f"  {l_name:<34}: {col}${l_val:,.2f}{C.RESET}")
        print()

    def show_cosmo_analysis(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from western_cosmo_engine import WesternCosmoEngine
        dial = WesternCosmoEngine.calculate_90_deg_dial(self.chart_obj)

        print(f"\n{C.BOLD}{C.CYAN}═══ COSMOBIOLOGY: 90° GRAPHIC DIAL & MIDPOINT TREES ({p['name']}) ═══{C.RESET}")
        print(f" {'Planet':<10} {'Dial 90° Pos':<14} {'Full Zodiac Degree'}")
        print(f" {'─'*45}")
        for p_name, p_data in dial["dial_90_positions"].items():
            print(f" {p_name:<10} {C.YELLOW}{p_data['dial_formatted']:<14}{C.RESET} {p_data['sign']} {p_data['degree']:.2f}° ({p_data['full_longitude']:.2f}°)")

        print(f"\n{C.BOLD}--- Active Midpoint Trees (A/B = C within <= 1.0° orb) ---{C.RESET}")
        for mp in dial["active_midpoint_pictures"][:10]:
            print(f" [✓] {C.GREEN}{mp['configuration']:<18}{C.RESET} -> Dial: {mp['midpoint_dial_deg']:.2f}° (Orb: {mp['orb']}°)")
        print()

    def show_sensitive_analysis(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from sensitive_points import SensitivePointsEngine
        sp = SensitivePointsEngine(self.chart_obj).calculate_all()

        print(f"\n{C.BOLD}{C.CYAN}=== CRITICAL SENSITIVE POINTS & VULNERABILITY MATRIX ({p['name']}) ==={C.RESET}")
        d22 = sp['22nd_drekkana']
        d64l = sp['64th_navamsha']['from_lagna']
        print(f" 22nd Drekkana (Kharesh):  {d22['d3_sign']} (Lord: {C.YELLOW}{d22['kharesh_lord']}{C.RESET})")
        print(f" 64th Navamsha (Lagna):    {d64l['d9_sign']} (Lord: {C.YELLOW}{d64l['lord']}{C.RESET}, D1 Arc: {d64l['d1_arc_start_deg']})")
        if 'from_moon' in sp['64th_navamsha']:
            d64m = sp['64th_navamsha']['from_moon']
            print(f" 64th Navamsha (Moon):     {d64m['d9_sign']} (Lord: {C.YELLOW}{d64m['lord']}{C.RESET}, D1 Arc: {d64m['d1_arc_start_deg']})")

        bb = sp.get('bhrigu_bindu', {})
        print(f" Bhrigu Bindu (Destiny):   {bb.get('sign')} {bb.get('degree_in_sign')} (Lord: {C.YELLOW}{bb.get('sign_lord')}{C.RESET})")

        il = sp.get('indu_lagna', {})
        print(f" Indu Lagna (Wealth):      {il.get('indu_lagna_sign')} | Rays: {il.get('total_rays')} | Grade: {C.GREEN}{il.get('wealth_grade')}{C.RESET}")

        mbs = sp.get('mrityu_bhagas', [])
        if mbs:
            print(f"\n {C.RED}-- Mrityu Bhaga Afflictions ({len(mbs)}) --{C.RESET}")
            for mb in mbs:
                print(f" [!] {mb['entity']} at {mb['degree']} {mb['sign']} (MB exact: {mb['mrityu_bhaga_degree']})")
        else:
            print(f" {C.GREEN}No Mrityu Bhaga afflictions.{C.RESET}")

        gands = sp.get('gandanta_points', [])
        if gands:
            print(f"\n {C.YELLOW}-- Gandanta Karmic Knots ({len(gands)}) --{C.RESET}")
            for g in gands:
                print(f" [!] {g['entity']} in {g['knot']} ({g['type']})")

        ps = sp.get('pushkara_status', {})
        if ps.get('planets'):
            print(f"\n {C.CYAN}-- Pushkara Auspicious Points ({len(ps['planets'])}) --{C.RESET}")
            for p_info in ps['planets']:
                nav = f"PN:{p_info['navamsha_sign']}" if p_info['pushkara_navamsha'] else ""
                pba = "PB" if p_info['pushkara_bhaga'] else ""
                print(f" [*] {p_info['planet']} at {p_info['sign']} {p_info['degree']} ({nav} {pba})")
        print()

    def show_upagrahas_analysis(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from upagrahas import UpagrahaEngine
        up_data = UpagrahaEngine(self.chart_obj).calculate_aprakash_grahas()

        print(f"\n{C.BOLD}{C.CYAN}=== UPAGRAHAS & NON-LUMINOUS SHADOW GRAHAS ({p['name']}) ==={C.RESET}")
        print(f" {'Upagraha':<14} {'Sign':<14} {'Degree':<10} {'House'}")
        print(f" {'-'*45}")
        for k, pt in up_data.items():
            print(f" {pt['name']:<14} {pt['sign']:<14} {pt['degree_in_sign']:<10.2f} H{pt['house']}")
        print()

    def show_numerology_analysis(self, name_str: str = ""):
        p = self.active_profile
        from numerology_engine import NumerologyEngine
        report = NumerologyEngine.generate_full_profile(
            day=p["day"], month=p["month"], year=p["year"], name=name_str
        )
        
        print(f"\n{C.BOLD}{C.CYAN}=== ANK JYOTISH & CHALDEAN NUMEROLOGY ({name_str or p['name']}) ==={C.RESET}")
        m = report['moolank']
        print(f" {C.BOLD}Moolank (Day/Nature):{C.RESET}    {C.YELLOW}{m['single']}{C.RESET} (Root: {m['compound']}, Lord: {m['ruler']})")
        
        b = report['bhagyank']
        print(f" {C.BOLD}Bhagyank (Destiny/Path):{C.RESET} {C.YELLOW}{b['single']}{C.RESET} (Root: {b['compound']}, Lord: {b['ruler']})")
        
        print(f" {C.BOLD}Core Harmony:{C.RESET}            {report['core_harmony']}")
        
        if 'namank' in report:
            n = report['namank']
            print(f"\n {C.BOLD}Namank (Chaldean Name):{C.RESET}  {C.YELLOW}{n['single']}{C.RESET} (Root: {n['compound']}, Lord: {n['ruler']})")
            print(f" {C.BOLD}Name Harmony:{C.RESET}            {C.GREEN if 'ALIGNED' in report['name_harmony'] else C.RED}{report['name_harmony']}{C.RESET}")
            print(f" {C.BOLD}Katapayadi Varga Sum:{C.RESET}    {report['katapayadi_nama']}")
        print()

    def show_dosha_analysis(self):
        if not self.chart_obj: return
        p = self.active_profile
        from dosha_engine import DoshaEngine
        import pytz
        de = DoshaEngine(self.chart_obj)
        res = de.evaluate_all(target_date=datetime.now(pytz.utc))
        
        print(f"\n{C.BOLD}{C.CYAN}=== DOSHAS & KARMIC FRICTION MATRIX ({p['name']}) ==={C.RESET}")
        
        ss = res["sade_sati"]
        cc = C.RED if "ACTIVE" in ss["status"] else C.GREEN
        print(f"\n{C.BOLD}--- Saturn Transits (Sade Sati/Kantaka) ---{C.RESET}")
        print(f" {cc}[{ss['status']}]{C.RESET} Currently in {ss['transit_saturn_sign']} (House {ss['house_from_moon']} from Moon)")
        print(f"   Effect: {ss['phase']}")
        
        kd = res["kuja_dosha"]
        cc = C.RED if kd["severity"] == "HIGH" else (C.YELLOW if "CANCELLED" in kd["status"] else C.GREEN)
        print(f"\n{C.BOLD}--- Kuja Dosha (Manglik) ---{C.RESET}")
        print(f" {cc}[{kd['status']}]{C.RESET}")
        for t in kd.get("triggers", []):
            print(f"   [!] {t}")
        for c in kd.get("cancellations", []):
            print(f"   [+] {c}")
        if not kd.get("triggers"):
            print(f"   ✓ No Manglik affliction detected.")
        print()

    def show_yogas_analysis(self):
        if not self.chart_obj: return
        p = self.active_profile
        from yogas import evaluate_all_yogas
        res = evaluate_all_yogas(self.chart_obj)
        
        print(f"\n{C.BOLD}{C.CYAN}=== CLASSICAL YOGAS ({p['name']}) ==={C.RESET}")
        if not res:
            print(f" {C.YELLOW}No core classical Yogas detected.{C.RESET}")
            return
            
        for y in res:
            cc = C.GREEN if y["polarity"] == "supporting" else (C.RED if y["polarity"] == "contradicting" else C.YELLOW)
            print(f" {cc}[{y['name']}]{C.RESET} {y['reason']}")
            for m in y.get("exceptions_encountered", []):
                print(f"   -> Cancellation/Mod: {m}")
        print()

    def show_cancellations_analysis(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from cancellations import CancellationEngine
        canc = CancellationEngine(self.chart_obj).evaluate_all()

        print(f"\n{C.BOLD}{C.CYAN}=== CANCELLATIONS, NEECHA BHANGA & VIPAREETA YOGAS ({p['name']}) ==={C.RESET}")
        nb = canc.get("neecha_bhanga_raja_yogas", [])
        if nb:
            print(f"\n--- Neecha Bhanga Raja Yogas ---")
            for n in nb:
                color = C.GREEN if n["is_cancelled"] else C.RED
                print(f" {color}[{n['grade']}]{C.RESET} {n['planet']} in {n['debilitated_sign']}")
                for cond in n["conditions_met"]:
                    print(f"   + {cond}")
        vry = canc.get("vipareeta_raja_yogas", [])
        if vry:
            print(f"\n--- Vipareeta Raja Yogas ---")
            for v in vry:
                color = C.GREEN if v["is_pure"] else C.YELLOW
                print(f" {color}[{v['status']}]{C.RESET} {v['description']}")
        yb = canc.get("yoga_bhangas", [])
        if yb:
            print(f"\n--- Yoga Bhangas (Severe Impairments) ---")
            for b in yb:
                print(f" {C.RED}[!]{C.RESET} {b['detail']}")
        print()

    def show_advanced_avasthas(self):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        p = self.active_profile
        from advanced_avasthas import AdvancedAvasthaEngine
        eng = AdvancedAvasthaEngine(self.chart_obj)
        res = eng.combine_all()
        
        print(f"\n{C.BOLD}{C.CYAN}=== ADVANCED AVASTHAS & CONTRADICTIONS ({p['name']}) ==={C.RESET}")
        
        laj = res.get("lajjitadi_avasthas", {})
        if laj:
            print(f"\n{C.BOLD}--- Lajjitadi Avasthas (Psychological States) ---{C.RESET}")
            for pl, states in laj.items():
                print(f" {C.YELLOW}{pl}:{C.RESET}")
                for st in states:
                    print(f"  - [{st['state']}] {st['reason']}")
        
        ret = res.get("retrogression_anomalies", {})
        if ret:
            print(f"\n{C.BOLD}--- Retrogression Anomalies (Cheshta) ---{C.RESET}")
            for pl, data in ret.items():
                color = C.GREEN if "NEICHA_BHANGA" in data["effect"] else (C.RED if "CANCELLATION" in data["effect"] else C.MAGENTA)
                print(f" {color}[{data['effect']}]{C.RESET} {pl}: {data['description']}")
        print()

    def show_ontology_analysis(self, query_arg: str = ""):
        from jyotisha_ontology import JyotishaOntology
        target_q = query_arg.strip() if query_arg.strip() else "career growth and foreign business scaling"
        res = JyotishaOntology.classify_question(target_q)
        
        print(f"\n{C.BOLD}{C.CYAN}=== 🏛️ 70-NODE JYOTIṢA QUESTION ONTOLOGY ROUTING ==={C.RESET}")
        print(f" {C.BOLD}Query:{C.RESET}                 {target_q}")
        print(f" {C.BOLD}Matched Node:{C.RESET}          {C.GREEN}[Node {res.node_id}] {res.node_title}{C.RESET}")
        print(f" {C.BOLD}Sub-Node:{C.RESET}              {C.MAGENTA}{res.subnode_id}: {res.subnode_title}{C.RESET}")
        print(f" {C.BOLD}Category:{C.RESET}              {res.category}")
        print(f" {C.BOLD}Query Mode:{C.RESET}            {res.query_mode_id}: {res.query_mode}")
        print(f" {C.BOLD}Primary Houses:{C.RESET}        {res.primary_houses} (Secondary: {res.secondary_houses})")
        print(f" {C.BOLD}Primary Karakas:{C.RESET}       {', '.join(res.primary_karakas)}")
        print(f" {C.BOLD}Primary Vargas:{C.RESET}        {', '.join(res.primary_vargas)}")
        if res.jaimini_factors:
            print(f" {C.BOLD}Jaimini Factors:{C.RESET}       {', '.join(res.jaimini_factors)}")
        if res.kp_significators:
            print(f" {C.BOLD}KP Significators:{C.RESET}      {res.kp_significators}")
        print(f" {C.BOLD}System Priority:{C.RESET}       {' > '.join(res.system_priority)}")
        if res.cross_domain_links:
            print(f" {C.BOLD}Cross-Domain Links:{C.RESET}    {C.YELLOW}{', '.join(res.cross_domain_links)}{C.RESET}")
        print(f" {C.BOLD}Falsification Gates:{C.RESET}")
        for gate in res.falsification_checks:
            print(f"   🛡️ {gate}")
        print()

    def show_forward_timing(self, domain_arg: str = ""):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return
        domain = domain_arg.strip().upper() if domain_arg.strip() else "CAREER"
        p = self.active_profile
        from forward_timing_scanner import ForwardTimingScanner
        import pytz
        scanner = ForwardTimingScanner(self.chart_obj)
        now = datetime.now(pytz.utc)
        windows = scanner.scan_domain_windows(domain, start_date=now, months_ahead=36)

        print(f"\n{C.BOLD}{C.CYAN}=== FORWARD TIMING SCANNER: {domain} 36-MONTH ({p['name']}) ==={C.RESET}")
        if not windows:
            print(f" {C.YELLOW}No peak qualifying windows for {domain} in next 36 months.{C.RESET}")
            return
        for i, w in enumerate(windows, 1):
            cc = C.GREEN if "HIGH" in w["confidence"] else C.YELLOW
            print(f"\n Window #{i}: {w['start_date']} to {w['end_date']}  [{cc}{w['confidence']}{C.RESET} | Score: {w['score']}]")
            print(f"   Dasha: {C.MAGENTA}{w['dasha_trigger']}{C.RESET}")
            for dr in w.get("dasha_reasons", []):
                print(f"   + {dr}")
            for tr in w.get("transit_reasons", []):
                print(f"   + {tr}")
        print()

    def run_reconciliation(self, question: str, target_year: int = None):
        if not self.chart_obj:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return

        target_dt = datetime(target_year or datetime.now().year, 6, 1)
        print(f"\n{C.CYAN}Running Reconciliation Engine for:{C.RESET} '{question}' (Target Year: {target_dt.year})")
        
        engine = EventPredictionEngine(self.chart_obj)
        res = engine.analyze_event(question, target_dt)
        
        print(f"\n{C.BOLD}═══ 2.4 RECONCILIATION & CONTRADICTION MATRIX ═══{C.RESET}")
        print(f" {C.BOLD}Domain:{C.RESET}                 {res.domain}")
        print(f" {C.BOLD}Primary Methodology:{C.RESET}    {res.methodology_route.get('primary_methodology')}")
        print(f" {C.BOLD}Secondary Methods:{C.RESET}      {', '.join(res.methodology_route.get('secondary_methodologies', []))}")
        print(f" {C.BOLD}Natal Promise Status:{C.RESET}   {C.MAGENTA}{res.natal_promise.get('status')}{C.RESET}")
        print(f" {C.BOLD}Convergence Status:{C.RESET}     {C.YELLOW}{res.convergence}{C.RESET}")
        print(f" {C.BOLD}Double Transits (Rao):{C.RESET}  Houses activated: {res.timing.get('activated_natal_houses', [])}")
        
        # Supporting vs Contradicting
        sup = res.natal_promise.get("supporting_evidence", [])
        con = res.natal_promise.get("contradicting_evidence", [])
        
        print(f"\n{C.GREEN}--- Supporting Factors ({len(sup)}) ---{C.RESET}")
        for s in sup[:5]:
            print(f" [✓] {s.get('subject', 'General')}: {s.get('reason')}")
        if len(sup) > 5:
            print(f" ... and {len(sup)-5} more supporting indicators.")
            
        print(f"\n{C.RED}--- Contradicting Factors ({len(con)}) ---{C.RESET}")
        for c in con[:5]:
            print(f" [✗] {c.get('subject', 'General')}: {c.get('reason')}")
        if len(con) > 5:
            print(f" ... and {len(con)-5} more friction indicators.")

        # Multi-Tradition Arbitration Matrix (Priority Ladder, not discards)
        try:
            from tradition_arbiter import run_full_arbitration
            p = self.active_profile
            birth_local = {"year": p["year"], "month": p["month"], "day": p["day"],
                           "hour": p["hour"], "minute": p["minute"],
                           "lat": p["lat"], "lon": p["lon"],
                           "tz": p.get("tz", "Asia/Kolkata")}
            arb = run_full_arbitration(
                self.chart_obj, domain=res.domain, question=question,
                domain_analysis=None, birth_local=birth_local,
                target_date=target_dt)
            print(f"\n{C.BOLD}═══ MULTI-TRADITION ARBITRATION MATRIX ═══{C.RESET}")
            print(f" Priority Ladder: {' > '.join(arb['priority_ladder'])}")
            for v in arb["verdicts"]:
                color = C.GREEN if v["verdict"] == "FAVORABLE" else (C.RED if v["verdict"] == "UNFAVORABLE" else C.YELLOW)
                print(f" [{color}{v['tradition']:9s}{C.RESET}] {color}{v['verdict']:12s}{C.RESET} "
                      f"conf={v['confidence'][:22]:22s} weight={v['authority_weight']:.2f} score={v['weighted_score']:+.2f}")
            print(f" {C.BOLD}Weighted Total:{C.RESET} {arb['weighted_total']:+.2f}  →  "
                  f"{C.MAGENTA}{C.BOLD}FINAL: {arb['final_verdict']}{C.RESET}")
            if arb["contradiction_detected"]:
                print(f" {C.YELLOW}⚠ Genuine contradiction detected — dissent preserved, not discarded:{C.RESET}")
                for d in arb["dissent_register"]:
                    print(f"    [{d['tradition']}] says {d['verdict']} ({d['confidence']})")
        except Exception as e:
            print(f" {C.DIM}(Arbitration matrix unavailable: {e}){C.RESET}")

        print(f"\n{C.BOLD}LLM Guidance Payload:{C.RESET} {res.llm_guidance}\n")
        return res

    def synthesize_response(self, question: str):
        if not self.chart_obj or not self.chart_dict:
            print(f"{C.RED}No chart calculated.{C.RESET}")
            return

        # 1. Run reconciliation engine
        target_year = datetime.now().year
        # Simple year extraction heuristic
        for word in question.split():
            if word.isdigit() and len(word) == 4 and int(word) > 1900:
                target_year = int(word)
                break

        engine = EventPredictionEngine(self.chart_obj)
        recon_result = engine.analyze_event(question, datetime(target_year, 6, 1))
        
        # 2. RAG retrieval for relevant topic
        rag_context = ""
        rag = self.get_rag()
        if rag:
            try:
                raw_rag = rag.retrieve_with_filters(question, num_results=3, use_hyde=False, use_reranker=True)
                rag_json = json.loads(raw_rag)
                rag_docs = [d.get("text", "")[:400] for d in rag_json.get("results", [])]
                rag_context = "\n\n".join(rag_docs)[:1000]
            except Exception:
                rag_context = "Classical principles indicate standard house and dasha results."

        # Real-time and Advanced Multi-System Snapshot
        p = self.active_profile
        from realtime_engine import RealtimeEngine
        from kp_engine import KPEngine
        from nadi_engine import NadiEngine
        from pancha_pakshi_engine import PanchaPakshiEngine
        from institutional_chakra_engine import InstitutionalChakraEngine
        from ashtakavarga_engine import AshtakavargaEngine

        rt_snapshot = RealtimeEngine.get_realtime_correlation_snapshot(self.chart_obj, p["lat"], p["lon"], p["tz"])
        kp_chart = KPEngine.calculate_kp_chart(p["year"], p["month"], p["day"], p["hour"], p["minute"], p["lat"], p["lon"], p["tz"])
        bnn_data = NadiEngine.evaluate_jeeva_and_karma(self.chart_obj)
        kota_defense = InstitutionalChakraEngine.calculate_kota_chakra(self.chart_obj, rt_snapshot["live_planets"])

        # Pancha Pakshi
        from varga_engine import VargaEngine
        moon_p = self.chart_obj.planets.get("Moon")
        sun_p = self.chart_obj.planets.get("Sun")
        m_lon = (VargaEngine.get_sign_index(moon_p.sign) * 30.0) + moon_p.degree if moon_p else 0.0
        s_lon = (VargaEngine.get_sign_index(sun_p.sign) * 30.0) + sun_p.degree if sun_p else 0.0
        bird_info = PanchaPakshiEngine.get_birth_bird(m_lon, s_lon)
        pakshi_now = PanchaPakshiEngine.calculate_current_activity(bird_info["birth_bird"], datetime.now(pytz.timezone(p["tz"])))

        # 3. Construct Grandmaster Synthesis Prompt
        timing = recon_result.timing
        transit_signs = timing.get("double_transit_signs", [])
        activated_houses = timing.get("activated_natal_houses", [])
        yogas_formed = [y.get("name") for y in self.chart_dict.get("Yogas_Found", [])]

        system_prompt = (
            "You are the Grandmaster Astrologer AI, an expert in classical Vedic Jyotisha.\n"
            "CRITICAL ANTI-HALLUCINATION RULES (violation invalidates the entire reading):\n"
            "1. You MUST use ONLY the deterministic values provided below. The Python backend has already "
            "calculated every planetary position, transit sign, activated house, dasha, and yoga.\n"
            "2. NEVER recompute or infer transit signs or activated houses yourself. If the payload says the "
            "double transit is in sign X activating house(s) [N], you state EXACTLY sign X and house(s) [N]. "
            "Do NOT convert signs to houses on your own or substitute a different sign/house.\n"
            "3. Treat every yoga in 'Yogas Formed' as an established FACT. If a yoga is formed by a planetary "
            "combination (e.g. Budhaditya from Sun+Mercury conjunction), you must credit it as a supporting "
            "factor even if the same planets carry afflictions elsewhere. State both the strength and the affliction; do not erase the yoga.\n"
            "4. Do NOT invent mantras, gemstones, or timings not present in the provided data.\n"
            "Format your reading authoritatively with:\n"
            "1. Astrological Logic First (House lords, dashas, transits, cancellations, KP/BNN/Pakshi factors)\n"
            "2. Direct tangible prediction/verdict\n"
            "3. The Grandmaster's Protocol (Remedies & Mitigations: Mantras, charities, gemstones)\n"
        )

        user_prompt = f"""
User Question: {question}

=== FIXED DETERMINISTIC FACTS (USE VERBATIM — DO NOT RECOMPUTE) ===
Ascendant (Lagna): {self.chart_obj.ascendant_sign}
Natal Promise: {recon_result.natal_promise.get('status')}
Methodology Convergence: {recon_result.convergence}
Analysis Target Year: {target_year}
Double-Transit Sign(s) (Saturn+Jupiter): {transit_signs}
Activated Natal House(s) by Double Transit: {activated_houses}
Current Dasha: {json.dumps(self.chart_dict.get('Current_Dasha', {}))}
Yogas Formed (each is an established fact): {yogas_formed}

=== KP SYSTEM (249 CUSPAL SUB-LORD PROMISES) ===
{json.dumps(kp_chart.get('csl_analysis', {}), indent=2)}

=== BHRIGU NANDI NADI (BNN LIFE & CAREER PATTERNS) ===
Karma Karaka (Saturn) Combo: {bnn_data['karma_karaka'].get('composite_bnn_combination')}
Jeeva Karaka (Jupiter) Combo: {bnn_data['jeeva_karaka'].get('composite_bnn_combination')}
Patterns: {bnn_data.get('bnn_career_patterns', [])}

=== TAMIL SIDDHA PANCHA PAKSHI BIO-TIMING ===
Birth Bird: {bird_info['birth_bird']}
Current Bio-State: {pakshi_now['active_activity']} ({pakshi_now['potency_score']}% potency) -> {pakshi_now['action_guidance']}

=== INSTITUTIONAL KOTA CHAKRA DEFENSE ===
Defense Status: {kota_defense.get('siege_status')}
Tactical Verdict: {kota_defense.get('tactical_verdict')}

=== REAL-TIME SKY & TRANSIT ASPECTS ===
Active Planetary Hora: {rt_snapshot['planetary_hora']['active_hora']}
KP 5 Ruling Planets: {rt_snapshot['kp_ruling_planets']['ruling_planets_ordered']}
Tight Catalytic Aspects Hits (<= 1.2° orb): {json.dumps(rt_snapshot.get('catalytic_aspects', []))}

=== FULL DETERMINISTIC RECONCILIATION RESULT ===
{json.dumps(recon_result.to_dict(), indent=2)}

=== REMEDIES AVAILABLE (use only these) ===
{json.dumps(self.chart_dict.get('Remedies', {}), indent=2)}

=== CLASSICAL TEXT RULES (retrieved from ingested scriptures) ===
{rag_context}

Reminder: The target year analyzed is {target_year}, double transit is in {transit_signs} activating house(s) {activated_houses}. Use these EXACT values.
Please provide your Grandmaster consultation now.
"""
        print(f"\n{C.CYAN}{C.BOLD}✦ Consulting the Grandmaster ({self.active_provider})...{C.RESET}\n")
        try:
            llm = LLMProvider.get_llm(self.active_provider)
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            text_output = extract_text(response.content)
            print(f"{C.BOLD}{C.WHITE}{text_output}{C.RESET}\n")
        except Exception as e:
            print(f"{C.RED}LLM synthesis error: {e}{C.RESET}\n")

    def edit_birth_details(self):
        print(f"\n{C.BOLD}{C.CYAN}═══ ENTER NEW BIRTH DETAILS ═══{C.RESET}")
        try:
            name = input(" Full Name (e.g. Seeker): ").strip() or "Seeker"
            year = int(input(" Year of Birth (YYYY): ").strip())
            month = int(input(" Month of Birth (1-12): ").strip())
            day = int(input(" Day of Birth (1-31): ").strip())
            hour = int(input(" Hour of Birth (0-23): ").strip())
            minute = int(input(" Minute of Birth (0-59): ").strip())
            
            city = input(" Birth City / Location (e.g. New York, London, New Delhi): ").strip()
            while not city:
                city = input(f" {C.YELLOW}Location is required for Panchangam & Ascendant calculation. Enter City: {C.RESET}").strip()

            lat, lon, tz = None, None, None
            try:
                from geopy.geocoders import Nominatim
                from timezonefinder import TimezoneFinder
                geolocator = Nominatim(user_agent="astrology_ai_cli")
                loc = geolocator.geocode(city)
                if loc:
                    lat = round(loc.latitude, 4)
                    lon = round(loc.longitude, 4)
                    tf = TimezoneFinder()
                    tz = tf.timezone_at(lng=loc.longitude, lat=loc.latitude) or "UTC"
                    print(f" {C.GREEN}✓ Geocoded:{C.RESET} {loc.address[:50]}... | Lat: {lat}, Lon: {lon}, Timezone: {tz}")
            except Exception:
                pass

            if lat is None or lon is None:
                lat_str = input(" Latitude (e.g. 19.0760): ").strip()
                lat = float(lat_str) if lat_str else 0.0
                lon_str = input(" Longitude (e.g. 72.8777): ").strip()
                lon = float(lon_str) if lon_str else 0.0
                tz = input(" Timezone (e.g. Asia/Kolkata, America/New_York): ").strip() or "UTC"

            self.active_profile = {
                "name": name, "year": year, "month": month, "day": day,
                "hour": hour, "minute": minute, "lat": lat, "lon": lon, "tz": tz, "city": city
            }
            self.calculate_active_chart()
            print(f"\n{C.GREEN}✓ Chart successfully calculated and set active!{C.RESET}\n")
            self.show_chart_summary()
        except Exception as e:
            print(f"{C.RED}Invalid input: {e}{C.RESET}")

    def run(self):
        self.banner()
        while True:
            try:
                cmd = input(f"{C.BOLD}{C.CYAN}AstrologyAI [{self.active_profile['name']}] > {C.RESET}").strip()
                if not cmd:
                    continue

                if cmd in ["/exit", "/quit", "exit", "quit"]:
                    print(f"{C.CYAN}Cosmic journey concluded. Farewell! ✨{C.RESET}")
                    break

                elif cmd in ["/help", "help", "?"]:
                    print(f"\n{C.BOLD}Available Commands:{C.RESET}")
                    print(f" {C.CYAN}/chart{C.RESET}               - Display the complete Kundli breakdown, vargas & yogas")
                    print(f" {C.CYAN}/panchang{C.RESET}            - Location-Based Drik Panchanga: Tithi, Nakshatra, Choghadiya, Rahu Kalam")
                    print(f" {C.CYAN}/realtime{C.RESET}            - Display live transits, active Hora, KP Ruling Planets & Gochara Vedha")
                    print(f" {C.CYAN}/kp{C.RESET}                  - KP System: 12 Placidus Cusps, 249 Sub-Lords, ABCD Matrix & CSL Promises")
                    print(f" {C.CYAN}/bnn{C.RESET}                 - Bhrigu Nandi Nadi: Directional Trines (1-5-9), Jeeva/Karma axes")
                    print(f" {C.CYAN}/kakshya [planet]{C.RESET}    - Ashtakavarga: 3°45' Kakshya Micro-Transit Fructification Windows")
                    print(f" {C.CYAN}/pakshi{C.RESET}              - Tamil Siddha 5-Bird Bio-Timing: Birth Bird & active bio-state")
                    print(f" {C.CYAN}/tajaka <year>{C.RESET}       - Annual Solar Return: Muntha, Sahams (Punya, Karma) & Ithasala Yogas")
                    print(f" {C.CYAN}/chakras [entity]{C.RESET}    - Institutional Defense: Kota Chakra (Fortress) & Sarvatobhadra (SBC)")
                    print(f" {C.CYAN}/gann [price]{C.RESET}        - Financial Astrology: W.D. Gann Square of 9 Price-Time Squaring")
                    print(f" {C.CYAN}/cosmo{C.RESET}               - Cosmobiology: 90° Graphic Dial & Planetary Midpoint Trees (A/B=C)")
                    print(f" {C.CYAN}/remedy <planet>{C.RESET}     - Prescriptive Remedial Matrix: Vedic Mantras, Daana (Hora), Lal Kitab")
                    print(f" {C.CYAN}/sensitive{C.RESET}            - Critical Sensitivities: 22nd Drekkana, 64th Navamsha, Mrityu Bhagas")
                    print(f" {C.CYAN}/upagraha{C.RESET}             - Non-Luminous Shadows: Mandi, Gulika, Dhuma, Vyatipata")
                    print(f" {C.CYAN}/avastha{C.RESET}              - Mood & Mechanics: Lajjitadi Avasthas & Retrogression (Cheshta) overrides")
                    print(f" {C.CYAN}/dosha{C.RESET}                - Afflictions: Sade Sati, Kantaka Shani, Kuja Dosha (Manglik) & Bhanga")
                    print(f" {C.CYAN}/yogas{C.RESET}                - Benefic Multi-Planet Yogas (Gajakesari, Budhaditya, Kemadruma)")
                    print(f" {C.CYAN}/cancel{C.RESET}               - Verifications: NBRY, Vipareeta Raja Yoga, Yoga Bhangas")
                    print(f" {C.CYAN}/numero [name]{C.RESET}       - Ank Jyotish, Chaldean Namank & Katapayadi Sankhya")
                    print(f" {C.CYAN}/forward <domain>{C.RESET}    - Forward Timing Scanner: 36-Month Predictive Target Windows")
                    print(f" {C.CYAN}/varga <D1-D60>{C.RESET}      - Inspect specific divisional chart (e.g. /varga D9, /varga D10, /varga D60)")
                    print(f" {C.CYAN}/preset <1|2|3>{C.RESET}      - Switch birth profile (1: India 1947, 2: Steve Jobs, 3: Einstein)")
                    print(f" {C.CYAN}/birth{C.RESET}               - Enter custom birth coordinates and details")
                    print(f" {C.CYAN}/rag <query>{C.RESET}          - Run classical RAG query with HyDE & Cross-Encoder")
                    print(f" {C.CYAN}/learn <path>{C.RESET}         - Auto-ingest new book/PDF/folder into RAG & refresh BM25")
                    print(f" {C.CYAN}/sources{C.RESET}              - List all ingested classical sources in the knowledge base")
                    print(f" {C.CYAN}/reconcile <q>{C.RESET}       - Run 2.4 Reconciliation Engine without LLM synthesis")
                    print(f" {C.CYAN}/provider <name>{C.RESET}     - Switch model provider (auto, gemini-3.6-flash, groq, openrouter, ollama)")
                    print(f" {C.CYAN}/mode <name>{C.RESET}         - Switch execution mode (grandmaster, raw)")
                    print(f" {C.CYAN}/clear{C.RESET}               - Clear screen and reprint banner")
                    print(f" {C.CYAN}<Any Question>{C.RESET}       - Ask any astrological question (e.g. 'Will I get married in 2027?')\n")

                elif cmd.startswith("/panchang") or cmd.startswith("/almanac"):
                    parts = cmd.split(maxsplit=1)
                    c_arg = parts[1] if len(parts) > 1 else ""
                    self.show_drik_panchang(c_arg)

                elif cmd in ["/realtime", "/transits", "/live"]:
                    self.show_realtime_snapshot()

                elif cmd.startswith("/ontology") or cmd.startswith("/nodes"):
                    parts = cmd.split(maxsplit=1)
                    q_arg = parts[1] if len(parts) > 1 else ""
                    self.show_ontology_analysis(q_arg)

                elif cmd == "/kp":
                    self.show_kp_analysis()

                elif cmd.startswith("/bnn"):
                    self.show_bnn_analysis()

                elif cmd.startswith("/kakshya"):
                    parts = cmd.split(maxsplit=1)
                    p_arg = parts[1] if len(parts) > 1 else ""
                    self.show_kakshya_analysis(p_arg)

                elif cmd.startswith("/gann"):
                    parts = cmd.split(maxsplit=1)
                    pr_arg = parts[1] if len(parts) > 1 else ""
                    self.show_gann_analysis(pr_arg)

                elif cmd.startswith("/cosmo") or cmd.startswith("/dial"):
                    self.show_cosmo_analysis()

                elif cmd in ["/pakshi", "/panchapakshi"]:
                    self.show_pakshi_analysis()

                elif cmd.startswith("/tajaka") or cmd.startswith("/varshaphala"):
                    parts = cmd.split(maxsplit=1)
                    y_arg = parts[1] if len(parts) > 1 else ""
                    self.show_tajaka_analysis(y_arg)

                elif cmd.startswith("/chakras") or cmd.startswith("/kota") or cmd.startswith("/sbc"):
                    parts = cmd.split(maxsplit=1)
                    ent_arg = parts[1] if len(parts) > 1 else ""
                    self.show_chakras_analysis(ent_arg)

                elif cmd.startswith("/remedy") or cmd.startswith("/remedies"):
                    parts = cmd.split(maxsplit=1)
                    p_arg = parts[1] if len(parts) > 1 else ""
                    self.show_remedy_analysis(p_arg)

                elif cmd == "/chart":
                    self.show_chart_summary()

                elif cmd.startswith("/varga"):
                    parts = cmd.split(maxsplit=1)
                    if len(parts) > 1:
                        self.show_varga_chart(parts[1])
                    else:
                        print("Usage: /varga <D1|D2|D3|D4|D7|D9|D10|D12|D16|D20|D24|D27|D30|D40|D45|D60>")

                elif cmd.startswith("/sensitive"):
                    self.show_sensitive_analysis()

                elif cmd.startswith("/upagraha"):
                    self.show_upagrahas_analysis()

                elif cmd.startswith("/dosha") or cmd.startswith("/sadesati") or cmd.startswith("/manglik"):
                    self.show_dosha_analysis()

                elif cmd.startswith("/yogas"):
                    self.show_yogas_analysis()

                elif cmd.startswith("/cancel") or cmd.startswith("/bhanga") or cmd.startswith("/vry") or cmd.startswith("/nbry"):
                    self.show_cancellations_analysis()
                    
                elif cmd.startswith("/numero") or cmd.startswith("/ank"):
                    parts = cmd.split(maxsplit=1)
                    n_arg = parts[1] if len(parts) > 1 else self.active_profile.get("name", "")
                    self.show_numerology_analysis(n_arg)

                elif cmd.startswith("/avastha") or cmd.startswith("/retro"):
                    self.show_advanced_avasthas()

                elif cmd.startswith("/forward") or cmd.startswith("/timing"):
                    parts = cmd.split(maxsplit=1)
                    d_arg = parts[1] if len(parts) > 1 else ""
                    self.show_forward_timing(d_arg)

                elif cmd == "/clear":
                    os.system("cls" if os.name == "nt" else "clear")
                    self.banner()

                elif cmd.startswith("/preset"):
                    parts = cmd.split()
                    if len(parts) > 1 and parts[1] in PRESETS:
                        self.active_profile = PRESETS[parts[1]]
                        self.calculate_active_chart()
                        print(f"{C.GREEN}✓ Switched to preset: {self.active_profile['name']}{C.RESET}")
                    else:
                        print(f"Usage: /preset <1|2|3> (1: India, 2: Steve Jobs, 3: Einstein)")

                elif cmd == "/birth":
                    self.edit_birth_details()

                elif cmd.startswith("/provider"):
                    parts = cmd.split(maxsplit=1)
                    if len(parts) > 1:
                        self.active_provider = parts[1].strip()
                        print(f"{C.GREEN}✓ Active provider set to: {self.active_provider}{C.RESET}")
                    else:
                        print(f"Current provider: {self.active_provider}. Usage: /provider <gemini-3.6-flash|groq|openrouter|ollama|auto>")

                elif cmd.startswith("/mode"):
                    parts = cmd.split(maxsplit=1)
                    if len(parts) > 1:
                        target_mode = parts[1].lower().strip()
                        if target_mode in ["client_safe", "client", "safe", "bounded"]:
                            from modes import set_active_mode
                            set_active_mode("client_safe")
                            self.active_mode = "client_safe"
                            print(f"{C.GREEN}✓ Active execution mode set to: CLIENT_SAFE (Bounded Guardrails & Disclaimers){C.RESET}")
                        elif target_mode in ["unconstrained", "grandmaster", "raw", "unfiltered"]:
                            from modes import set_active_mode
                            set_active_mode("unconstrained")
                            self.active_mode = "unconstrained"
                            print(f"{C.GREEN}✓ Active execution mode set to: UNCONSTRAINED (Raw Grandmaster Astronomical Math){C.RESET}")
                        else:
                            print(f"Usage: /mode <client_safe|unconstrained>")
                    else:
                        from modes import get_active_mode
                        print(f"Current mode: {get_active_mode()}. Usage: /mode <client_safe|unconstrained>")

                elif cmd.startswith("/learn") or cmd.startswith("/ingest"):
                    parts = cmd.split(maxsplit=1)
                    if len(parts) > 1:
                        self.learn_document(parts[1])
                    else:
                        print("Usage: /learn <path_to_pdf_or_txt_or_folder>")

                elif cmd == "/sources":
                    self.show_sources()

                elif cmd.startswith("/rag"):
                    q = cmd[4:].strip()
                    if q:
                        self.run_rag_search(q)
                    else:
                        print("Usage: /rag <query about yogas, combinations, or classical rules>")

                elif cmd.startswith("/reconcile"):
                    q = cmd[10:].strip()
                    if q:
                        self.run_reconciliation(q)
                    else:
                        print("Usage: /reconcile <question e.g. Will I get promoted in 2027?>")

                else:
                    # Direct question flow
                    if self.active_mode == "raw":
                        self.run_reconciliation(cmd)
                    else:
                        self.synthesize_response(cmd)

            except (KeyboardInterrupt, EOFError):
                print(f"\n{C.CYAN}Cosmic journey concluded. Farewell! ✨{C.RESET}")
                break
            except Exception as e:
                print(f"{C.RED}Error: {e}{C.RESET}")

if __name__ == "__main__":
    cli = AstrologyCLI()
    cli.run()
