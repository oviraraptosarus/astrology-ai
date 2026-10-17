from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pytz
import swisseph as swe
from config import Config
from astronomy_core import AstronomyCore, NAKSHATRAS, DASHA_LORDS

class DashaEngine:
    """
    Dedicated engine for calculating planetary periods (Dashas).
    Supports generating full timelines for Vimshottari Dasha with configurable
    year-length models (K.N. Rao 365.2422d Solar Calendar, 360d Savana/JHora, 365.25d Julian)
    and multi-model transition corridor consensus.
    """
    
    DASHA_LORDS = DASHA_LORDS
    DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    TOTAL_YEARS = 120.0
    
    @staticmethod
    def _jd_to_iso(jd: float) -> str:
        y, m, d, h_dec = swe.revjul(jd, swe.GREG_CAL)
        h = int(h_dec)
        min_dec = (h_dec - h) * 60.0
        minute = int(min_dec)
        sec = int(round((min_dec - minute) * 60.0))
        if sec >= 60:
            sec = 0
            minute += 1
        if minute >= 60:
            minute = 0
            h += 1
        if h >= 24:
            return DashaEngine._jd_to_iso(jd + (1.0/24.0))
        return f"{y:04d}-{m:02d}-{d:02d}T{h:02d}:{minute:02d}:{sec:02d}Z"
    
    @staticmethod
    def _dt_to_jd(dt: datetime) -> float:
        utc_dt = dt.astimezone(pytz.utc) if dt.tzinfo else pytz.utc.localize(dt)
        hour_dec = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
        return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)

    @staticmethod
    def calculate_vimshottari_timeline(birth_time_utc: datetime, moon_longitude: float, num_levels: int = 3, year_length: Optional[float] = None) -> List[Dict]:
        """
        Calculates the Vimshottari Dasha timeline from birth to 120 years.
        Supports up to 3 levels (Mahadasha, Antardasha, Pratyantardasha).
        year_length: Days per year (default from Config: 365.2422 for Solar/K.N. Rao, 360.0 for Savana/JHora).
        """
        if year_length is None:
            year_length = Config.get_year_length_days()

        nak_idx, _, fraction = AstronomyCore.calculate_nakshatra(moon_longitude)
        lord_idx = nak_idx % 9
        
        fraction_left = 1.0 - fraction
        balance_years = fraction_left * DashaEngine.DASHA_YEARS[lord_idx]
        
        timeline = []
        start_jd = DashaEngine._dt_to_jd(birth_time_utc)
        current_jd = start_jd
        
        # We simulate up to 120 years, starting from the current fractional lord
        c_idx = lord_idx
        elapsed_years = 0.0
        
        # Calculate the first (fractional) Mahadasha
        first_md_years = balance_years
        first_md_end_jd = current_jd + (first_md_years * year_length)
        
        md_node = {
            "level": 1,
            "lord": DashaEngine.DASHA_LORDS[c_idx],
            "start": DashaEngine._jd_to_iso(current_jd),
            "end": DashaEngine._jd_to_iso(first_md_end_jd),
            "sub_periods": []
        }
        
        if num_levels >= 2:
            md_node["sub_periods"] = DashaEngine._calculate_antardashas(
                c_idx, current_jd, first_md_years, num_levels, is_fractional=True, total_md_years=DashaEngine.DASHA_YEARS[c_idx], year_length=year_length
            )
            
        timeline.append(md_node)
        current_jd = first_md_end_jd
        elapsed_years += first_md_years
        c_idx = (c_idx + 1) % 9
        
        # Calculate subsequent Mahadashas
        while elapsed_years < DashaEngine.TOTAL_YEARS:
            md_years = DashaEngine.DASHA_YEARS[c_idx]
            md_end_jd = current_jd + (md_years * year_length)
            
            md_node = {
                "level": 1,
                "lord": DashaEngine.DASHA_LORDS[c_idx],
                "start": DashaEngine._jd_to_iso(current_jd),
                "end": DashaEngine._jd_to_iso(md_end_jd),
                "sub_periods": []
            }
            
            if num_levels >= 2:
                md_node["sub_periods"] = DashaEngine._calculate_antardashas(
                    c_idx, current_jd, md_years, num_levels, is_fractional=False, total_md_years=md_years, year_length=year_length
                )
                
            timeline.append(md_node)
            current_jd = md_end_jd
            elapsed_years += md_years
            c_idx = (c_idx + 1) % 9
            
        return timeline

    @staticmethod
    def _calculate_antardashas(md_lord_idx: int, start_jd: float, md_duration: float, num_levels: int, is_fractional: bool, total_md_years: float, year_length: float) -> List[Dict]:
        sub_periods = []
        current_jd = start_jd
        
        ad_idx = md_lord_idx
        
        time_elapsed_before_birth = total_md_years - md_duration
        accumulated_ad_time = 0.0
        
        for _ in range(9):
            ad_total_years = (total_md_years * DashaEngine.DASHA_YEARS[ad_idx]) / DashaEngine.TOTAL_YEARS
            
            if is_fractional:
                if accumulated_ad_time + ad_total_years <= time_elapsed_before_birth:
                    accumulated_ad_time += ad_total_years
                    ad_idx = (ad_idx + 1) % 9
                    continue
                else:
                    time_spent_in_this_ad_before_birth = time_elapsed_before_birth - accumulated_ad_time
                    ad_actual_years = ad_total_years - time_spent_in_this_ad_before_birth
                    is_fractional = False
            else:
                ad_actual_years = ad_total_years
                
            ad_end_jd = current_jd + (ad_actual_years * year_length)
            
            ad_node = {
                "level": 2,
                "lord": DashaEngine.DASHA_LORDS[ad_idx],
                "start": DashaEngine._jd_to_iso(current_jd),
                "end": DashaEngine._jd_to_iso(ad_end_jd),
                "sub_periods": []
            }
            
            if num_levels >= 3:
                ad_node["sub_periods"] = DashaEngine._calculate_pratyantardashas(
                    ad_idx, current_jd, ad_actual_years, total_md_years, ad_total_years, year_length=year_length
                )
                
            sub_periods.append(ad_node)
            current_jd = ad_end_jd
            accumulated_ad_time += ad_total_years
            ad_idx = (ad_idx + 1) % 9
            
        return sub_periods

    @staticmethod
    def _calculate_pratyantardashas(ad_lord_idx: int, start_jd: float, ad_duration: float, total_md_years: float, total_ad_years: float, year_length: float) -> List[Dict]:
        sub_periods = []
        current_jd = start_jd
        pd_idx = ad_lord_idx
        
        for _ in range(9):
            pd_total_years = (total_ad_years * DashaEngine.DASHA_YEARS[pd_idx]) / DashaEngine.TOTAL_YEARS
            pd_actual_years = pd_total_years * (ad_duration / total_ad_years)
            
            pd_end_jd = current_jd + (pd_actual_years * year_length)
            
            sub_periods.append({
                "level": 3,
                "lord": DashaEngine.DASHA_LORDS[pd_idx],
                "start": DashaEngine._jd_to_iso(current_jd),
                "end": DashaEngine._jd_to_iso(pd_end_jd)
            })
            
            current_jd = pd_end_jd
            pd_idx = (pd_idx + 1) % 9
            
        return sub_periods

    @classmethod
    def calculate_multi_model_dasha_corridor(cls, birth_time_utc: datetime, moon_longitude: float, target_md: str, target_ad: str) -> Dict[str, Any]:
        """
        Synthesizes multiple classical Dasha chronometry models into a unified transition corridor:
        - Model 1: Solar Calendar Standard (365.2422 days / K.N. Rao)
        - Model 2: Savana Standard (360.0 days / Surya Siddhanta & JHora default)
        - Model 3: Julian Standard (365.25 days)
        Returns the exact boundaries per model and the unified consensus transition window.
        """
        tl_solar = cls.calculate_vimshottari_timeline(birth_time_utc, moon_longitude, num_levels=2, year_length=365.2422)
        tl_savana = cls.calculate_vimshottari_timeline(birth_time_utc, moon_longitude, num_levels=2, year_length=360.0)
        tl_julian = cls.calculate_vimshottari_timeline(birth_time_utc, moon_longitude, num_levels=2, year_length=365.25)

        def find_ad_range(timeline):
            for md in timeline:
                if md["lord"] == target_md:
                    for ad in md.get("sub_periods", []):
                        if ad["lord"] == target_ad:
                            return ad["start"], ad["end"]
            return None, None

        s_solar, e_solar = find_ad_range(tl_solar)
        s_savana, e_savana = find_ad_range(tl_savana)
        s_julian, e_julian = find_ad_range(tl_julian)

        starts = [s for s in [s_solar, s_savana, s_julian] if s]
        ends = [e for e in [e_solar, e_savana, e_julian] if e]

        corridor_start = min(starts)[:10] if starts else None
        corridor_start_latest = max(starts)[:10] if starts else None
        corridor_end = min(ends)[:10] if ends else None
        corridor_end_latest = max(ends)[:10] if ends else None

        return {
            "target_period": f"{target_md} -> {target_ad}",
            "models": {
                "kn_rao_solar_365d": {"start": s_solar, "end": e_solar},
                "jhora_savana_360d": {"start": s_savana, "end": e_savana},
                "julian_365_25d": {"start": s_julian, "end": e_julian}
            },
            "transition_start_corridor": f"{corridor_start} to {corridor_start_latest}",
            "transition_end_corridor": f"{corridor_end} to {corridor_end_latest}"
        }

    @staticmethod
    def get_current_dasha(timeline: List[Dict], target_date: datetime) -> Dict:
        """
        Traverses the timeline to find the current MD, AD, and PD.
        """
        result = {"mahadasha": None, "antardasha": None, "pratyantardasha": None}
        
        target_jd = DashaEngine._dt_to_jd(target_date)
        target_iso = DashaEngine._jd_to_iso(target_jd)
        
        for md in timeline:
            if md["start"] <= target_iso <= md["end"]:
                result["mahadasha"] = md["lord"]
                result["mahadasha_start"] = md["start"]
                result["mahadasha_end"] = md["end"]
                for ad in md.get("sub_periods", []):
                    if ad["start"] <= target_iso <= ad["end"]:
                        result["antardasha"] = ad["lord"]
                        for pd in ad.get("sub_periods", []):
                            if pd["start"] <= target_iso <= pd["end"]:
                                result["pratyantardasha"] = pd["lord"]
                                break
                        break
                break
                
        return result
