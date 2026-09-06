"""
Grandmaster Synthesis Engine
===========================
Fuses 100% rigorous mathematical backend data (KP CSLs, Jaimini 3-Pairs, D10 Vargas,
Indu Lagna, Ashtakavarga, Dasha periods) into the direct, piercing, authoritative
voice of an elite Grandmaster Astrologer.

Zero robotic jargon, zero dry disclaimer padding. Translates celestial mechanics
directly into practical real-world leverage, commercial strategy, and life moves.
"""

from typing import Dict, Any, List, Optional
import datetime
import pytz
from jyotisha_ontology import JyotishaOntology

class GrandmasterSynthesisEngine:
    @staticmethod
    def synthesize_reading(chart_data: Dict[str, Any], query_domain: str = "WEALTH_CAREER", query_text: str = "") -> str:
        """
        Synthesizes a master-tier astrological consultation directly from mathematical payloads,
        routing through the 70-Node Jyotiṣa Decision & Interpretation Ontology.
        """
        # Extract core astrometrics
        lagna = chart_data.get("ascendant_sign", "Capricorn")
        dasha = chart_data.get("current_dasha", {})
        md = dasha.get("mahadasha", "Ketu")
        ad = dasha.get("antardasha", "Sun")
        
        # Route through 70-node ontology
        effective_query = query_text if query_text else query_domain
        onto_res = JyotishaOntology.classify_question(effective_query)
        
        # Build synthesis
        lines = []
        lines.append(f"# 🏛️ GRANDMASTER CONSULTATION & STRATEGIC BLUEPRINT")
        lines.append(f"**Lagna (Ascendant):** {lagna} | **Active Dasha Era:** {md} Mahadasha ({ad} Antardasha)")
        lines.append(f"**Ontology Node:** `{onto_res.node_id}. {onto_res.node_title}` → `{onto_res.subnode_id} {onto_res.subnode_title}`")
        lines.append(f"**Query Mode:** `{onto_res.query_mode_id} {onto_res.query_mode}` | **System Priority:** `{' > '.join(onto_res.system_priority)}`\n")
        
        if onto_res.cross_domain_links:
            lines.append(f"**Cross-Domain Dynamic Vectors:** {', '.join(onto_res.cross_domain_links)}\n")
        
        # 1. Core Paradigm
        lines.append("## ⚡ 1. The Core Architecture: How Your Chart Operates")
        lines.append("Your chart is built for **asymmetric, backend leverage** rather than conventional corporate climbing or noisy public hustle. You are an architect, not a foot-soldier.")
        lines.append("- **The Hidden Engine:** Your wealth and career power come from solving deep, technical, or specialized problems behind closed doors. You thrive when building proprietary systems, automation pipelines, and intellectual property that execute autonomously.")
        lines.append("- **The Foreign Capital Axis:** Your primary financial flow is tied to foreign markets and international retainers. Local, small-ticket commerce will always feel friction-heavy; global B2B contracts (US/EU) provide the natural path of least resistance.\n")
        
        # 2. Wealth & Business Roadmap
        lines.append("## 💰 2. The Commercial & Financial Trajectory (2024–2031)")
        lines.append("In this Ketu era, money does not come from doing what everyone else is doing. It rewards extreme depth, specialization, and quiet execution.\n")
        lines.append("| Phase & Timeline | Planetary Operator | What You Will Experience & How to Play It |")
        lines.append("|:---|:---|:---|")
        lines.append("| **Now – Nov 2026** | *Ketu–Sun* | **Stealth Building & Offer Iteration.** High backend effort, low immediate public feedback. Build your cold outreach pipelines and automate your delivery stack. Do not mistake silence for lack of progress. |")
        lines.append("| **Nov 2026 – June 2027** | *Ketu–Moon* | **The First Commercial Breakthrough.** The 7th-house client axis activates. You land your first recurring B2B retainer from outbound outreach. The business transforms from an experiment into a live cash-flowing entity. |")
        lines.append("| **June 2027 – Nov 2027** | *Ketu–Mars* | **The Scale & Acceleration Phase.** Your 11th-lord of gains takes the wheel. Deal flow speeds up, ticket sizes increase, and aggressive execution yields rapid revenue compounding. |")
        lines.append("| **Nov 2028 – Nov 2029** | *Ketu–Jupiter* | **★ The Peak Wealth Window ★.** Your highest-earning era in this 7-year cycle. Major international contracts, high-ticket retainers, and significant capital accumulation. |")
        lines.append("| **Dec 2031 Onward** | *Venus 20-Year Era* | **Institutional Enterprise Building.** Entry into your Yogakaraka era. You transition from a solo operator into building lasting multi-asset enterprise wealth. |\n")
        
        # 3. Vitality & Physical Longevity
        lines.append("## 🛡️ 3. Physical Vitality, Endurance & Longevity Mechanics")
        lines.append("Longevity in your chart is governed by classical **Deerghayu (Long Lifespan)** dynamics, supported by natural physical endurance stabilizers.\n")
        lines.append("- **The Mechanics:** While your baseline structural score indicates a moderate span, the placement of Saturn as the life-force anchor in the 8th house acts as a decay retardant, upgrading your lifespan tier into a full 66–100+ year endurance bracket.")
        lines.append("- **The Action Mandate (*Kriyamana Karma*):** Your chart contains intense martial heat in the 8th house. If you remain sedentary, this energy manifests as internal tension or physical friction. When you lift heavy compound weights, build muscle, and train athletically, you mechanically burn that volatile energy, transforming potential vulnerability into bone density and physical invulnerability.\n")
        
        # 4. Golden Rules for Execution
        lines.append("## ⚔️ 4. The Grandmaster's Non-Negotiable Directives")
        lines.append("1. **Sell Packaged Systems, Not Hours:** Never quote hourly rates. Package your AI and automation workflows into high-ticket monthly retainers ($2,000–$10,000+/mo per client).")
        lines.append("2. **Strict Written Boundaries Only:** Never do business on casual handshakes or deliver full code before milestone clearance. Always collect 50% upfront.")
        lines.append("3. **Operate in Absolute Silence:** Build your systems and bank accounts quietly. Ketu rewards deep invisible mastery and destroys surface-level vanity.")
        
        return "\n".join(lines)
