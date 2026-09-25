from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pytz
from config import Config

class DashaEngine:
    """
    Dedicated engine for calculating planetary periods (Dashas).
    Supports generating full timelines for Vimshottari Dasha with configurable
    year-length models (K.N. Rao 365.2422d Solar Calendar, 360d Savana/JHora, 365.25d Julian)
    and multi-model transition corridor consensus.
    """
    
    DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    TOTAL_YEARS = 120.0
    
    @staticmethod
    def calculate_vimshottari_timeline(birth_time_utc: datetime, moon_longitude: float, num_levels: int = 3, year_length: Optional[float] = None) -> List[Dict]:
        """
        Calculates the Vimshottari Dasha timeline from birth to 120 years.
        Supports up to 3 levels (Mahadasha, Antardasha, Pratyantardasha).
        year_length: Days per year (default from Config: 365.2422 for Solar/K.N. Rao, 360.0 for Savana/JHora).
        """
        if year_length is None:
            year_length = Config.get_year_length_days()

        nak_span = 360.0 / 27.0
        nak_idx = int(moon_longitude / nak_span)
        lord_idx = nak_idx % 9
        
        fraction_left = (nak_span - (moon_longitude % nak_span)) / nak_span
        balance_years = fraction_left * DashaEngine.DASHA_YEARS[lord_idx]
        
        timeline = []
        current_date = birth_time_utc
        
        # We simulate up to 120 years, starting from the current fractional lord
        c_idx = lord_idx
        elapsed_years = 0.0
        
        # Calculate the first (fractional) Mahadasha
        first_md_years = balance_years
        first_md_end = current_date + timedelta(days=first_md_years * year_length)
        
        md_node = {
            "level": 1,
            "lord": DashaEngine.DASHA_LORDS[c_idx],
            "start": current_date.isoformat(),
            "end": first_md_end.isoformat(),
            "sub_periods": []
        }
        
        if num_levels >= 2:
            md_node["sub_periods"] = DashaEngine._calculate_antardashas(
                c_idx, current_date, first_md_years, num_levels, is_fractional=True, total_md_years=DashaEngine.DASHA_YEARS[c_idx], year_length=year_length
            )
            
        timeline.append(md_node)
        current_date = first_md_end
        elapsed_years += first_md_years
        c_idx = (c_idx + 1) % 9
        
        # Calculate subsequent Mahadashas
        while elapsed_years < DashaEngine.TOTAL_YEARS:
            md_years = DashaEngine.DASHA_YEARS[c_idx]
            md_end = current_date + timedelta(days=md_years * year_length)
            
            md_node = {
                "level": 1,
                "lord": DashaEngine.DASHA_LORDS[c_idx],
                "start": current_date.isoformat(),
                "end": md_end.isoformat(),
                "sub_periods": []
            }
            
            if num_levels >= 2:
                md_node["sub_periods"] = DashaEngine._calculate_antardashas(
                    c_idx, current_date, md_years, num_levels, is_fractional=False, total_md_years=md_years, year_length=year_length
                )
                
            timeline.append(md_node)
            current_date = md_end
            elapsed_years += md_years
            c_idx = (c_idx + 1) % 9
            
        return timeline

    @staticmethod
    def _calculate_antardashas(md_lord_idx: int, start_date: datetime, md_duration: float, num_levels: int, is_fractional: bool, total_md_years: float, year_length: float = 365.2422) -> List[Dict]:
        sub_periods = []
        current_date = start_date
        
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
                
            ad_end = current_date + timedelta(days=ad_actual_years * year_length)
            
            ad_node = {
                "level": 2,
                "lord": DashaEngine.DASHA_LORDS[ad_idx],
                "start": current_date.isoformat(),
                "end": ad_end.isoformat(),
                "sub_periods": []
            }
            
            if num_levels >= 3:
                ad_node["sub_periods"] = DashaEngine._calculate_pratyantardashas(
                    ad_idx, current_date, ad_actual_years, total_md_years, ad_total_years, year_length=year_length
                )
                
            sub_periods.append(ad_node)
            current_date = ad_end
            accumulated_ad_time += ad_total_years
            ad_idx = (ad_idx + 1) % 9
            
        return sub_periods

    @staticmethod
    def _calculate_pratyantardashas(ad_lord_idx: int, start_date: datetime, ad_duration: float, total_md_years: float, total_ad_years: float, year_length: float = 365.2422) -> List[Dict]:
        sub_periods = []
        current_date = start_date
        pd_idx = ad_lord_idx
        
        for _ in range(9):
            pd_total_years = (total_ad_years * DashaEngine.DASHA_YEARS[pd_idx]) / DashaEngine.TOTAL_YEARS
            pd_actual_years = pd_total_years * (ad_duration / total_ad_years)
            
            pd_end = current_date + timedelta(days=pd_actual_years * year_length)
            
            sub_periods.append({
                "level": 3,
                "lord": DashaEngine.DASHA_LORDS[pd_idx],
                "start": current_date.isoformat(),
                "end": pd_end.isoformat()
            })
            
            current_date = pd_end
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

        # Consensus transition start corridor (earliest model to latest model)
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
        
        target_iso = target_date.isoformat()
        
        for md in timeline:
            if md["start"] <= target_iso <= md["end"]:
                result["mahadasha"] = md["lord"]
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
