from vedic_models import Chart
from typing import List, Dict, Any
from dataclasses import dataclass, field
import datetime

@dataclass
class ActivationEvidence:
    type: str # 'DASHA' or 'TRANSIT'
    subject: str # e.g. 'Jupiter', 'Saturn'
    domain: str
    polarity: str # 'supporting', 'contradicting', 'modifier'
    reason: str
    
    def to_dict(self):
        return {
            "type": self.type,
            "subject": self.subject,
            "domain": self.domain,
            "polarity": self.polarity,
            "reason": self.reason
        }

@dataclass
class TimingWindow:
    start_date: str
    end_date: str
    confidence: str # e.g. "HIGH", "MEDIUM"
    trigger_dasha: str
    trigger_transit: str
    reason: str
    
    def to_dict(self):
        return {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "confidence": self.confidence,
            "trigger_dasha": self.trigger_dasha,
            "trigger_transit": self.trigger_transit,
            "reason": self.reason
        }

@dataclass
class ActivationProfile:
    domain: str
    dasha_evidence: List[ActivationEvidence]
    transit_evidence: List[ActivationEvidence]
    timing_status: str # FAVORABLE, UNFAVORABLE, MIXED, NEUTRAL
    timing_windows: List[TimingWindow] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "domain": self.domain,
            "dasha_evidence": [e.to_dict() for e in self.dasha_evidence],
            "transit_evidence": [e.to_dict() for e in self.transit_evidence],
            "timing_status": self.timing_status,
            "timing_windows": [w.to_dict() for w in self.timing_windows]
        }

class ActivationEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        
    def assess_activation(self, event_id: str, relevant_planets: List[str], relevant_houses: List[int]) -> ActivationProfile:
        dasha_evidence = self._eval_dasha(event_id, relevant_planets, relevant_houses)
        transit_evidence = self._eval_transits(event_id, relevant_planets, relevant_houses)
        
        # Synthesize timing status (Phase 17 Strict Layering)
        if not hasattr(self.chart, "current_dasha") or not self.chart.current_dasha:
            timing_status = "INSUFFICIENT TIMING EVIDENCE"
        else:
            sup_count = len([e for e in dasha_evidence + transit_evidence if e.polarity == "supporting"])
            con_count = len([e for e in dasha_evidence + transit_evidence if e.polarity == "contradicting"])
            
            if sup_count > 0 and con_count == 0:
                timing_status = "FAVORABLE"
            elif con_count > 0 and sup_count == 0:
                timing_status = "UNFAVORABLE"
            elif sup_count > 0 and con_count > 0:
                timing_status = "MIXED"
            else:
                timing_status = "NEUTRAL"
                
        # Calculate concrete timing windows scanning forward
        windows = self._calculate_timing_windows(event_id, relevant_planets, relevant_houses)
                
        return ActivationProfile(
            domain=event_id,
            dasha_evidence=dasha_evidence,
            transit_evidence=transit_evidence,
            timing_status=timing_status,
            timing_windows=windows
        )
        
    def _calculate_timing_windows(self, event_id: str, relevant_planets: List[str], relevant_houses: List[int]) -> List[TimingWindow]:
        """
        Scans forward in time across 24 months to find explicit date windows where 
        Dasha (Antardasha/Pratyantardasha), Double Transits, and Ashtakavarga overlap.
        """
        windows = []
        try:
            from forward_timing_scanner import ForwardTimingScanner
            scanner = ForwardTimingScanner(self.chart)
            now = datetime.datetime.now(datetime.timezone.utc)
            scanned_windows = scanner.scan_domain_windows(event_id, start_date=now, months_ahead=24)
            
            for sw in scanned_windows:
                reasons = []
                if sw.get("dasha_reasons"):
                    reasons.extend(sw["dasha_reasons"])
                if sw.get("transit_reasons"):
                    reasons.extend(sw["transit_reasons"])
                    
                windows.append(TimingWindow(
                    start_date=sw["start_date"],
                    end_date=sw["end_date"],
                    confidence=sw["confidence"],
                    trigger_dasha=sw["dasha_trigger"],
                    trigger_transit=", ".join(sw.get("transit_reasons", ["Transit alignment"])),
                    reason="; ".join(reasons)
                ))
        except Exception as e:
            # Safe fallback if ephemeris or chart is incomplete
            current_dasha = getattr(self.chart, "current_dasha", {})
            md_lord = current_dasha.get("mahadasha", "Unknown")
            ad_lord = current_dasha.get("antardasha", "Unknown")
            now = datetime.datetime.now()
            windows.append(TimingWindow(
                start_date=now.strftime("%Y-%m-%d"),
                end_date=(now + datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
                confidence="MODERATE",
                trigger_dasha=f"{md_lord}/{ad_lord}",
                trigger_transit="Transits of Jupiter/Saturn",
                reason=f"Active period of {md_lord}/{ad_lord} correlates with domain potential."
            ))
            
        return windows
        
    def _eval_dasha(self, domain: str, relevant_planets: List[str], relevant_houses: List[int]) -> List[ActivationEvidence]:
        evidence = []
        current_dasha = getattr(self.chart, "current_dasha", {})
        if not current_dasha:
            return []
            
        md_lord = current_dasha.get("Mahadasha") or current_dasha.get("mahadasha")
        ad_lord = current_dasha.get("Antardasha") or current_dasha.get("antardasha")
        pd_lord = current_dasha.get("Pratyantardasha") or current_dasha.get("pratyantardasha")
        
        for lord, level in [(md_lord, "Mahadasha"), (ad_lord, "Antardasha"), (pd_lord, "Pratyantardasha")]:
            if not lord: continue
            
            p = self.chart.planets.get(lord)
            if not p: continue
            
            if lord in relevant_planets:
                evidence.append(ActivationEvidence(
                    type="DASHA",
                    subject=lord,
                    domain=domain,
                    polarity="supporting",
                    reason=f"The current {level} lord ({lord}) is a primary significator for {domain}."
                ))
                
            owns_relevant = any(h in p.owns_houses for h in relevant_houses)
            if owns_relevant:
                evidence.append(ActivationEvidence(
                    type="DASHA",
                    subject=lord,
                    domain=domain,
                    polarity="supporting",
                    reason=f"The current {level} lord ({lord}) owns houses relevant to {domain}."
                ))
            
            # Dignity and House Placement of Dasha Lord
            if p.house in [6, 8, 12] and not owns_relevant:
                evidence.append(ActivationEvidence(
                    type="DASHA",
                    subject=lord,
                    domain=domain,
                    polarity="contradicting",
                    reason=f"The current {level} lord ({lord}) is in a Dusthana house ({p.house}), creating friction."
                ))
                
            if p.dignity in ["Exalted", "Own House", "Moolatrikona"]:
                evidence.append(ActivationEvidence(
                    type="DASHA",
                    subject=lord,
                    domain=domain,
                    polarity="supporting",
                    reason=f"The current {level} lord ({lord}) is highly dignified ({p.dignity}), strengthening its positive effects."
                ))
            elif p.dignity in ["Debilitated", "Enemy Sign", "Bitter Enemy Sign"]:
                evidence.append(ActivationEvidence(
                    type="DASHA",
                    subject=lord,
                    domain=domain,
                    polarity="contradicting",
                    reason=f"The current {level} lord ({lord}) is weak/afflicted ({p.dignity}), hindering its capacity."
                ))

        return evidence

    def _eval_transits(self, domain: str, relevant_planets: List[str], relevant_houses: List[int]) -> List[ActivationEvidence]:
        evidence = []
        transits = getattr(self.chart, "current_transits", {})
        if not transits:
            return []
            
        # Hook transits directly into Ashtakavarga and Houses
        from transit_engine import TransitEngine
        asc_idx = TransitEngine.ZODIAC_SIGNS.index(self.chart.ascendant_sign) if hasattr(self.chart, "ascendant_sign") and self.chart.ascendant_sign in TransitEngine.ZODIAC_SIGNS else 0
        
        for t_planet, t_data in transits.items():
            t_sign = t_data.get("current_sign") or t_data.get("sign")
            if not t_sign or t_sign not in TransitEngine.ZODIAC_SIGNS:
                continue
            
            t_sign_idx = TransitEngine.ZODIAC_SIGNS.index(t_sign)
            t_house = ((t_sign_idx - asc_idx) % 12) + 1
            
            bav = getattr(self.chart, "bhinna_ashtakavarga", {}).get(t_planet, {})
            bindus = bav.get(t_house, 4)
            
            if t_house in relevant_houses:
                if bindus >= 5:
                    evidence.append(ActivationEvidence(
                        type="TRANSIT",
                        subject=t_planet,
                        domain=domain,
                        polarity="supporting",
                        reason=f"Transiting {t_planet} is in house {t_house} ({t_sign}) with high BAV ({bindus} bindus), activating this domain."
                    ))
                elif bindus <= 3:
                    evidence.append(ActivationEvidence(
                        type="TRANSIT",
                        subject=t_planet,
                        domain=domain,
                        polarity="contradicting",
                        reason=f"Transiting {t_planet} is in house {t_house} ({t_sign}) with low BAV ({bindus} bindus), causing friction."
                    ))

        # Sade Sati Check
        moon = self.chart.planets.get("Moon")
        saturn_transit = transits.get("Saturn", {})
        
        if moon and saturn_transit:
            t_sign = saturn_transit.get("current_sign") or saturn_transit.get("sign")
            moon_sign = moon.sign
            if t_sign == moon_sign:
                evidence.append(ActivationEvidence(
                    type="TRANSIT",
                    subject="Saturn",
                    domain=domain,
                    polarity="contradicting",
                    reason=f"Saturn is transiting over the Natal Moon (Peak Sade Sati). This introduces pressure or delay."
                ))
                
        return evidence
