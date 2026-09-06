from typing import List, Dict, Any
from datetime import datetime, timedelta
import pytz

class DashaEngine:
    """
    Dedicated engine for calculating planetary periods (Dashas).
    Supports generating full timelines for Vimshottari Dasha.
    """
    
    DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    TOTAL_YEARS = 120.0
    
    @staticmethod
    def calculate_vimshottari_timeline(birth_time_utc: datetime, moon_longitude: float, num_levels: int = 3) -> List[Dict]:
        """
        Calculates the Vimshottari Dasha timeline from birth to 120 years.
        Supports up to 3 levels (Mahadasha, Antardasha, Pratyantardasha).
        """
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
        first_md_end = current_date + timedelta(days=first_md_years * 365.25)
        
        md_node = {
            "level": 1,
            "lord": DashaEngine.DASHA_LORDS[c_idx],
            "start": current_date.isoformat(),
            "end": first_md_end.isoformat(),
            "sub_periods": []
        }
        
        if num_levels >= 2:
            md_node["sub_periods"] = DashaEngine._calculate_antardashas(
                c_idx, current_date, first_md_years, num_levels, is_fractional=True, total_md_years=DashaEngine.DASHA_YEARS[c_idx]
            )
            
        timeline.append(md_node)
        current_date = first_md_end
        elapsed_years += first_md_years
        c_idx = (c_idx + 1) % 9
        
        # Calculate subsequent Mahadashas
        while elapsed_years < DashaEngine.TOTAL_YEARS:
            md_years = DashaEngine.DASHA_YEARS[c_idx]
            md_end = current_date + timedelta(days=md_years * 365.25)
            
            md_node = {
                "level": 1,
                "lord": DashaEngine.DASHA_LORDS[c_idx],
                "start": current_date.isoformat(),
                "end": md_end.isoformat(),
                "sub_periods": []
            }
            
            if num_levels >= 2:
                md_node["sub_periods"] = DashaEngine._calculate_antardashas(
                    c_idx, current_date, md_years, num_levels, is_fractional=False, total_md_years=md_years
                )
                
            timeline.append(md_node)
            current_date = md_end
            elapsed_years += md_years
            c_idx = (c_idx + 1) % 9
            
        return timeline

    @staticmethod
    def _calculate_antardashas(md_lord_idx: int, start_date: datetime, md_duration: float, num_levels: int, is_fractional: bool, total_md_years: float) -> List[Dict]:
        sub_periods = []
        current_date = start_date
        
        ad_idx = md_lord_idx
        
        # If this is the balance of birth Dasha, we need to find which Antardasha we are currently in.
        # This is complex because we skipped some time.
        # We calculate the total time elapsed in the Mahadasha BEFORE birth.
        time_elapsed_before_birth = total_md_years - md_duration
        accumulated_ad_time = 0.0
        
        for _ in range(9):
            ad_total_years = (total_md_years * DashaEngine.DASHA_YEARS[ad_idx]) / DashaEngine.TOTAL_YEARS
            
            if is_fractional:
                if accumulated_ad_time + ad_total_years <= time_elapsed_before_birth:
                    # This AD finished before birth
                    accumulated_ad_time += ad_total_years
                    ad_idx = (ad_idx + 1) % 9
                    continue
                else:
                    # We are born inside this AD
                    time_spent_in_this_ad_before_birth = time_elapsed_before_birth - accumulated_ad_time
                    ad_actual_years = ad_total_years - time_spent_in_this_ad_before_birth
                    # Reset is_fractional so subsequent ADs are full
                    is_fractional = False
            else:
                ad_actual_years = ad_total_years
                
            ad_end = current_date + timedelta(days=ad_actual_years * 365.25)
            
            ad_node = {
                "level": 2,
                "lord": DashaEngine.DASHA_LORDS[ad_idx],
                "start": current_date.isoformat(),
                "end": ad_end.isoformat(),
                "sub_periods": []
            }
            
            if num_levels >= 3:
                ad_node["sub_periods"] = DashaEngine._calculate_pratyantardashas(
                    ad_idx, current_date, ad_actual_years, total_md_years, ad_total_years
                )
                
            sub_periods.append(ad_node)
            current_date = ad_end
            accumulated_ad_time += ad_total_years
            ad_idx = (ad_idx + 1) % 9
            
        return sub_periods

    @staticmethod
    def _calculate_pratyantardashas(ad_lord_idx: int, start_date: datetime, ad_duration: float, total_md_years: float, total_ad_years: float) -> List[Dict]:
        sub_periods = []
        current_date = start_date
        pd_idx = ad_lord_idx
        
        # Simplified: We assume PRs inside a fractional AD are scaled down proportionally for now.
        # In exact calculation, we'd need to find the fractional PR too.
        # For our AI reasoning engine, knowing the AD and rough PD is sufficient.
        
        for _ in range(9):
            pd_total_years = (total_ad_years * DashaEngine.DASHA_YEARS[pd_idx]) / DashaEngine.TOTAL_YEARS
            # If AD is fractional, we just scale PD proportionally
            pd_actual_years = pd_total_years * (ad_duration / total_ad_years)
            
            pd_end = current_date + timedelta(days=pd_actual_years * 365.25)
            
            sub_periods.append({
                "level": 3,
                "lord": DashaEngine.DASHA_LORDS[pd_idx],
                "start": current_date.isoformat(),
                "end": pd_end.isoformat()
            })
            
            current_date = pd_end
            pd_idx = (pd_idx + 1) % 9
            
        return sub_periods

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
