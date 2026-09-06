"""
Multi-Tradition Arbitration Engine
==================================
When Parashari / Jaimini / KP / Nadi / Tajaka / Pancha Pakshi disagree, this engine
does NOT discard the losing opinion. Instead it:

1. Collects an independent VERDICT from each tradition for the asked domain.
2. Detects genuine contradictions (strong-yes vs strong-no).
3. Resolves them through a domain-weighted priority ladder:
   - NATAL-PROMISE questions  : Parashari > Jaimini > KP > Nadi  (structure first)
   - TIMING/WHEN questions    : KP > Tajaka > Nadi > Parashari   (timing is KP's home turf)
   - DESTINY/KARMIC questions : Jaimini > Nadi > Parashari > KP
4. Produces a ranked confidence + an explicit "dissent register" so the LLM
   synthesis layer always sees WHAT disagreed, WHY, and which opinion was
   overruled on what grounds.

Design rule: the arbiter never silently drops an opinion. Overruled verdicts
remain visible in the output as dissenting evidence.
"""

from typing import Dict, List, Any, Optional

# Confidence scale mapped to numeric weight
CONF_WEIGHT = {
    "VERY_WEAK": -2, "WEAK": -1, "MIXED": 0, "INSUFFICIENT": 0,
    "MODERATE": 1, "STRONG": 2, "VERY_STRONG": 3,
    # KP-style statuses
    "PROMISED_FAVORABLE": 2, "STRONG_CAREER_PROMISE": 2,
    "WEALTH_ACCUMULATION_CONFIRMED": 2, "FRICTION_OR_DELAY": -1,
    "CHALLENGING_CAREER_PATH": -1, "WEALTH_ACCUMULATION_DENIED": -2,
}

# Domain -> tradition priority ladder (highest authority first).
# Rationale:
#   - Parashari is the base system for natal promise (houses/lords/vargas).
#   - Jaimini owns destiny/karakas/arudhas; strong for character & marriage.
#   - KP is razor-sharp for event timing & yes/no via cuspal sub-lords.
#   - Nadi reads karmic clusters; strongest for destiny pattern questions.
#   - Tajaka owns the annual (solar-return) year-level verdict.
PRIORITY_LADDERS = {
    "CAREER":      ["PARASHARI", "JAIMINI", "KP", "NADI"],
    "BUSINESS":    ["PARASHARI", "JAIMINI", "KP", "NADI"],
    "WEALTH":      ["PARASHARI", "KP", "JAIMINI", "NADI"],
    "MARRIAGE":    ["JAIMINI", "PARASHARI", "KP", "NADI"],
    "RELATIONSHIP": ["JAIMINI", "PARASHARI", "KP", "NADI"],
    "EDUCATION":   ["PARASHARI", "JAIMINI", "KP", "NADI"],
    "CHILDREN":    ["JAIMINI", "PARASHARI", "KP", "NADI"],
    "HEALTH":      ["PARASHARI", "NADI", "JAIMINI", "KP"],
    "PROPERTY":    ["PARASHARI", "KP", "JAIMINI", "NADI"],
    "SPIRITUALITY": ["JAIMINI", "NADI", "PARASHARI", "KP"],
    "TIMING":      ["KP", "TAJAKA", "NADI", "PARASHARI", "JAIMINI"],
}

# Questions where timing matters -> TAJAKA & KP get boosted
TIMING_KEYWORDS = ["when", "timing", "this year", "next year", "month",
                   "which year", "how long", "window", "soon", "date"]


class TraditionVerdict:
    """One tradition's independent opinion on the domain."""

    def __init__(self, tradition: str, verdict: str, confidence: str,
                 evidence: List[str], weight_multiplier: float = 1.0):
        self.tradition = tradition
        self.verdict = verdict          # FAVORABLE / UNFAVORABLE / NEUTRAL
        self.confidence = confidence    # scale from CONF_WEIGHT keys
        self.evidence = evidence
        self.weight_multiplier = weight_multiplier

    @property
    def signed_score(self) -> float:
        base = CONF_WEIGHT.get(self.confidence, 0)
        direction = 1 if self.verdict == "FAVORABLE" else (-1 if self.verdict == "UNFAVORABLE" else 0)
        return base * direction * self.weight_multiplier

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tradition": self.tradition,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "signed_score": round(self.signed_score, 3),
            "evidence": self.evidence,
        }


def _conf_from_status(status: str) -> str:
    """Map engine-specific status strings onto the shared confidence scale."""
    s = str(status).upper().replace(" ", "_")
    if s in CONF_WEIGHT:
        return s
    if "STRONG" in s and ("DENIED" not in s and "NOT" not in s):
        return "STRONG"
    if "WEAK" in s or "FRICTION" in s or "DELAY" in s or "CHALLENGING" in s:
        return "WEAK"
    if "CONFIRMED" in s or "PROMISED" in s or "VERY_STRONG" in s:
        return "STRONG"
    return "MODERATE"


def _direction_from_status(status: str) -> str:
    s = str(status).upper()
    if any(w in s for w in ["FRICTION", "DELAY", "DENIED", "CHALLENGING", "WEAK", "DOSHA", "AFFLICTION"]):
        return "UNFAVORABLE"
    if any(w in s for w in ["STRONG", "PROMISED", "CONFIRMED", "FAVORABLE", "SUPPORT"]):
        return "FAVORABLE"
    return "NEUTRAL"


class MultiTraditionArbiter:
    """Collects verdicts, detects contradictions, arbitrates via priority ladder."""

    def __init__(self, chart, question: str = "", target_date=None,
                 birth_dt_utc=None, lat: float = None, lon: float = None):
        self.chart = chart
        self.question = (question or "").lower()
        self.target_date = target_date
        self.birth_dt_utc = birth_dt_utc
        self.lat = lat
        self.lon = lon
        self.verdicts: List[TraditionVerdict] = []

    # ---------------- individual tradition collectors ----------------

    def collect_parashari(self, domain_analysis) -> None:
        conf = domain_analysis.confidence or "MODERATE"
        supp = len(domain_analysis.supporting_evidence or [])
        contra = len(domain_analysis.contradicting_evidence or [])
        if supp > contra:
            verdict = "FAVORABLE"
        elif contra > supp:
            verdict = "UNFAVORABLE"
        else:
            verdict = "NEUTRAL"
        evidence = [f"Supporting: {s}" for s in (domain_analysis.supporting_evidence or [])][:5] + \
                   [f"Contradicting: {c}" for c in (domain_analysis.contradicting_evidence or [])][:5]
        self.verdicts.append(TraditionVerdict(
            "PARASHARI", verdict, _conf_from_status(conf), evidence))

    def collect_jaimini(self) -> None:
        from jaimini_engine import JaiminiEngine
        res = JaiminiEngine.analyze_domain_jaimini(self.chart, self._domain_for_jaimini())
        conf = res.get("confidence", "MODERATE")
        supp = res.get("supporting_evidence", res.get("supporting", []))
        contra = res.get("contradicting_evidence", res.get("contradicting", []))
        verdict = "FAVORABLE" if len(supp) > len(contra) else ("UNFAVORABLE" if len(contra) > len(supp) else "NEUTRAL")
        self.verdicts.append(TraditionVerdict(
            "JAIMINI", verdict, _conf_from_status(conf), list(supp) + list(contra)))

    def _domain_for_jaimini(self) -> str:
        # Jaimini engine uses lowercase domain names
        return self.domain.lower() if hasattr(self, "domain") and self.domain else "career"

    def collect_kp(self, domain: str, birth_dt_local=None, lat=None, lon=None) -> None:
        """KP verdict from cuspal sub-lords. Requires birth data for cusp calc."""
        try:
            from kp_engine import KPEngine
            # birth params come from constructor or explicit args
            y = self._birth.get("year")
            if not y:
                self.verdicts.append(TraditionVerdict(
                    "KP", "NEUTRAL", "INSUFFICIENT", ["Birth data not provided for KP cusp calculation."]))
                return
            res = KPEngine.calculate_kp_chart(
                self._birth["year"], self._birth["month"], self._birth["day"],
                self._birth["hour"], self._birth["minute"],
                self.lat or self._birth.get("lat"), self.lon or self._birth.get("lon"),
                self._birth.get("tz", "Asia/Kolkata"))
            csl = res.get("csl_analysis", {})
            key_map = {
                "CAREER": "career_10th_csl", "BUSINESS": "career_10th_csl",
                "WEALTH": "wealth_2nd_csl", "MARRIAGE": "marriage_7th_csl",
                "RELATIONSHIP": "marriage_7th_csl",
            }
            key = key_map.get(domain.upper(), None)
            if not key or key not in csl:
                self.verdicts.append(TraditionVerdict(
                    "KP", "NEUTRAL", "INSUFFICIENT",
                    [f"KP CSL analysis not defined for domain {domain}."]))
                return
            entry = csl[key]
            status = entry.get("status", "MODERATE")
            houses = entry.get("signified_houses", [])
            ev = [f"CSL {entry.get('sub_lord')} signified houses {houses} -> {status}"]
            self.verdicts.append(TraditionVerdict(
                "KP", _direction_from_status(status), _conf_from_status(status), ev))
        except Exception as e:
            self.verdicts.append(TraditionVerdict(
                "KP", "NEUTRAL", "INSUFFICIENT", [f"KP collection error: {e}"]))

    def collect_nadi(self, domain: str) -> None:
        try:
            from nadi_engine import NadiEngine
            res = NadiEngine.evaluate_jeeva_and_karma(self.chart)
            # Interpret karma clusters for the domain
            evidence = []
            favorable = 0
            unfavorable = 0
            karma = res.get("karma_karaka", {}) if isinstance(res, dict) else {}
            jeeva = res.get("jeeva_karaka", {}) if isinstance(res, dict) else {}
            karma_name = karma.get("subject") or karma.get("planet") if isinstance(karma, dict) else None
            jeeva_name = jeeva.get("subject") or jeeva.get("planet") if isinstance(jeeva, dict) else None
            d = (domain or "").lower()
            if karma_name:
                links = NadiEngine.get_planet_bnn_links(self.chart, karma_name)
                combos = links.get("combinations", []) if isinstance(links, dict) else []
                dom_keywords = {
                    "career": ["engineering", "technical", "finance", "advisory", "authority", "organization"],
                    "business": ["finance", "trade", "assets", "business"],
                    "wealth": ["finance", "assets", "wealth", "real estate"],
                    "marriage": ["relationship", "arts", "beauty"],
                    "relationship": ["relationship", "arts", "beauty"],
                }
                kws = dom_keywords.get(d, [])
                for c in combos:
                    text = " ".join(str(v) for v in c.values()).lower() if isinstance(c, dict) else str(c).lower()
                    if any(k in text for k in kws):
                        favorable += 1
                        evidence.append(f"BNN Karma cluster aligns: {c}")
            if not evidence:
                # Fall back to structural reading: trine cluster around Karma Karaka
                tri = karma.get("trinal_conjunctions_1_5_9", []) if isinstance(karma, dict) else []
                if karma_name and len(tri) >= 2:
                    favorable = 1
                    evidence.append(
                        f"Karma Karaka {karma_name} holds a 1-5-9 trine cluster with {', '.join(tri)} "
                        f"— BNN directional strength for sustained work/career output.")
                else:
                    evidence = [f"Karma Karaka {karma_name or 'N/A'} present; no decisive trine cluster for this domain."]
            conf = "STRONG" if favorable >= 2 else ("MODERATE" if favorable == 1 else "INSUFFICIENT")
            verdict = "FAVORABLE" if favorable > 0 else "NEUTRAL"
            self.verdicts.append(TraditionVerdict("NADI", verdict, conf, evidence))
        except Exception as e:
            self.verdicts.append(TraditionVerdict(
                "NADI", "NEUTRAL", "INSUFFICIENT", [f"Nadi collection error: {e}"]))

    def collect_tajaka(self, domain: str) -> None:
        """Tajaka annual-chart verdict (only meaningful when target year known)."""
        try:
            if self.target_date is None or self.birth_dt_utc is None:
                self.verdicts.append(TraditionVerdict(
                    "TAJAKA", "NEUTRAL", "INSUFFICIENT",
                    ["No target date provided; Tajaka year-lord analysis skipped."]))
                return
            from tajaka_engine import TajakaEngine
            year = self.target_date.year
            sun = self.chart.planets.get("Sun")
            ZOD = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
                   "Sagittarius","Capricorn","Aquarius","Pisces"]
            sun_lon = ZOD.index(sun.sign) * 30 + sun.degree if sun else None
            if sun_lon is None:
                self.verdicts.append(TraditionVerdict(
                    "TAJAKA", "NEUTRAL", "INSUFFICIENT", ["Sun position unavailable."]))
                return
            res = TajakaEngine.calculate_varshaphala(
                self.chart, self.birth_dt_utc, year, self.lat or 16.0, self.lon or 82.0)
            yogas = res.get("tajaka_yogas", res.get("yogas", []))
            ith = [y for y in yogas if "ithasala" in str(y).lower()]
            eas = [y for y in yogas if "easarpha" in str(y).lower()]
            ev = ([f"Ithasala yoga: {y}" for y in ith[:3]] +
                  [f"Easarpha yoga: {y}" for y in eas[:3]])
            net = len(ith) - len(eas)
            conf = "STRONG" if abs(net) >= 2 else "MODERATE"
            verdict = "FAVORABLE" if net > 0 else ("UNFAVORABLE" if net < 0 else "NEUTRAL")
            self.verdicts.append(TraditionVerdict(
                "TAJAKA", verdict, conf,
                ev or [f"Neutral Tajaka year: {len(ith)} Ithasala vs {len(eas)} Easarpha."]))
        except Exception as e:
            self.verdicts.append(TraditionVerdict(
                "TAJAKA", "NEUTRAL", "INSUFFICIENT", [f"Tajaka collection error: {e}"]))

    # ---------------- arbitration ----------------

    def _get_ladder(self, domain: str) -> List[str]:
        d = (domain or "").upper()
        if d in PRIORITY_LADDERS:
            ladder = list(PRIORITY_LADDERS[d])
        else:
            ladder = list(PRIORITY_LADDERS["CAREER"])
        # Timing-flavored questions promote KP & TAJAKA
        if any(kw in self.question for kw in TIMING_KEYWORDS):
            for t in ["KP", "TAJAKA"]:
                if t in ladder:
                    ladder.remove(t)
                    ladder.insert(0, t)
                elif t == "TAJAKA":
                    ladder.insert(min(1, len(ladder)), t)
        return ladder

    def _weight_for(self, tradition: str, ladder: List[str]) -> float:
        """Authority weight: 1.5 for top authority, decays by rank."""
        if tradition in ladder:
            rank = ladder.index(tradition)
            return max(0.5, 1.5 - 0.25 * rank)
        return 0.5

    def arbitrate(self, domain: str) -> Dict[str, Any]:
        self.domain = domain
        ladder = self._get_ladder(domain)
        by_tradition = {v.tradition: v for v in self.verdicts}

        scored = []
        for t in ladder:
            v = by_tradition.get(t)
            if v is None:
                continue
            w = self._weight_for(t, ladder)
            scored.append({
                "tradition": t,
                "verdict": v.verdict,
                "confidence": v.confidence,
                "authority_weight": w,
                "weighted_score": round(v.signed_score * w, 3),
                "evidence": v.evidence,
            })
        # Traditions not in the ladder (e.g., PAKSHI) still get listed, lower weight
        for v in self.verdicts:
            if v.tradition not in ladder:
                scored.append({
                    "tradition": v.tradition,
                    "verdict": v.verdict,
                    "confidence": v.confidence,
                    "authority_weight": 0.5,
                    "weighted_score": round(v.signed_score * 0.5, 3),
                    "evidence": v.evidence,
                })

        total = sum(s["weighted_score"] for s in scored)
        favor = sum(1 for s in scored if s["verdict"] == "FAVORABLE")
        against = sum(1 for s in scored if s["verdict"] == "UNFAVORABLE")

        # Contradiction detection: strong opposite verdicts exist
        strong_yes = [s for s in scored if s["verdict"] == "FAVORABLE" and s["confidence"] in ("STRONG", "VERY_STRONG")]
        strong_no = [s for s in scored if s["verdict"] == "UNFAVORABLE" and s["confidence"] in ("STRONG", "VERY_STRONG")]
        has_contradiction = bool(strong_yes and strong_no)

        # Final call: weighted sum, but a top-authority STRONG dissent caps it
        if total > 1.0:
            final = "FAVORABLE"
        elif total < -1.0:
            final = "UNFAVORABLE"
        else:
            final = "MIXED"

        # If top authority strongly dissents from the weighted crowd, split verdict
        top = scored[0] if scored else None
        capped = False
        if top and top["confidence"] in ("STRONG", "VERY_STRONG"):
            if (final == "FAVORABLE" and top["verdict"] == "UNFAVORABLE") or \
               (final == "UNFAVORABLE" and top["verdict"] == "FAVORABLE"):
                final = f"MIXED ({top['tradition']} STRONG DISSENT)"
                capped = True

        dissent_register = [s for s in scored
                            if s["verdict"] != final.split(" ")[0]
                            and s["verdict"] != "NEUTRAL"]

        return {
            "domain": domain,
            "priority_ladder": ladder,
            "verdicts": scored,
            "weighted_total": round(total, 3),
            "votes_favorable": favor,
            "votes_unfavorable": against,
            "contradiction_detected": has_contradiction,
            "final_verdict": final,
            "top_authority_dissent": capped,
            "dissent_register": dissent_register,
            "explanation": self._explain(final, total, scored, ladder, has_contradiction, capped),
        }

    def _explain(self, final, total, scored, ladder, has_contradiction, capped) -> str:
        parts = [f"Arbitration ladder for this domain: {' > '.join(ladder)}."]
        parts.append(f"Weighted consensus score: {total:+.2f} -> {final}.")
        if has_contradiction:
            parts.append("Genuine contradiction detected: traditions hold strong opposing verdicts. "
                         "Dissenting opinions are PRESERVED in the dissent register, not discarded.")
        if capped:
            parts.append("The top-authority tradition issued a STRONG verdict against the crowd; "
                         "final call downgraded to MIXED to honor the dissent.")
        if not has_contradiction:
            parts.append("No strong contradictions; traditions broadly align.")
        return " ".join(parts)


def run_full_arbitration(chart, domain: str, question: str,
                         domain_analysis=None, target_date=None,
                         birth_dt_utc=None, birth_local=None,
                         lat=None, lon=None, tz_name="Asia/Kolkata") -> Dict[str, Any]:
    """Convenience wrapper: collects all tradition verdicts and arbitrates."""
    arb = MultiTraditionArbiter(chart, question=question, target_date=target_date,
                                birth_dt_utc=birth_dt_utc, lat=lat, lon=lon)
    if birth_local:
        arb._birth = birth_local
    else:
        arb._birth = {}

    if domain_analysis is not None:
        arb.collect_parashari(domain_analysis)
    arb.collect_jaimini()
    arb.collect_kp(domain)
    arb.collect_nadi(domain)
    arb.collect_tajaka(domain)
    return arb.arbitrate(domain)
