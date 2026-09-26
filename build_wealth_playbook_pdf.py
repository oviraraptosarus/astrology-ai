"""
Ketu Mahadasha Master Wealth & Peak Performance Blueprint (2024-2031)
PDF Generator Script
=====================================================================
Executive-grade PDF generation with dark navy/gold palette, custom NumberedCanvas,
and pure strategic execution content (zero astrological jargon).
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# --- COLOR DEFINITIONS ---
C_NAVY_DARK = colors.HexColor("#0B132B")      # Deep obsidian/navy for covers/headers
C_NAVY_MID = colors.HexColor("#1C2541")       # Slate navy for cards/subheaders
C_GOLD_DARK = colors.HexColor("#A8801C")      # Deep gold for borders/rules
C_GOLD_BRIGHT = colors.HexColor("#D4AF37")    # Bright metallic gold
C_GOLD_LIGHT = colors.HexColor("#FAF6E9")     # Cream gold for background callouts
C_BG_LIGHT = colors.HexColor("#F8F9FA")       # Clean off-white background
C_TEXT_DARK = colors.HexColor("#1A1D20")      # High-contrast body text
C_TEXT_MUTED = colors.HexColor("#4A4E69")     # Subtle slate for secondary text
C_WHITE = colors.white
C_ACCENT_RED = colors.HexColor("#8B0000")     # Deep crimson for warnings

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count + running headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip running headers on cover/title page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(C_GOLD_DARK)

        # Running Top Header
        self.drawString(54, 750, "PRIVATE WEALTH DIRECTIVE — KETU MAHADASHA (2024–2031)")
        self.setFont("Helvetica", 8)
        self.setFillColor(C_TEXT_MUTED)
        self.drawRightString(612 - 54, 750, "THE SOVEREIGN ALCHEMIST PLAYBOOK")

        # Top Accent Line
        self.setStrokeColor(C_GOLD_BRIGHT)
        self.setLineWidth(0.75)
        self.line(54, 742, 612 - 54, 742)

        # Running Bottom Footer
        self.setStrokeColor(colors.HexColor("#E0E0E0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)

        self.setFont("Helvetica", 8)
        self.setFillColor(C_TEXT_MUTED)
        self.drawString(54, 32, "CONFIDENTIAL — FOR PERSONAL USE ONLY")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_playbook_pdf(output_path="Ketu_Mahadasha_Master_Wealth_Playbook_2024_2031.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    style_cover_super = ParagraphStyle(
        "CoverSuper", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10, leading=14,
        textColor=C_GOLD_BRIGHT, textTransform="uppercase", spaceAfter=4
    )
    style_cover_title = ParagraphStyle(
        "CoverTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=23, leading=28,
        textColor=C_NAVY_DARK, spaceAfter=8
    )
    style_cover_sub = ParagraphStyle(
        "CoverSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=12, leading=16,
        textColor=C_TEXT_MUTED, spaceAfter=15
    )
    style_h1 = ParagraphStyle(
        "SectionH1", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=15, leading=19,
        textColor=C_NAVY_DARK, spaceBefore=14, spaceAfter=8, keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        "SectionH2", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=11, leading=15,
        textColor=C_GOLD_DARK, spaceBefore=10, spaceAfter=4, keepWithNext=True
    )
    style_body = ParagraphStyle(
        "BodyDark", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9.5, leading=14,
        textColor=C_TEXT_DARK, spaceAfter=6
    )
    style_body_bold = ParagraphStyle(
        "BodyDarkBold", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=9.5, leading=14,
        textColor=C_TEXT_DARK, spaceAfter=6
    )
    style_callout_title = ParagraphStyle(
        "CalloutTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10.5, leading=14,
        textColor=C_NAVY_DARK, spaceAfter=3
    )
    style_callout_body = ParagraphStyle(
        "CalloutBody", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9, leading=13,
        textColor=C_NAVY_MID
    )
    style_table_head = ParagraphStyle(
        "TableHead", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=8.5, leading=11,
        textColor=C_WHITE
    )
    style_table_cell = ParagraphStyle(
        "TableCell", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=11,
        textColor=C_TEXT_DARK
    )
    style_table_cell_bold = ParagraphStyle(
        "TableCellBold", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=8.5, leading=11,
        textColor=C_TEXT_DARK
    )

    story = []

    def make_callout(title, text, bg_color=C_GOLD_LIGHT, border_color=C_GOLD_DARK):
        p_title = Paragraph(title, style_callout_title)
        p_text = Paragraph(text, style_callout_body)
        tbl = Table([[p_title], [p_text]], colWidths=[504])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        return tbl

    def make_warning_box(title, text):
        return make_callout(
            f"<font color='#8B0000'>⚠️ {title}</font>",
            text,
            bg_color=colors.HexColor("#FDF2F2"),
            border_color=C_ACCENT_RED
        )

    # =========================================================================
    # COVER / HEADER
    # =========================================================================
    story.append(Paragraph("EXECUTIVE WEALTH ARCHITECTURE & TIMING DIRECTIVE", style_cover_super))
    story.append(Paragraph("THE 7-YEAR MASTER WEALTH & PEAK PERFORMANCE PLAYBOOK", style_cover_title))
    story.append(Paragraph("A Rigorous Operational Blueprint for Maximum Commercial Leverage & Biological Peak (2024–2031)", style_cover_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_GOLD_BRIGHT, spaceAfter=14))

    # Executive Summary Card
    exec_summary_text = (
        "<b>Core Operating Mandate:</b> You are in a high-velocity 7-year building epoch (2024–2031) specifically configured for "
        "<b>specialized enterprise client acquisition, backend equity capture, and cross-border capital extraction</b>. "
        "Linear employment or domestic local pricing will severely underperform your leverage architecture. "
        "This playbook translates your structural timing cycles into an unhedged operational strategy, detailing exact commercial models, "
        "seasonal unfair advantages, acute strike dates, and nervous system protocols to compound multi-crore enterprise value."
    )
    story.append(make_callout("EXECUTIVE SUMMARY: THE HIGH-LEVERAGE BLUEPRINT", exec_summary_text))
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 1: THE 3 STRUCTURAL UNFAIR ADVANTAGES
    # =========================================================================
    story.append(Paragraph("1. THE 3 STRUCTURAL UNFAIR ADVANTAGES", style_h1))
    story.append(Paragraph(
        "Your operating architecture possesses three distinct mathematical moats. "
        "Every dollar of revenue and every hour of effort must route through these three engines:",
        style_body
    ))

    advantage_data = [
        [
            Paragraph("Unfair Advantage", style_table_head),
            Paragraph("Operational Mechanism", style_table_head),
            Paragraph("Execution Mandate", style_table_head)
        ],
        [
            Paragraph("<b>1. Overseas Currency Arbitrage</b>", style_table_cell_bold),
            Paragraph("Your commercial communication channel is hard-locked to foreign territories and borderless systems.", style_table_cell),
            Paragraph("<b>100% US / EU / Global outreach.</b> Zero domestic/local enterprise selling. Charge premium Western USD retainers while maintaining lean operational costs.", style_table_cell)
        ],
        [
            Paragraph("<b>2. Other People's Capital (OPM) & Equity</b>", style_table_cell_bold),
            Paragraph("Your wealth engine is structurally wired to scale through backend performance and equity participation rather than flat hourly fees.", style_table_cell),
            Paragraph("<b>Structure contracts with hybrid compensation:</b> Base retainer ($3k–$5k/mo) + 10%–20% backend revenue share or performance equity bonuses.", style_table_cell)
        ],
        [
            Paragraph("<b>3. Sovereign Hyper-Niche Positioning</b>", style_table_cell_bold),
            Paragraph("Generalist agencies bleed margin. Your authority multiplies only when positioned as an elite, high-precision specialist.", style_table_cell),
            Paragraph("<b>One piercing offer.</b> Become the undeniable category-of-one in AI SDR / autonomous workflow infrastructure. Never compete on price.", style_table_cell)
        ]
    ]

    t_adv = Table(advantage_data, colWidths=[130, 160, 214])
    t_adv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_NAVY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D5DD")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_BG_LIGHT]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_adv)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 2: THE 7-SEASON CHRONOLOGICAL EXECUTION MATRIX
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("2. THE 7-SEASON CHRONOLOGICAL EXECUTION MATRIX (2024–2031)", style_h1))
    story.append(Paragraph(
        "Your 7-year build era is divided into 7 distinct tactical seasons. Each season carries a specific mandate, an operational pitfall to avoid, and key milestones:",
        style_body
    ))

    seasons = [
        {
            "num": "Season 1", "dates": "Now – November 14, 2026", "name": "The Authority & Infrastructure Sprint",
            "theme": "Laying the Cold Technical Foundation",
            "advantage": "Supreme executive willpower and sharp positioning. The gate is wide open for incorporation and initial client onboarding.",
            "pitfall": "Rushing out unpolished, generic marketing copy. Relying on warm domestic networks instead of automated cold pipelines.",
            "actions": "• Incorporate the agency/LLP structure.<br/>• Set up cold email infrastructure (domains, automated mailboxes, AI lead scrapers).<br/>• Close initial 2–3 beta enterprise retainers in US/EU markets."
        },
        {
            "num": "Season 2", "dates": "November 14, 2026 – June 15, 2027", "name": "The Pipeline Forge & Emotional Shield",
            "theme": "High-Rejection Volume & Cold Pipeline Engineering",
            "advantage": "High outreach volume and relationship entanglement capacity.",
            "pitfall": "Emotional reactivity. Rejection spikes and client volatility will feel intensely personal. Taking negotiation friction to heart will stall output.",
            "actions": "• Implement the <b>48-Hour Response Rule</b> for high-friction client messages.<br/>• Scale outbound volume to 1,000+ targeted foreign B2B prospects weekly.<br/>• Stack verifiable client case studies and refine backend delivery workflows."
        },
        {
            "num": "Season 3", "dates": "June 15, 2027 – November 12, 2027", "name": "The Multi-Crore Scale Window (Zero-Orb Peak)",
            "theme": "The Highest Leverage Commercial Surge of the Decade",
            "advantage": "<b>96.0 Critical High Convergence.</b> Exact sub-degree planetary return directly activating executive drive, 11th-house commercial gains, and foreign capital.",
            "pitfall": "Small thinking or playing defensive. Failing to raise prices or failing to demand backend performance equity.",
            "actions": "• <b>June 23–27, 2027 Strike:</b> Launch your flagship high-ticket enterprise offer.<br/>• Sign 5-figure monthly retainers + revenue-share equity deals.<br/>• Hire specialist operators to handle fulfillment while you focus entirely on high-stakes deal architecture."
        },
        {
            "num": "Season 4", "dates": "November 12, 2027 – November 29, 2028", "name": "The Empire Expansion & Radical Visibility Cycle",
            "theme": "Explosive Market Authority & Founder Visibility",
            "advantage": "Radical charisma, foreign market expansion, and breaking through previous enterprise ceilings.",
            "pitfall": "Scattering focus across 5 different business models (shiny object syndrome). Over-leveraging on debt or non-strategic expenditures.",
            "actions": "• Build a dominant thought-leadership brand in the AI automation space.<br/>• Expand from pure service delivery into proprietary micro-SaaS / workflow software.<br/>• Reinvest 70%+ of free cash flow directly into core capital reserves."
        },
        {
            "num": "Season 5", "dates": "November 29, 2028 – November 5, 2029", "name": "Foreign Consolidation & Backend Institutional Moats",
            "theme": "Locking In Enterprise Contracts & Overseas Expansion",
            "advantage": "Deep wisdom, strategic advisory authority, and institutional partnership alliances.",
            "pitfall": "Becoming complacent with existing cash flow and neglecting systemized fulfillment quality.",
            "actions": "• Form strategic partnerships with larger US/EU agencies for client syndication.<br/>• Establish overseas banking and tax-efficient corporate entities.<br/>• Transition from active founder selling to automated executive oversight."
        },
        {
            "num": "Season 6", "dates": "November 5, 2029 – December 15, 2030", "name": "Systematization, Legal Armor & Balance Sheet Fortress",
            "theme": "Structuring the Machine for 20-Year Durability",
            "advantage": "Iron discipline, flawless standard operating procedures (SOPs), and balance sheet durability.",
            "pitfall": "Disorganized bookkeeping, loose client contracts, or handshake agreements.",
            "actions": "• Conduct an exhaustive legal and financial audit of all client contracts and IP.<br/>• Lock in long-term recurring SaaS retainers.<br/>• Build an unassailable liquid capital fortress in preparation for the upcoming golden era."
        },
        {
            "num": "Season 7", "dates": "December 15, 2030 – December 12, 2031", "name": "The Fortune Bridge into the 20-Year Harvest Era",
            "theme": "Final Pruning & Launching the 20-Year Multiplier",
            "advantage": "Commercial fortune, high deal velocity, and seamless bridge into peak wealth (2031–2051).",
            "pitfall": "Failing to harvest what was built or holding on to unprofitable legacy services.",
            "actions": "• Package the business for maximum enterprise valuation or hands-off cash-cow dividends.<br/>• Transition directly into the 20-year Venus Era (Dec 2031 onwards) with multi-million dollar equity assets."
        }
    ]

    for s in seasons:
        season_table_data = [
            [
                Paragraph(f"<b>{s['num']}: {s['name']}</b>", style_table_head),
                Paragraph(f"<b>Timeframe: {s['dates']}</b>", ParagraphStyle("RHead", parent=style_table_head, alignment=2))
            ],
            [
                Paragraph("<b>Strategic Theme:</b>", style_table_cell_bold),
                Paragraph(s['theme'], style_table_cell)
            ],
            [
                Paragraph("<b>Unfair Advantage:</b>", style_table_cell_bold),
                Paragraph(s['advantage'], style_table_cell)
            ],
            [
                Paragraph("<b>Critical Pitfall:</b>", style_table_cell_bold),
                Paragraph(f"<font color='#8B0000'>{s['pitfall']}</font>", style_table_cell)
            ],
            [
                Paragraph("<b>Milestones:</b>", style_table_cell_bold),
                Paragraph(s['actions'], style_table_cell)
            ]
        ]
        t_season = Table(season_table_data, colWidths=[120, 384])
        t_season.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), C_NAVY_MID),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D5DD")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,1), (0,-1), C_BG_LIGHT),
        ]))
        story.append(KeepTogether([t_season, Spacer(1, 10)]))

    # =========================================================================
    # SECTION 3: THE PRECISION STRIKE CALENDAR
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. THE PRECISION STRIKE CALENDAR (ACUTE ACTION CORRIDORS)", style_h1))
    story.append(Paragraph(
        "The following dates represent high-probability energy corridors where commercial leverage, client closes, "
        "and strategic pivots yield exponential returns. Execute high-stakes actions inside these windows:",
        style_body
    ))

    strike_data = [
        [
            Paragraph("Window / Exact Peak", style_table_head),
            Paragraph("Convergence Score", style_table_head),
            Paragraph("Strategic Objective & Execution Mandate", style_table_head)
        ],
        [
            Paragraph("<b>Sep 8 – Sep 28, 2026</b>", style_table_cell_bold),
            Paragraph("<b>75.0 (High)</b>", style_table_cell),
            Paragraph("<b>Cold Infrastructure Launch:</b> Finish tech stack setup, scrapers, and outreach automation. Zero marketing fluff.", style_table_cell)
        ],
        [
            Paragraph("<b>Oct 24 – Nov 14, 2026</b>", style_table_cell_bold),
            Paragraph("<b>75.0 (High)</b>", style_table_cell),
            Paragraph("<b>Autumn Cash Harvest:</b> First wave of high-ticket retainer closes. Premium pricing enforcement ($3k–$5k/mo).", style_table_cell)
        ],
        [
            Paragraph("<b>Dec 2 – Dec 15, 2026</b>", style_table_cell_bold),
            Paragraph("<b>75.0 (High)</b>", style_table_cell),
            Paragraph("<b>Aggressive Outbound Burst:</b> Double outreach volume. Close contracts before corporate budget freezes.", style_table_cell)
        ],
        [
            Paragraph("<b>Jun 23 – Jul 15, 2027<br/><font color='#A8801C'>Peak: Jun 25, 2027</font></b>", style_table_cell_bold),
            Paragraph("<b><font color='#8B0000'>96.0 (Critical)</font></b>", style_table_cell),
            Paragraph("<b>THE DECADE SCALE STRIKE:</b> Launch flagship enterprise tier, sign multi-client backend equity deals, close 5-figure contracts.", style_table_cell)
        ],
        [
            Paragraph("<b>Jan 7 – Feb 27, 2028</b>", style_table_cell_bold),
            Paragraph("<b>75.0 (High)</b>", style_table_cell),
            Paragraph("<b>Software / SaaS Expansion:</b> Productize your agency services into recurring subscription software.", style_table_cell)
        ]
    ]

    t_strike = Table(strike_data, colWidths=[130, 94, 280])
    t_strike.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_NAVY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D5DD")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_BG_LIGHT]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_strike)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 4: PEAK BIOLOGICAL & MENTAL OPERATING SYSTEM
    # =========================================================================
    story.append(Paragraph("4. PEAK BIOLOGICAL & MENTAL OPERATING SYSTEM", style_h1))
    story.append(Paragraph(
        "Commercial leverage is useless if your biological hardware breaks down. "
        "Your constitutional profile is highly sensitive to nervous system depletion and mental loops. "
        "Execute these protocols daily as non-negotiable operational hygiene:",
        style_body
    ))

    # Protocol 1: Nervous System
    p1_text = (
        "<b>The Vata Nervous System Grounding Protocol:</b><br/>"
        "Your physiology naturally runs dry, cold, and fast. Mental stress manifests immediately as racing thoughts, "
        "erratic focus, and insomnia rather than physical fatigue. To keep your executive edge sharp:<br/>"
        "• <b>Sleep Window:</b> In bed by 10:30 PM. Complete digital shutdown 60 minutes prior (blue light severely dysregulates your focus).<br/>"
        "• <b>Dietary Grounding:</b> Warm, cooked, nutrient-dense meals. Healthy fats (ghee, olive oil, nuts) are mandatory to lubricate nerve function.<br/>"
        "• <b>Thermal Therapy:</b> Hot showers before sleep and regular warm oil body self-massage (Abhyanga) on weekends to instantly drop cortisol."
    )
    story.append(make_callout("PROTOCOL 1: NERVOUS SYSTEM STABILIZATION & BIO-LONGEVITY", p1_text))
    story.append(Spacer(1, 10))

    # Protocol 2: 48-Hour Rule
    p2_text = (
        "<b>The 48-Hour Emotional Response Shield:</b><br/>"
        "Your relationship and partnership center holds deep intensity and acute sensitivity. In business negotiations or personal communication, "
        "friction or rejection triggers an immediate desire to probe, over-explain, or demand instant resolution. "
        "<b>This reflex is your single greatest operational leak.</b><br/>"
        "• <b>The Iron Rule:</b> Whenever a client message, negotiation dispute, or personal communication spikes emotional friction, "
        "<b>mandate a strict 48-hour quarantine</b> before dispatching any response.<br/>"
        "• The initial draft is always written by reactivity; the 48-hour draft is written by sovereign strategy."
    )
    story.append(make_warning_box("PROTOCOL 2: THE 48-HOUR EMOTIONAL RESPONSE SHIELD", p2_text))
    story.append(Spacer(1, 10))

    # Protocol 3: Physical Training
    p3_text = (
        "<b>Physical Strength Architecture (Compensating for Native Energy Gaps):</b><br/>"
        "Your physical chart lacks natural raw muscular density by default—meaning physical stamina must be engineered with intent.<br/>"
        "• <b>Heavy Compound Resistance Training (3–4x/week):</b> Squats, deadlifts, presses, and pull-ups. "
        "Building lean muscle mass directly fuels executive assertiveness and physical presence on high-stakes video calls.<br/>"
        "• <b>Sprint Conditioning over Long-Distance Cardio:</b> Work in high-intensity output sprints followed by deep recovery, matching your native cognitive rhythms."
    )
    story.append(make_callout("PROTOCOL 3: PHYSICAL STRENGTH & EXECUTIVE PRESENCE", p3_text))
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 5: DAILY MOMENTUM & ENERGETIC MULTIPLIER STACK
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. DAILY MOMENTUM & ENERGETIC MULTIPLIER STACK", style_h1))
    story.append(Paragraph(
        "To ensure frictionless execution throughout the 7-year Ketu cycle, anchor your days with this streamlined behavioral stack:",
        style_body
    ))

    routine_data = [
        [
            Paragraph("Time / Pillar", style_table_head),
            Paragraph("Action Item", style_table_head),
            Paragraph("Strategic Objective", style_table_head)
        ],
        [
            Paragraph("<b>Morning Focus<br/>(06:30 – 07:30 AM)</b>", style_table_cell_bold),
            Paragraph("• Hydration + 10 min morning sunlight.<br/>• Deep Work Block 1: 90 min uninterrupted outbound architecture.", style_table_cell),
            Paragraph("Locks in high-status sovereign momentum before external reactive inputs arrive.", style_table_cell)
        ],
        [
            Paragraph("<b>Daily Upaya<br/>(Evening Focus)</b>", style_table_cell_bold),
            Paragraph("• 108 Repetitions: <i>'Om Sram Sreem Sroum Sah Ketave Namah'</i>.<br/>• 5 min silent breathwork/meditation.", style_table_cell),
            Paragraph("Directly pacifies the 7th-house nodal axis and unlocks supreme clarity in high-ticket client negotiations.", style_table_cell)
        ],
        [
            Paragraph("<b>Ancestral Alignment<br/>(Monthly Amavasya)</b>", style_table_cell_bold),
            Paragraph("• Gratitude offering to paternal lineage / father elders.<br/>• Voluntary anonymous charity.", style_table_cell),
            Paragraph("Directly activates the royal ancestral star (Magha) governing your long-term wealth multiplier.", style_table_cell)
        ],
        [
            Paragraph("<b>Weekly Service<br/>(Tuesdays / Saturdays)</b>", style_table_cell_bold),
            Paragraph("• Feed stray animals (dogs/birds).<br/>• Assist working-class laborers anonymously.", style_table_cell),
            Paragraph("Defuses crisis vectors and neutralizes sudden contractual friction in enterprise deals.", style_table_cell)
        ]
    ]

    t_routine = Table(routine_data, colWidths=[120, 204, 180])
    t_routine.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_NAVY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D5DD")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_BG_LIGHT]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_routine)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: THE 20-YEAR HARVEST HORIZON (2031–2051)
    # =========================================================================
    story.append(Paragraph("6. THE LONG-TERM HORIZON: THE 20-YEAR HARVEST ERA (2031–2051)", style_h1))
    horizon_text = (
        "<b>The Ultimate Destination:</b> Every line of code, every cold outreach campaign, and every equity contract you negotiate "
        "between 2024 and 2031 is the <b>forge</b>. On <b>December 11, 2031</b> (at age 23), you enter a monumental <b>20-year Venus Era (2031–2051)</b>.<br/><br/>"
        "In your architecture, the planet of luxury, prestige, and mega-scale wealth takes the wheel for two unbroken decades. "
        "However, that wealth is delivered through the exact vehicle you construct during this 7-year Ketu cycle. "
        "If you build an empire of automated foreign cash flow and equity stakes now, the 2031–2051 era multiplies it into generational wealth. "
        "<b>Stay disciplined, execute in sprints, honor the timing windows, and build the machine.</b>"
    )
    story.append(make_callout("THE 20-YEAR EXPONENTIAL MULTIPLIER", horizon_text, bg_color=C_GOLD_LIGHT, border_color=C_GOLD_BRIGHT))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    file_size = os.path.getsize(output_path)
    print(f"[SUCCESS] Playbook PDF generated: {os.path.abspath(output_path)}")
    print(f"File Size: {file_size / 1024:.2f} KB")
    return output_path


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Ketu_Mahadasha_Master_Wealth_Playbook_2024_2031.pdf"
    build_playbook_pdf(out_file)
